from app.database import get_session
from app.models.author import Author

def create_author(author_name: str, author_bio: str = None):
    with get_session() as session:
        author = Author(author_name=author_name, author_bio=author_bio)
        session.add(author)
        session.commit()
        session.refresh(author)
        return author

# Ví dụ sử dụng:
if __name__ == "__main__":
    new_author = create_author("J.K. dsfdasfsdfRowldasding", "Author of sdasdfsdfdsasdHarry Potter")
    print(new_author.id, new_author.author_name)
