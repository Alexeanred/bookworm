# FILE: dualagentsystem_with_feedback_v3_modified_layout.py
# Fixes asyncio event loop error in sync_crawl_product_info
# MODIFIED: UI Layout adjusted based on user request

import os
import glob
import pickle
import numpy as np
import gradio as gr
from typing import List, Dict, Any, Optional, Union, Tuple
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# Imports needed for feedback and saving
import json
import datetime

# Imports needed for advanced cleaning and web requests
import re
from bs4 import BeautifulSoup
import emoji
import aiohttp
import asyncio
import random

# Assuming these llamafactory imports are available (or fallback handled)
try:
    from llamafactory.chat.hf_engine import HuggingfaceEngine
    from llamafactory.chat.chat_model import get_infer_args
    from llamafactory.chat.hf_engine_adapter import LangChainHFAdapter
except ImportError:
    print("Warning: llamafactory imports failed. ProductSpecialistAgent might use fallback.")
    class HuggingfaceEngine: pass
    def get_infer_args(args): return {}, {}, {}, {}
    class LangChainHFAdapter: pass

import yaml

# --- Google API Key ---
# Replace with your key or key management


# --- Advanced Cleaning Regex Patterns ---
ascii_printable = r'\x20-\x7E'
whitespace = r'\n\t\r '
vietnamese_chars = (
    r'ÁÀẠẢÃÂẤẦẬẨẪĂẮẰẶẲẴÉÈẸẺẼÊẾỀỆỂỄÍÌỊỈĨÓÒỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÚÙỤỦŨƯỨỪỰỬỮÝỲỴỶỸĐ'
    r'áàạảãâấầậẩẫăắằặẳẵéèẹẻẽêếềệểễíìịỉĩóòọỏõôốồộổỗơớờợởỡúùụủũưứừựửữýỳỵỷỹđ'
)
vn_space_punct_before = f'{vietnamese_chars}{whitespace}.'
vn_space_upperlatin_after = f'{vietnamese_chars}{whitespace}A-Z'
allowed_chars_pattern_content = f'{ascii_printable}{whitespace}{vietnamese_chars}'
tiki_promo_text_pattern = re.compile(
    r"Giá sản phẩm trên Tiki đã bao gồm thuế theo luật hiện hành.*?\.\.+",
    re.DOTALL | re.IGNORECASE
)
vat_info_text = "Sản phẩm này là tài sản cá nhân được bán bởi Nhà Bán Hàng Cá Nhân và không thuộc đối tượng phải chịu thuế GTGT. Do đó hoá đơn VAT không được cung cấp trong trường hợp này."
hashtag_pattern = re.compile(r"#\S+")
separator_pattern = re.compile(r"[-=_\*]{3,}")
dimension_star_pattern = re.compile(r"(?<=\d)\*|\*(?=\d)")
selective_star_pattern = re.compile(
    f"(?<=[{vn_space_punct_before}])"
    r"\*\*?"
    f"(?=[{vn_space_upperlatin_after}])"
)
multiple_spaces_pattern = re.compile(r"[^\S\n\t\r]{2,}")
multiple_newlines_pattern = re.compile(r'\n{3,}')
unwanted_symbols_pattern = re.compile(f'[^{allowed_chars_pattern_content}]')

# --- Document Processor Class (No changes) ---
class DocumentProcessor:
    def __init__(self, docs_path: str, embedding_model: str = "models/text-embedding-004"):
        self.docs_path = docs_path
        self.embedding_model = embedding_model
        self.embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
        self.documents = []
        self.doc_embeddings = {}

    def load_documents(self) -> List[Document]:
        file_pattern = os.path.join(self.docs_path, "*doc.txt")
        files = glob.glob(file_pattern)
        documents = []
        for file_path in sorted(files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc_id = os.path.basename(file_path)
                    documents.append(Document(page_content=content, metadata={"source": doc_id}))
            except Exception as e:
                print(f"Error loading document {file_path}: {e}")
        self.documents = documents
        return documents

    def split_documents(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        split_docs = text_splitter.split_documents(self.documents)
        return split_docs

    def create_embeddings(self, split_docs: List[Document] = None):
        if split_docs is None and not self.documents:
            self.load_documents()
            split_docs = self.documents
        elif split_docs is None:
             split_docs = self.documents

        for doc in split_docs:
            try:
                embedding_vector = self.embeddings.embed_query(doc.page_content)
                self.doc_embeddings[doc.metadata["source"]] = {
                    "content": doc.page_content,
                    "embedding": embedding_vector
                }
            except Exception as e:
                print(f"Error creating embedding for {doc.metadata['source']}: {e}")
        return self.doc_embeddings

    def save_embeddings(self, save_path: str = "saved_embeddings"):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        with open(os.path.join(save_path, "document_embeddings.pkl"), "wb") as f:
            pickle.dump(self.doc_embeddings, f)
        return save_path

    def load_saved_embeddings(self, load_path: str = "saved_embeddings"):
        embeddings_path = os.path.join(load_path, "document_embeddings.pkl")
        if os.path.exists(embeddings_path):
            try:
                with open(embeddings_path, "rb") as f:
                    self.doc_embeddings = pickle.load(f)
                self.documents = [
                    Document(page_content=data["content"], metadata={"source": doc_id})
                    for doc_id, data in self.doc_embeddings.items()
                ]
                return self.doc_embeddings
            except Exception as e:
                print(f"Error loading embeddings pickle file: {e}")
                raise FileNotFoundError(f"Could not load embeddings from {embeddings_path}")
        else:
            raise FileNotFoundError(f"No saved embeddings found at {embeddings_path}")

    def create_vectorstore(self, docs=None):
        if docs is None:
            if not self.documents:
                self.load_documents()
            docs = self.documents
        if not docs:
            print("Warning: No documents provided to create vector store.")
            return None
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        return vectorstore

    def save_vectorstore(self, vectorstore, save_path: str = "saved_vectorstore"):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        vectorstore.save_local(save_path)
        return save_path

    def load_vectorstore(self, load_path: str = "saved_vectorstore"):
        return FAISS.load_local(load_path, self.embeddings, allow_dangerous_deserialization=True)


# --- Policy RAG Agent Class (No changes) ---
class PolicyRAGAgent:
    def __init__(self, vectorstore=None, vectorstore_path: Optional[str] = None):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )

        if vectorstore is None and vectorstore_path:
            try:
                embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
                if os.path.exists(vectorstore_path):
                    self.vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
                else:
                    raise FileNotFoundError(f"Vectorstore path not found: {vectorstore_path}")
            except Exception as e:
                print(f"Error loading vectorstore from {vectorstore_path}: {e}")
                raise ValueError(f"Failed to load vectorstore from {vectorstore_path}")
        elif vectorstore:
            self.vectorstore = vectorstore
        else:
            raise ValueError("Either vectorstore or vectorstore_path must be provided")

        self.qa_prompt = PromptTemplate.from_template("""
        Bạn là một chuyên gia về chính sách công ty, có nhiệm vụ trả lời các câu hỏi dựa trên các tài liệu chính sách được cung cấp. Hãy sử dụng các phần thông tin sau để trả lời câu hỏi liên quan đến chính sách của công ty. Nếu bạn không biết câu trả lời dựa trên thông tin được cung cấp, hãy nói rằng bạn không có thông tin chính sách đó.
        Ngữ cảnh: {context}
        Lịch sử trò chuyện: {chat_history}
        Câu hỏi: {question}
        Hãy trả lời câu hỏi dựa trên ngữ cảnh và lịch sử trò chuyện.
        """)
        self.setup_chain()

    def setup_chain(self):
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            memory=self.memory,
            return_source_documents=False,
            combine_docs_chain_kwargs={"prompt": self.qa_prompt},
            verbose=False
        )

    def ask(self, question: str) -> Dict[str, Any]:
        try:
            result = self.chain.invoke({"question": question})
            if isinstance(result, dict):
                return {
                    "answer": result.get("answer", "Lỗi: Không nhận được câu trả lời."),
                    "source_documents": result.get("source_documents", [])
                }
            else:
                print(f"Unexpected result type from chain: {type(result)}")
                return {"answer": "Lỗi: Định dạng phản hồi không mong đợi.", "source_documents": []}
        except Exception as e:
            print(f"Error in PolicyRAGAgent ask: {e}")
            return {"answer": f"Đã xảy ra lỗi khi xử lý yêu cầu chính sách: {e}", "source_documents": []}

    def get_conversation_history(self):
        return self.memory.chat_memory.messages

    def clear_history(self):
        self.memory.clear()
        return "Policy Agent history cleared."


