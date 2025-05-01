import bcrypt
from passlib.context import CryptContext

# Thử sử dụng CryptContext với xử lý lỗi
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    print(f"Error initializing CryptContext: {e}")
    # Fallback to direct bcrypt usage
    pwd_context = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """
    if pwd_context:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            print(f"Error using passlib verify: {e}")

    # Fallback to direct bcrypt usage
    try:
        # Ensure plain_password is encoded to bytes
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')

        # Ensure hashed_password is encoded to bytes
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')

        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception as e:
        print(f"Error using direct bcrypt: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password for storing
    """
    if pwd_context:
        try:
            return pwd_context.hash(password)
        except Exception as e:
            print(f"Error using passlib hash: {e}")

    # Fallback to direct bcrypt usage
    try:
        # Ensure password is encoded to bytes
        if isinstance(password, str):
            password = password.encode('utf-8')

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt)

        # Return as string
        if isinstance(hashed, bytes):
            return hashed.decode('utf-8')
        return hashed
    except Exception as e:
        print(f"Error using direct bcrypt: {e}")
        raise
