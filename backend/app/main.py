from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.books import router as books_router
from app.routers.categories import router as categories_router
from app.routers.authors import router as authors_router
from app.routers.orders import router as orders_router
from app.auth.auth_router import router as auth_router

app = FastAPI(
    title="Bookworm API",
    description="API for Bookworm online bookstore",
    version="1.0.0"
)

# Set up CORS
origins = [
    "http://localhost",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
    "http://frontend",        # Docker container name
    "http://frontend:80",     # Docker container with port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books_router)
app.include_router(categories_router)
app.include_router(authors_router)
app.include_router(orders_router)
app.include_router(auth_router)

@app.get("/")
def root():
    return {"message": "Welcome to Bookworm API"}