# --- Product Specialist Agent Class (No core changes) ---
class ProductSpecialistAgent:
    def __init__(self):
        model_name_or_path = "meta-llama/Llama-3.2-3B-Instruct"
        adapter_name_or_path = "/content/drive/MyDrive/llama_3.2_3b_checkpoint/checkpoint-1000"
        self.llm = None
        self.llm_chain_adapter = None

        try:
            if 'HuggingfaceEngine' in globals() and 'get_infer_args' in globals() and 'LangChainHFAdapter' in globals():
                args = {
                    "model_name_or_path": model_name_or_path,
                }
                if adapter_name_or_path is not None:
                    args["adapter_name_or_path"] = adapter_name_or_path
                model_args, data_args, finetuning_args, generating_args = get_infer_args(args)
                self.llm = HuggingfaceEngine(model_args, data_args, finetuning_args, generating_args)
                self.llm_chain_adapter = LangChainHFAdapter(self.llm)
                print(f"Successfully initialized HuggingfaceEngine with {model_name_or_path}")
            else:
                raise ImportError("llamafactory components not fully available.")

        except Exception as e:
            print(f"Failed to initialize Llama via HuggingFace: {e}")
            print("Falling back to Gemini Pro for product agent...")
            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
            self.llm_chain_adapter = self.llm

        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.setup_chain()

    def setup_chain(self):
        if not self.llm_chain_adapter:
            print("Error: LLM adapter not initialized for ProductSpecialistAgent.")
            self.chain = RunnablePassthrough.assign(
                answer=lambda _: "Lỗi: Chuyên gia sản phẩm chưa được khởi tạo đúng cách."
            )
            return

        self.chain = self.llm_chain_adapter | StrOutputParser()

    def format_chat_history(self):
        """Format chat history for inclusion in prompt."""
        messages = self.memory.chat_memory.messages
        formatted_history = ""

        for i in range(0, len(messages), 2):  # Process pairs of messages
            if i < len(messages):
                user_msg = messages[i].content
                # Extract only the actual question from the structured user message
                if "### Câu hỏi:" in user_msg:
                    parts = user_msg.split("### Câu hỏi:")
                    if len(parts) > 1:
                        user_msg = parts[1].strip()
                formatted_history += f"Người dùng: {user_msg}\n"

                # Add AI response if available
                if i+1 < len(messages):
                    formatted_history += f"Trợ lý: {messages[i+1].content}\n\n"

        return formatted_history

    def ask(self, question: str, current_product_info: str) -> Dict[str, Any]:
        """
        Stores original user question in memory and uses chat history for context.
        """
        try:
            # Save the original question to memory
            self.memory.chat_memory.add_user_message(question)

            # Format chat history from previous turns
            chat_history = self.format_chat_history()

            # Create structured prompt with system instructions, product info, chat history and current question
            structured_input = (
                "Bạn là chatbot bán hàng chuyên nghiệp trên sàn thương mại điện tử Tiki. "
                "Nhiệm vụ của bạn là tư vấn khách hàng về sản phẩm này, trả lời câu hỏi một cách tự nhiên, "
                "thân thiện với nhiệm vụ duy nhất là chỉ hỗ trợ người dùng trả lời thông tin dựa trên thông tin sản phẩm được cung cấp, "
                "không hỗ trợ thanh toán, đặt, mua hàng. "
                "Đồng thời, không gợi ý, cung cấp thông tin sản phẩm khác. "
                "Tóm tắt phần **Mô tả** để trả lời thông tin, mô tả cho sản phẩm khi được người dùng hỏi. "
                "Những câu hỏi ngoài thông tin sản phẩm thì từ chối trả lời.\n"
                f"### Thông tin sản phẩm:\n{current_product_info}\n"
            )

            # Only add chat history if it's not empty
            if chat_history.strip():
                structured_input += f"### Lịch sử trò chuyện:\n{chat_history}\n"

            # Add current question
            structured_input += f"### Câu hỏi hiện tại:\n{question}"

            # Get answer from LLM
            answer = self.chain.invoke(structured_input)

            # Save the AI response to memory
            self.memory.chat_memory.add_ai_message(answer)

            return {"answer": answer}

        except Exception as e:
            print(f"Error in ProductSpecialistAgent ask: {e}")
            return {"answer": f"Đã xảy ra lỗi khi xử lý yêu cầu sản phẩm: {e}"}

    def get_conversation_history(self):
        return self.memory.chat_memory.messages

    def clear_history(self):
        self.memory.clear()
        return "Product Agent history cleared."


