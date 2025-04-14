-- Tạo bảng category
CREATE TABLE category (
    id BIGSERIAL PRIMARY KEY,
    category_name VARCHAR(120) NOT NULL,
    category_desc VARCHAR(255)
);

-- Tạo bảng author
CREATE TABLE author (
    id BIGSERIAL PRIMARY KEY,
    author_name VARCHAR(255) NOT NULL,
    author_bio TEXT
);

-- Tạo bảng user
CREATE TABLE "user" (
    id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(70) NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Tạo bảng book
CREATE TABLE book (
    id BIGSERIAL PRIMARY KEY,
    category_id BIGINT,
    author_id BIGINT,
    book_title VARCHAR(255) NOT NULL,
    book_summary TEXT,
    book_price NUMERIC(5,2) NOT NULL,
    book_cover_photo VARCHAR(20)
);

-- Tạo bảng discount
CREATE TABLE discount (
    id BIGSERIAL PRIMARY KEY,
    book_id BIGINT,
    discount_price NUMERIC(5,2) NOT NULL,
    discount_start_date DATE NOT NULL,
    discount_end_date DATE NOT NULL
);

-- Tạo bảng review
CREATE TABLE review (
    id BIGSERIAL PRIMARY KEY,
    book_id BIGINT, 
	review_title varchar(120),
    review_details TEXT,
	review_date timestamp(0),
    rating_start varchar(255) NOT NULL
);

-- Tạo bảng order
CREATE TABLE order_item (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT,
	book_id BIGINT,
    quantity SMALLINT,
    price NUMERIC(5,2) NOT NULL
);

-- Tạo bảng order_item
CREATE TABLE "order" (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
   	order_date TIMESTAMP(0),  
    order_amount NUMERIC(8,2)
);

ALTER TABLE book
    ADD CONSTRAINT fk_book_category FOREIGN KEY (category_id) REFERENCES category(id),
    ADD CONSTRAINT fk_book_author FOREIGN KEY (author_id) REFERENCES author(id);
	
ALTER TABLE discount
    ADD CONSTRAINT fk_discount_book FOREIGN KEY (book_id) REFERENCES book(id);

ALTER TABLE review
    ADD CONSTRAINT fk_review_book FOREIGN KEY (book_id) REFERENCES book(id);

ALTER TABLE "order"
    ADD CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES "user"(id);

-- Thêm khóa ngoại cho bảng order_item
ALTER TABLE order_item
    ADD CONSTRAINT fk_order_item_order FOREIGN KEY (order_id) REFERENCES "order"(id),
    ADD CONSTRAINT fk_order_item_book FOREIGN KEY (book_id) REFERENCES book(id);

ALTER TABLE "user"
    ADD CONSTRAINT unique_user_email UNIQUE (email);

ALTER TABLE review
    ADD CONSTRAINT check_rating_range CHECK (rating_start IN ('1', '2', '3', '4', '5'));

INSERT INTO category (category_name, category_desc) VALUES
('Fiction', 'Fictional stories and novels'),
('Non-Fiction', 'Books based on real events and facts'),
('Science Fiction', 'Books about futuristic science and technology');

INSERT INTO author (author_name, author_bio) VALUES
('John Doe', 'A renowned novelist with a passion for adventure stories'),
('Jane Smith', 'An expert in self-help and mindfulness literature'),
('Alan Turing', 'A science fiction enthusiast and computer scientist');

INSERT INTO "user" (first_name, last_name, email, password, is_admin) VALUES
('Alice', 'Johnson', 'alice.johnson@email.com', 'alice123', FALSE),
('Bob', 'Smith', 'bob.smith@email.com', 'bob456', FALSE),
('Admin', 'User', 'admin@email.com', 'admin789', TRUE);

INSERT INTO book (category_id, author_id, book_title, book_summary, book_price, book_cover_photo) VALUES
(1, 1, 'The Lost World', 'A thrilling adventure in a prehistoric jungle', 20.00, 'lostworld.jpg'),
(1, 1, 'The Hidden Realm', 'A fantasy tale of hidden kingdoms', 18.50, 'hiddenrealm.jpg'),
(2, 2, 'Mindful Living', 'A guide to living a peaceful life', 15.00, 'mindful.jpg'),
(3, 3, 'Future Worlds', 'A sci-fi epic about interstellar travel', 22.00, 'futureworlds.jpg'),
(3, 3, 'AI Revolution', 'A speculative look at artificial intelligence', 19.99, 'airevolution.jpg');

INSERT INTO discount (book_id, discount_price, discount_start_date, discount_end_date) VALUES
(1, 18.00, '2025-04-01', '2025-04-30'), -- Giảm 10% cho The Lost World
(3, 12.75, '2025-05-01', '2025-05-15'), -- Giảm 15% cho Mindful Living
(4, 17.60, '2025-06-01', '2025-06-10'); -- Giảm 20% cho Future Worlds

INSERT INTO review (book_id, review_title, review_details, review_date, rating_start) VALUES
(1, 'Amazing Adventure', 'Couldn''t put it down! A fantastic read.', '2025-04-10 10:00:00', '5'),
(1, 'Great Story', 'Loved the characters and plot twists.', '2025-04-12 14:30:00', '4'),
(3, 'Very Insightful', 'Helped me find peace in my daily life.', '2025-04-15 09:15:00', '5'),
(4, 'Futuristic Fun', 'A great sci-fi journey!', '2025-04-20 16:45:00', '4');

INSERT INTO "order" (user_id, order_date, order_amount) VALUES
(1, '2025-04-10 08:00:00', 38.50), -- Alice đặt hàng, tổng 38.50
(1, '2025-04-12 12:00:00', 22.00), -- Alice đặt hàng, tổng 22.00
(2, '2025-04-15 15:30:00', 34.99); -- Bob đặt hàng, tổng 34.99

INSERT INTO order_item (order_id, book_id, quantity, price) VALUES
(1, 1, 1, 20.00), -- Đơn hàng 1: 1 cuốn The Lost World (20.00)
(1, 2, 1, 18.50), -- Đơn hàng 1: 1 cuốn The Hidden Realm (18.50)
(2, 4, 1, 22.00), -- Đơn hàng 2: 1 cuốn Future Worlds (22.00)
(3, 3, 1, 15.00), -- Đơn hàng 3: 1 cuốn Mindful Living (15.00)
(3, 5, 1, 19.99); -- Đơn hàng 3: 1 cuốn AI Revolution (19.99)

SELECT * FROM category;
SELECT * FROM author;
SELECT * FROM "user";
SELECT * FROM book;
SELECT * FROM discount;
SELECT * FROM review;
SELECT * FROM "order";
SELECT * FROM order_item;
