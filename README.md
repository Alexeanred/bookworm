# Bookworm Online Bookstore

A full-stack web application for an online bookstore with features like browsing books, filtering by categories and authors, cart management, and order processing.

## Project Structure

- **Frontend**: React application with TypeScript and Tailwind CSS
- **Backend**: FastAPI application with SQLModel for database operations
- **Database**: PostgreSQL for data storage

## Docker Setup

This project is containerized using Docker and Docker Compose for easy setup and deployment.

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd bookworm
   ```

2. Đảm bảo file dump SQL `bookworm_localhost-2025_04_24_18_57_48-dump.sql` đã được đặt trong thư mục gốc của dự án.

3. Khởi động các container:
   ```bash
   docker-compose up -d
   ```

4. Import dữ liệu vào cơ sở dữ liệu (sau khi container đã khởi động):
   ```bash
   chmod +x import-data.sh
   ./import-data.sh
   ```

3. Access the application:
   - Frontend: http://localhost
   - Backend API: http://localhost/api
   - API Documentation: http://localhost/api/docs

### Development Mode

For development, you can use the following commands:

1. Start the database only:
   ```bash
   docker-compose up -d db
   ```

2. Run the backend locally:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

3. Run the frontend locally:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Environment Variables

### Backend

- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT token generation
- `JWT_ALGORITHM`: Algorithm used for JWT (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time in minutes
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration time in days

### Frontend

- `VITE_API_BASE_URL`: URL of the backend API

## Features

- Browse books with filtering by category, author, and rating
- Sort books by price, discount, and popularity
- View book details
- Add books to cart
- Place orders
- User authentication
- Responsive design for mobile and desktop