# --- Question Router Class (No core changes) ---
class QuestionRouter:
    def __init__(self, policy_agent: PolicyRAGAgent, product_agent: ProductSpecialistAgent):
        self.policy_agent = policy_agent
        self.product_agent = product_agent
        self.router_llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

        self.router_prompt = PromptTemplate.from_template("""
                Bạn là một hệ thống định tuyến câu hỏi. Nhiệm vụ của bạn là xác định trợ lý chuyên môn nào sẽ xử lý câu hỏi của người dùng:

                Chuyên gia chính sách – Dành cho các câu hỏi tổng quan về chính sách công ty, điều khoản dịch vụ, chính sách bảo mật, chính sách đổi trả, phương thức thanh toán, đơn hàng, tuân thủ quy định, các câu hỏi liên quan đến ứng dụng tiki và các vấn đề liên quan đến chính sách trừ thông tin bảo hành.
                {question}
                Chuyên gia sản phẩm – Dành cho bất kì câu hỏi nào liên quan đến thông tin sản phẩm, giá cả sản phẩm, kể cả bảo hành và các trường hợp không liên quan.

                Chỉ trả về MỘT trong hai chuỗi sau, CHÍNH XÁC như sau:
                "policy" (nếu câu hỏi dành cho chuyên gia chính sách)
                "product" (nếu câu hỏi dành cho chuyên gia sản phẩm)

                Phản hồi của bạn PHẢI chỉ là một trong hai từ trên, KHÔNG kèm theo bất kỳ văn bản nào khác.
                """)
        self.setup_router()

        self.rejection_prompt = PromptTemplate.from_template("""
                Tạo một phản hồi lịch sự từ chối trả lời câu hỏi sau vì nó không liên quan đến sản phẩm hoặc chính sách của tiki:
                Câu hỏi: {question}
                Phản hồi cần lịch sự, ngắn gọn và nên gợi ý người dùng đặt câu hỏi liên quan đến sản phẩm hoặc chính sách của công ty.
                """)
        self.rejection_chain = LLMChain(
            llm=self.router_llm,
            prompt=self.rejection_prompt,
            verbose=False
        )

    def setup_router(self):
        self.router_chain = (
            {"question": RunnablePassthrough()}
            | self.router_prompt
            | self.router_llm
            | StrOutputParser()
        )

    # Add product_info_text parameter
    def route_question(self, question: str, product_info_text: str) -> Tuple[str, Dict[str, Any]]:
        if not self.policy_agent or not self.product_agent:
            print("Error: One or both agents not initialized in QuestionRouter.")
            return "none", {"answer": "Lỗi hệ thống: Bộ định tuyến không được cấu hình đúng."}

        try:
            agent_type = self.router_chain.invoke(question).strip().lower()
            if agent_type not in ["product", "policy", "none"]:
                print(f"Warning: Router produced unexpected output: '{agent_type}'. Defaulting to 'none'.")
                agent_type = "none"

        except Exception as e:
            print(f"Error in router chain invocation: {e}")
            agent_type = "none"

        if agent_type == "product":
            # Pass product_info_text to the product agent's ask method
            return "product", self.product_agent.ask(question, product_info_text)
        elif agent_type == "policy":
             # Policy agent doesn't need the product info text
             return "policy", self.policy_agent.ask(question)
        else:
            try:
                rejection = self.rejection_chain.invoke({"question": question})
                rejection_text = rejection.get("text", "Xin lỗi, tôi không thể trả lời câu hỏi này vì nó không liên quan đến sản phẩm hoặc chính sách.")
                return "none", {"answer": rejection_text}
            except Exception as e:
                print(f"Error in rejection chain: {e}")
                return "none", {"answer": "Xin lỗi, đã có lỗi khi xử lý yêu cầu từ chối."}


