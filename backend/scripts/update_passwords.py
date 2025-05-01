import sys
import os

# Thêm thư mục gốc của dự án vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.database import engine
from app.models.user import User
from app.auth.password import get_password_hash

def update_passwords():
    """
    Cập nhật mật khẩu cho tất cả người dùng trong database
    """
    with Session(engine) as session:
        # Lấy tất cả người dùng
        statement = select(User)
        users = session.exec(statement).all()
        
        print(f"Found {len(users)} users")
        
        for user in users:
            # Giả sử mật khẩu ban đầu là 'password123'
            # Bạn có thể thay đổi thành mật khẩu khác hoặc sử dụng mật khẩu hiện tại
            plain_password = "password123"
            
            # Hash mật khẩu
            hashed_password = get_password_hash(plain_password)
            
            # Cập nhật mật khẩu
            user.password = hashed_password
            session.add(user)
            
            print(f"Updated password for user {user.email}")
        
        # Lưu thay đổi
        session.commit()
        print("All passwords updated successfully")

if __name__ == "__main__":
    update_passwords()