# --- Dual Agent System Class (No core changes) ---
class DualAgentSystem:
    def __init__(
        self,
        policy_docs_path: str,
        vectorstore_path: str
    ):
        self.policy_agent = None
        self.product_agent = None
        self.router = None

        # --- Vector Store Initialization (No changes) ---
        faiss_index_file = os.path.join(vectorstore_path, "index.faiss")
        vectorstore = None
        if os.path.exists(vectorstore_path) and os.path.exists(faiss_index_file):
            try:
                print(f"Loading existing policy vector store from {vectorstore_path}...")
                embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
                vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
                print("Vector store loaded successfully.")
            except Exception as e:
                print(f"Error loading vector store from {vectorstore_path}: {e}. Will attempt to create a new one.")
                vectorstore = None
        else:
            print(f"Vector store not found at {vectorstore_path} or index file missing. Creating new policy vector store...")

        if vectorstore is None:
            if not os.path.exists(policy_docs_path):
                print(f"ERROR: Policy documents path not found: {policy_docs_path}. Cannot create vector store.")
            else:
                try:
                    print("Creating new vector store...")
                    docs_processor = DocumentProcessor(docs_path=policy_docs_path)
                    documents = docs_processor.load_documents()
                    print(f"Loaded {len(documents)} policy documents")
                    if documents:
                        split_docs = docs_processor.split_documents(chunk_size=1500, chunk_overlap=200)
                        print(f"Split into {len(split_docs)} chunks")
                        if split_docs:
                            print("Creating embeddings and vector store...")
                            os.makedirs(vectorstore_path, exist_ok=True)
                            vectorstore = docs_processor.create_vectorstore(split_docs)
                            if vectorstore:
                                docs_processor.save_vectorstore(vectorstore, save_path=vectorstore_path)
                                print(f"Saved new policy vector store to {vectorstore_path}")
                            else:
                                print("ERROR: Failed to create vector store instance.")
                        else:
                            print("Warning: No document chunks to process after splitting.")
                    else:
                        print("Warning: No documents found to create vector store.")
                except Exception as e:
                    print(f"ERROR: Failed to create new vector store: {e}")
                    vectorstore = None

        # --- Agent Initialization (No changes) ---
        if vectorstore:
            try:
                self.policy_agent = PolicyRAGAgent(vectorstore=vectorstore)
                print("Policy RAG agent initialized.")
            except Exception as e:
                print(f"ERROR: Failed to initialize PolicyRAGAgent: {e}")
                self.policy_agent = None
        else:
            print("ERROR: Policy vector store not available. Policy agent cannot be initialized.")
            self.policy_agent = None

        try:
            self.product_agent = ProductSpecialistAgent()
            print("Product Specialist agent initialized.")
        except Exception as e:
            print(f"ERROR: Failed to initialize ProductSpecialistAgent: {e}")
            self.product_agent = None

        # --- Router Initialization (No changes) ---
        if self.policy_agent and self.product_agent:
            try:
                self.router = QuestionRouter(self.policy_agent, self.product_agent)
                print("Question router initialized.")
            except Exception as e:
                print(f"ERROR: Failed to initialize QuestionRouter: {e}")
                self.router = None
        else:
            print("ERROR: Cannot initialize Question Router because one or both agents failed to initialize.")
            self.router = None

    # --- Ask method (No core changes) ---
    def ask(self, question: str, product_info_text: str) -> Dict[str, Any]:
        if self.router is None:
            return {
                "answer": "Xin lỗi, hệ thống chưa được khởi tạo đúng cách. Vui lòng kiểm tra cấu hình.",
                "agent": "System Error",
                "sources": []
            }

        agent_type, result = self.router.route_question(question, product_info_text)

        response = {
            "answer": "Xin lỗi, đã có lỗi xảy ra.",
            "agent": "Error",
            "sources": []
        }

        if isinstance(result, dict) and "answer" in result:
            response["answer"] = result["answer"]
            response["agent"] = agent_type # Store the determined agent type
            if agent_type == "policy":
                 sources = result.get("source_documents", [])
                 response["sources"] = [doc.metadata.get("source", "N/A") for doc in sources if hasattr(doc, 'metadata')]
            # No sources needed for product or none types
            else:
                 response["sources"] = []

        else:
            print(f"Warning: Unexpected result format from agent '{agent_type}': {result}")
            response["answer"] = f"Lỗi định dạng phản hồi từ {agent_type} agent."
            response["agent"] = "Error" # Mark as error if format is wrong

        return response # Returns dict including 'agent' key

    # --- Clear Agent Histories Method ---
    def clear_agent_histories(self):
        histories_cleared = []
        if self.policy_agent:
            self.policy_agent.clear_history()
            histories_cleared.append("Policy Agent")
        if self.product_agent:
            self.product_agent.clear_history()
            histories_cleared.append("Product Agent")
        if histories_cleared:
            return f"Agent histories cleared for: {', '.join(histories_cleared)}."
        else:
            return "No agent histories to clear (agents might not be initialized)."


# --- Global System Instance ---
dual_agent_system = None

# --- System Initialization (No changes) ---
def initialize_system(policy_docs_path, vectorstore_path):
    """Initialize the dual agent system if it doesn't exist."""
    global dual_agent_system
    if dual_agent_system is None:
        print("Initializing Dual Agent System...")
        vs_parent_dir = os.path.dirname(vectorstore_path)
        if vs_parent_dir and not os.path.exists(vs_parent_dir):
            os.makedirs(vs_parent_dir)
            print(f"Created directory for vectorstore: {vs_parent_dir}")

        dual_agent_system = DualAgentSystem(
            policy_docs_path=policy_docs_path,
            vectorstore_path=vectorstore_path
        )
        print("Dual Agent System initialization complete.")
    else:
        print("Dual Agent System already initialized.")
    return dual_agent_system

# --- Tiki Product Scraping & Formatting ---

def extract_product_id_from_input(input_str: str) -> str | None:
    input_str = input_str.strip()
    match = re.search(r'-p(\d+)\.html', input_str)
    if match:
        return match.group(1)
    elif input_str.isdigit():
        return input_str
    return None

cookies = {'TIKI_GUEST_TOKEN': '8jWSuIDBb2NGVzr6hsUZXpkP1FRin7lY'}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
}
params = {'platform': 'web'}

# --- Updated clean_description Function ---
def clean_description(html_description: str) -> str:
    if not html_description:
        return ""
    soup = BeautifulSoup(html_description, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)
    text = text.replace('\u00A0', ' ')
    text = tiki_promo_text_pattern.sub("", text)
    text = text.replace(vat_info_text, "")
    text = dimension_star_pattern.sub("x", text)
    text = emoji.replace_emoji(text, replace="")
    text = hashtag_pattern.sub("", text)
    text = separator_pattern.sub("", text)
    text = selective_star_pattern.sub("-", text)
    text = unwanted_symbols_pattern.sub("", text)
    text = multiple_spaces_pattern.sub(" ", text)
    text = multiple_newlines_pattern.sub("\n\n", text)
    cleaned_text = text.strip()
    return cleaned_text

# --- Updated parser_product Function ---
def parser_product(json_data):
    d = dict()
    d['id'] = json_data.get('id', '')
    d['name'] = json_data.get('name', '') # Keep the name
    raw_description = json_data.get('description', '')
    d['description'] = clean_description(raw_description) # Use advanced cleaning
    d['price'] = json_data.get('price', 0)
    d['list_price'] = json_data.get('list_price', 0)
    d['discount'] = json_data.get('discount', 0)
    d['discount_rate'] = json_data.get('discount_rate', 0)
    inventory_status = json_data.get('inventory_status', '')
    d['inventory_status'] = "còn hàng" if inventory_status == "available" else "hết hàng"
    brand = json_data.get('brand', {})
    d['brand_name'] = brand.get('name', '')
    warranty_info = json_data.get('warranty_info', []) or []
    specifications = json_data.get('specifications', []) or []
    d['warranty_status'] = 'không có thông tin'
    d['warranty_duration'] = ''
    d['warranty_type'] = ''
    d['warranty_location'] = ''
    for spec in specifications:
        if spec.get('name') == 'Operation':
            attributes = spec.get('attributes', []) or []
            for attr in attributes:
                code = attr.get('code', '')
                value = attr.get('value', '').lower()
                if code == 'is_warranty_applied':
                    d['warranty_status'] = 'có' if value in ['có', 'yes', 'true'] else 'không'
                elif code == 'warranty_time_period' and d['warranty_status'] == 'có':
                    d['warranty_duration'] = attr.get('value', '')
                elif code == 'warranty_form' and d['warranty_status'] == 'có':
                    d['warranty_type'] = attr.get('value', '')
    if d['warranty_status'] == 'không có thông tin' and warranty_info:
        has_warranty = False
        for info in warranty_info:
            name = info.get('name', '').lower()
            value = info.get('value', '')
            if 'bảo hành' in name or 'warranty' in name:
                has_warranty = True
                d['warranty_status'] = 'có'
                if 'thời gian bảo hành' in name or 'warranty period' in name:
                    d['warranty_duration'] = value
                elif 'hình thức bảo hành' in name or 'warranty type' in name:
                    d['warranty_type'] = value
                elif 'nơi bảo hành' in name or 'warranty location' in name:
                    d['warranty_location'] = value
        if not has_warranty:
            d['warranty_status'] = 'không'
    configurable_options = json_data.get('configurable_options', []) or []
    d['options'] = {}
    if configurable_options:
        for option in configurable_options:
            option_name = option.get('name', '')
            option_values = [val.get('label', '') for val in option.get('values', []) if val.get('label')]
            if  option_values:
                d['options'][option_name] = ', '.join(option_values)

    return d

# --- Updated format_product_info Function ---
def format_product_info(product_data):
    if not product_data or not isinstance(product_data, dict):
        return "Không thể lấy thông tin sản phẩm."

    inventory_status_display = product_data.get('inventory_status', 'không rõ')
    brand_name = product_data.get('brand_name', '').strip() or 'không có'
    output = (
        f"Tên sản phẩm: {product_data.get('name', 'Không có tên')}\n"
        f"Mô tả sản phẩm:\n{product_data.get('description', 'Không có mô tả')}\n\n"
        f"Giá: {product_data.get('price', 0):,}\n"
        f"Giá gốc: {product_data.get('list_price', 0):,}\n"
        f"Số tiền được giảm: {product_data.get('discount', 0):,}\n"
        f"Tỉ lệ được giảm: {product_data.get('discount_rate', 0)}%\n"
        f"Tình trạng tồn kho: {inventory_status_display}\n"
        f"Thương hiệu: {brand_name}\n"
        f"Bảo hành: {product_data.get('warranty_status', 'không rõ')}"
    )

    if product_data.get('warranty_status') == 'có':
        if product_data.get('warranty_duration'):
            output += f"\nThời gian bảo hành: {product_data['warranty_duration']}"
        if product_data.get('warranty_type'):
            output += f"\nHình thức bảo hành: {product_data['warranty_type']}"
        if product_data.get('warranty_location'):
            output += f"\nNơi bảo hành: {product_data['warranty_location']}"

    options_data = product_data.get('options', {})  # Default to empty dict
    if options_data:
        for option_name, option_value in options_data.items():
            output += f"\n{option_name}: {str(option_value)}"

    return output


# --- Updated fetch_product Function ---
async def fetch_product(session, pid, semaphore, max_retries=3) -> Optional[Dict]:
    url = f'https://tiki.vn/api/v2/products/{pid}'
    async with semaphore:
        retries = 0
        while retries < max_retries:
            try:
                await asyncio.sleep(random.uniform(0.5, 1.0))
                async with session.get(url, params=params, headers=headers, cookies=cookies, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, dict) and "id" in data:
                            parsed_data = parser_product(data)
                            return parsed_data
                        else:
                             print(f'Invalid JSON structure for {pid}.')
                             return None
                    elif response.status == 404:
                        print(f'Product {pid} not found (404).')
                        return None
                    else:
                           print(f'Failed fetch for {pid}. Status: {response.status}')
                           return None
            except asyncio.TimeoutError:
                print(f'Timeout fetching {pid} (retry {retries + 1})')
            except aiohttp.ClientError as e:
                print(f'Client error fetching {pid} (retry {retries + 1}): {e}')
            except json.JSONDecodeError as e:
                print(f'JSON decode error for {pid} on retry {retries + 1}: {e}')
                try:
                    error_text = await response.text()
                    print(f'Response text causing JSON error for {pid}: {error_text[:200]}')
                except: pass
            except Exception as e:
                print(f'Generic error fetching {pid} (retry {retries + 1}): {e}')

            retries += 1
            if retries < max_retries:
                wait_time = (2 ** retries) + random.uniform(0.1, 0.5)
                await asyncio.sleep(wait_time)
        print(f'Max retries reached for {pid}. Giving up.')
        return None

# --- *** MODIFIED ASYNC sync_crawl_product_info Function *** ---
async def sync_crawl_product_info(product_id_or_url) -> Tuple[str, str]:
    """
    Asynchronously crawls product info and returns (product_name, formatted_info).
    Handles errors by returning specific error messages.
    """
    product_id = extract_product_id_from_input(product_id_or_url)
    if not product_id:
        error_msg = "Đầu vào không hợp lệ. Vui lòng nhập Product ID hoặc URL Tiki hợp lệ."
        return "Lỗi Đầu Vào", error_msg

    # This inner function remains async
    async def crawl() -> Optional[Dict]:
        semaphore = asyncio.Semaphore(5)
        # Create session within the async function
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            product_data_dict = await fetch_product(session, product_id, semaphore)
            return product_data_dict

    try:
        # Directly await the async crawl function
        print(f"Attempting to crawl product ID: {product_id}")
        product_data = await crawl()
        print(f"Crawling result for {product_id}: {'Success' if product_data else 'Failure'}")

        if product_data and isinstance(product_data, dict):
            product_name = product_data.get('name', 'Không tìm thấy tên')
            formatted_info = format_product_info(product_data)
            return product_name, formatted_info
        elif product_data is None:
            error_msg = f"Không tìm thấy thông tin cho Product ID: {product_id}"
            return "Không tìm thấy", error_msg
        else:
            error_msg = f"Lỗi không xác định khi lấy thông tin cho Product ID: {product_id}"
            return "Lỗi", error_msg

    except asyncio.TimeoutError:
        print("Error: Crawling product info timed out.")
        error_msg = "Lỗi: Quá trình lấy thông tin sản phẩm mất quá nhiều thời gian."
        return "Lỗi Timeout", error_msg
    except Exception as e:
        # Catch other potential exceptions during await or processing
        print(f"Error during async crawl execution for {product_id}: {e}")
        error_msg = f"Đã xảy ra lỗi khi crawl dữ liệu: {e}"
        # Avoid returning the raw exception string directly to UI if it's sensitive
        return "Lỗi Thực Thi", "Đã xảy ra lỗi hệ thống khi lấy thông tin sản phẩm."


# --- Feedback and Saving Logic Functions (No changes) ---

def give_feedback(feedback_type, chat_state_with_feedback, feedback_provided_flag):
    """
    Applies feedback to the last turn in the chat_state_with_feedback.
    Format: [[user_msg, bot_response, feedback_status], ...]
    """
    status_message = ""
    updated_history = list(chat_state_with_feedback)

    if not updated_history:
        status_message = "Chưa có hội thoại để đưa ra phản hồi."
        return updated_history, feedback_provided_flag, status_message

    last_turn_index = len(updated_history) - 1

    if not isinstance(updated_history[last_turn_index], (list, tuple)) or len(updated_history[last_turn_index]) < 3:
        status_message = "Lỗi cấu trúc lịch sử nội bộ. Không thể áp dụng phản hồi."
        print(f"ERROR: Unexpected history item structure: {updated_history[last_turn_index]}")
        return updated_history, feedback_provided_flag, status_message

    if isinstance(updated_history[last_turn_index], tuple):
        updated_history[last_turn_index] = list(updated_history[last_turn_index])

    updated_history[last_turn_index][2] = feedback_type
    feedback_provided_flag = True
    status_message = f"Phản hồi '{feedback_type}' đã được ghi nhận cho câu trả lời cuối cùng."
    print(f"DEBUG: Feedback '{feedback_type}' recorded/updated. History item: {updated_history[last_turn_index]}")

    return updated_history, feedback_provided_flag, status_message


# --- MODIFIED save_conversation Function ---
# Transforms the internal log state into the desired training data format before saving.
def save_conversation(chat_state_with_feedback, feedback_provided_flag, product_context_text):
    """
    Saves the conversation in the specified training data JSON format
    if any feedback was provided during the session. Includes product context.
    """
    save_dir = "/content/chat_logs" # Save to Colab temporary storage
    # Ensure the directory exists
    os.makedirs(save_dir, exist_ok=True) # Added this line for robustness

    if not chat_state_with_feedback:
        return "Hội thoại trống. Không có gì để lưu."
    # Only save if at least one feedback was given overall during the session
    if feedback_provided_flag:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(save_dir, f"conversation_{timestamp}.json")

        try:
            # Transform the internal state [[user, bot, feedback], ...]
            # into the desired format
            formatted_conversations = []
            for turn in chat_state_with_feedback:
                # Unpack the turn, KEEP feedback status now
                user_msg, bot_response, feedback_status = turn # Changed from _ to feedback_status

                # Add human turn
                formatted_conversations.append({
                    "from": "human",
                    "value": user_msg
                })
                # Add gpt turn WITH feedback
                formatted_conversations.append({
                    "from": "gpt", # MODIFIED: Changed from "assistant"
                    "value": bot_response,
                    "feedback": feedback_status # ADDED: Feedback field
                })

            # Wrap the list in the final dictionary structure WITH product context
            final_data_to_save = {
                # ADDED: Product context field
                "product_context": product_context_text if product_context_text else "Không có thông tin sản phẩm được cung cấp.",
                "conversations": formatted_conversations
            }


            with open(filename, 'w', encoding='utf-8') as f:
                # Save the transformed data
                json.dump(final_data_to_save, f, indent=4, ensure_ascii=False) # Use indent=4 for readability
            print(f"Conversation saved to {filename} in training format.")
            return f"Hội thoại đã được lưu thành công vào {filename} theo định dạng huấn luyện."
        except Exception as e:
            print(f"Error saving conversation in training format: {e}")
            return f"Lỗi khi lưu hội thoại theo định dạng huấn luyện: {e}"
    else:
        # This part remains unchanged
        print("No feedback provided this session, conversation not saved.")
        return "Không có phản hồi nào được đưa ra trong phiên này. Hội thoại không được lưu."


# --- MODIFIED Gradio Interface Creation ---

def create_gradio_interface(policy_docs_path, vectorstore_path):
    """Create and launch the Gradio interface with feedback and product name display."""

    system = initialize_system(policy_docs_path, vectorstore_path)

    # --- MODIFIED handle_chat for First Turn Logging ---
    def handle_chat(message, chat_display_history, product_info_text, chat_log_state):
        """
        Processes user message, calls the dual agent system, updates display,
        and adds the turn to the feedback log state (modifying first turn user msg if needed).
        """
        if not message or message.strip() == "":
            chat_display_history.append((message, "Vui lòng nhập câu hỏi."))
            return "", chat_display_history, product_info_text, chat_log_state

        agent_type = "Error"
        formatted_response = "Lỗi không xác định."
        if system is None or system.router is None:
            response = {
                "answer": "Xin lỗi, hệ thống chưa được khởi tạo đúng cách.",
                "agent": "System Error", "sources": []
            }
            agent_type = response["agent"]
            formatted_response = f"**[{agent_type}]** {response['answer']}"
        else:
            response = system.ask(message, product_info_text)
            agent_type = response.get('agent', 'Error')

            agent_tag = f"**[{agent_type}]** " if agent_type not in ["None", "System Error", "Error", "product", "policy"] else "" # Adjusted tag based on typical router output
            # Map agent types for display if needed, e.g., "product" -> "Product Specialist"
            display_agent_type = agent_type
            if agent_type == "product": display_agent_type = "Chuyên gia sản phẩm"
            elif agent_type == "policy": display_agent_type = "Chuyên gia chính sách"
            elif agent_type == "none": display_agent_type = "Hệ thống" # Or some other neutral name

            agent_tag = f"**[{display_agent_type}]** " if agent_type not in ["System Error", "Error"] else ""
            formatted_response = f"{agent_tag}{response.get('answer', 'Lỗi không xác định.')}"


            sources = response.get("sources", [])
            # Adjust source display check based on actual agent type from router
            if sources and agent_type == "policy":
                sources_text = "\n\n**Nguồn:**\n" + "\n".join([f"- {source}" for source in sources])
                formatted_response += sources_text

        user_message_for_log = message
        is_first_turn = not bool(chat_log_state)
        # Check if it's the first turn, product info exists and is not placeholder, and product agent was used
        # Adjusted agent_type check to "product" (as returned by the router)
        if is_first_turn and product_info_text and product_info_text.strip() and not product_info_text.startswith("Không thể lấy thông tin") and agent_type == "product":
            user_message_for_log = f"{product_info_text.strip()}\n### Câu hỏi:\n{message}"
            print("DEBUG: Prepending product info to user message for first turn log.")

        # Store the raw bot response in the log, not the formatted one
        new_log_entry = [user_message_for_log, response.get('answer', 'Lỗi không xác định.'), "none"]
        updated_log_state = list(chat_log_state) + [new_log_entry]
        print(f"DEBUG: Added turn to log state. Length: {len(updated_log_state)}")

        chat_display_history.append((message, formatted_response)) # Display formatted response

        return "", chat_display_history, product_info_text, updated_log_state

    # --- MODIFIED handle_clear_and_save Function ---
    def handle_clear_and_save(current_feedback_state, current_feedback_flag, current_product_info):
        """
        Attempts to save the conversation (passing product info), clears agent histories,
        then returns values to clear the UI components including product name.
        """
        print("DEBUG: Clear button clicked. Checking if save is needed...")
        # Pass product info to save function
        save_status = save_conversation(current_feedback_state, current_feedback_flag,
                                        current_product_info)  # MODIFIED: Added current_product_info
        print(f"DEBUG: Auto-save attempt status: {save_status}")

        agent_clear_status = "Không thể xóa lịch sử tác nhân (hệ thống chưa khởi tạo)."
        if dual_agent_system:
            agent_clear_status = dual_agent_system.clear_agent_histories()
        print(f"Agent clear status: {agent_clear_status}")

        final_status = f"{save_status}\n{agent_clear_status}"

        # Clears: chatbot, query, product_id_input, product_info, log_state, flag_state, status_display, product_name_display
        return (
            [], "", "", "", [], False, final_status, ""
        )

    # --- Build Gradio UI using gr.Blocks ---
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Dual Agent System with Feedback v3 (Async Fix, Modified Layout)")
        gr.Markdown("""Hỏi về sản phẩm Tiki hoặc chính sách công ty. Hệ thống sẽ định tuyến câu hỏi đến chuyên gia phù hợp.
- **Product Specialist**: Trả lời câu hỏi về sản phẩm (tính năng, giá, sử dụng,...).
- **Policy Expert**: Trả lời câu hỏi về chính sách công ty (đổi trả, bảo mật,...).
Cung cấp phản hồi về câu trả lời bằng các nút 👍/👎. Lịch sử trò chuyện (bao gồm thông tin sản phẩm cho câu hỏi đầu tiên) sẽ được lưu vào Colab khi bạn nhấn nút 'Xóa và Lưu cuộc trò chuyện' **nếu** bạn đã cung cấp ít nhất một phản hồi.
""")

        # --- States ---
        chat_state_with_feedback = gr.State([])
        feedback_given_flag = gr.State(False)
        # product_info needs to be a visible component to be passed correctly
        # We will define it in the layout below

        # --- NEW LAYOUT START ---
        with gr.Row(): # Main row dividing the interface
            # --- Left Column (2/3 width) ---
            with gr.Column(scale=2):
                product_name_display = gr.Textbox(
                    label="Tên sản phẩm hiện tại",
                    placeholder="Thông tin sản phẩm sẽ xuất hiện ở đây...",
                    interactive=False
                )
                chatbot = gr.Chatbot(label="Chatbot", height=450, show_copy_button=True)

                gr.Markdown("Đánh giá câu trả lời cuối cùng của bot:")
                with gr.Row(): # Slim row for feedback buttons
                    good_button = gr.Button("👍 Tốt")
                    bad_button = gr.Button("👎 Chưa tốt")

                with gr.Row(): # Query input and Send button row
                    query = gr.Textbox(
                        placeholder="Nhập câu hỏi của bạn ở đây...",
                        show_label=False,
                        lines=1,
                        scale=18, # Give textbox more relative space
                        elem_id="chat-input"
                    )
                    send_btn = gr.Button(
                        value="➤", # Using an arrow symbol
                        scale=1, # Give button less relative space
                        min_width=50 # Ensure minimum width for the button
                    )

                # Clear button and status display below input
                clear_btn = gr.Button("Xóa và Lưu cuộc trò chuyện")
                feedback_status_display = gr.Textbox(label="Trạng thái Phản hồi/Lưu", interactive=False)

            # --- Right Column (1/3 width) ---
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("### Thông tin sản phẩm Tiki (Tùy chọn)")
                    product_id_input = gr.Textbox(placeholder="Nhập Product ID hoặc URL Tiki...",
                                                label="Product ID / URL")
                    crawl_btn = gr.Button("Lấy thông tin SP")
                    # Define product_info here as it's part of the right column
                    product_info = gr.Textbox(
                        placeholder="Chi tiết sản phẩm sẽ xuất hiện ở đây...\n(Thông tin này sẽ được tự động gửi kèm câu hỏi cho chuyên gia sản phẩm)",
                        lines=10, label="Chi tiết sản phẩm (Có thể chỉnh sửa)", interactive=True
                    )
                gr.Examples(
                    examples=[
                        "344517256",
                        "https://tiki.vn/dien-thoai-ban-kxts500-hang-chinh-hang-p163914808.html?spid=163914810",
                        "https://tiki.vn/may-pha-ca-phe-bear-sb-cf06a-hang-chinh-hang-p263967937.html?spid=270701841",
                        "275618846",
                        "https://tiki.vn/api/v2/products/75977724"
                    ],
                    # Input examples can target either product ID or the main query
                    # Adjust inputs based on which field makes more sense for examples
                    # Using product_id_input here for product examples
                    inputs=[product_id_input],
                    label="Ví dụ ID/URL sản phẩm hoặc câu hỏi"
                )
        # --- NEW LAYOUT END ---


        # --- Event Handlers (Functionality unchanged, ensure inputs/outputs match components) ---

        # Click handler for the send button
        send_btn.click(
            handle_chat,
            # Inputs: query, chatbot (display history), product_info (content), chat_state_with_feedback (log state)
            inputs=[query, chatbot, product_info, chat_state_with_feedback],
            # Outputs: query (clear), chatbot (update display), product_info (keep content), chat_state_with_feedback (update log)
            outputs=[query, chatbot, product_info, chat_state_with_feedback],
            queue=True
        )

        # Query submit handler (handles Enter key)
        query.submit(
            handle_chat,
            inputs=[query, chatbot, product_info, chat_state_with_feedback],
            outputs=[query, chatbot, product_info, chat_state_with_feedback],
            queue=True
        )

        # Clear button handler - CRITICAL CHECK: Inputs must match function definition
        # Function: handle_clear_and_save(current_feedback_state, current_feedback_flag, current_product_info)
        # Inputs: chat_state_with_feedback, feedback_given_flag, product_info
        clear_btn.click(
            handle_clear_and_save,
            inputs=[chat_state_with_feedback, feedback_given_flag, product_info], # Keep this exactly as it was!
            # Outputs: chatbot, query, product_id_input, product_info, chat_state_with_feedback, feedback_given_flag, feedback_status_display, product_name_display
            outputs=[chatbot, query, product_id_input, product_info, chat_state_with_feedback, feedback_given_flag,
                     feedback_status_display, product_name_display],
            queue=False # Typically False for clear actions
        )

        # Crawl button handler
        crawl_btn.click(
            sync_crawl_product_info,
            inputs=[product_id_input],
            outputs=[product_name_display, product_info], # Output to product name display and product info textbox
            queue=True
        )

        # Feedback button handlers
        good_button.click(
            give_feedback,
            inputs=[gr.Number(value="good", visible=False), chat_state_with_feedback, feedback_given_flag],
            outputs=[chat_state_with_feedback, feedback_given_flag, feedback_status_display],
            queue=False
        )
        bad_button.click(
            give_feedback,
            inputs=[gr.Number(value="bad", visible=False), chat_state_with_feedback, feedback_given_flag],
            outputs=[chat_state_with_feedback, feedback_given_flag, feedback_status_display],
            queue=False
        )

    demo.launch(share=True, debug=True) # Keep share=True and debug=True if needed

# --- Main Execution (No changes) ---
if __name__ == "__main__":
    # Determine the script directory robustly
    current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() and os.path.exists(__file__) else '.'
    policy_docs_path = os.path.join(current_dir, "policy_documents")
    vectorstore_path = os.path.join(current_dir, "policy_vector_store")

    # Ensure policy documents directory exists and create a dummy file if empty
    if not os.path.exists(policy_docs_path):
        os.makedirs(policy_docs_path)
        print(f"Created policy documents directory: {policy_docs_path}")
        dummy_policy_file = os.path.join(policy_docs_path, "dummy_policy_doc.txt")
        if not os.path.exists(dummy_policy_file):
            try:
                with open(dummy_policy_file, "w", encoding='utf-8') as f:
                    f.write("Đây là chính sách mẫu về việc đổi trả hàng trong vòng 7 ngày kể từ ngày nhận hàng.")
                print(f"Created dummy policy file: {dummy_policy_file}")
            except Exception as e:
                print(f"Warning: Could not create dummy policy file: {e}")
    else:
         print(f"Policy documents directory found: {policy_docs_path}")


    print("Starting Gradio Interface Setup...")
    create_gradio_interface(policy_docs_path, vectorstore_path)
    print("Gradio Interface Launched.")
