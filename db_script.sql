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

-- Thêm thêm các danh mục sách
INSERT INTO category (category_name, category_desc) VALUES
('Mystery', 'Mystery and detective novels'),
('Romance', 'Love stories and romantic fiction'),
('Biography', 'True stories about real people'),
('History', 'Books about historical events and periods'),
('Fantasy', 'Books featuring magical and supernatural elements'),
('Self-Help', 'Books for personal development'),
('Thriller', 'Suspenseful and exciting fiction'),
('Horror', 'Scary and frightening stories'),
('Poetry', 'Collections of poems and verses'),
('Cooking', 'Cookbooks and culinary guides');

-- Thêm thêm các tác giả
INSERT INTO author (author_name, author_bio) VALUES
('Agatha Christie', 'The Queen of Mystery, known for her detective novels'),
('Stephen King', 'Master of horror and supernatural fiction'),
('J.K. Rowling', 'Creator of the Harry Potter series'),
('George Orwell', 'Author of dystopian classics like 1984'),
('Jane Austen', 'Renowned for her romantic fiction set in the British gentry'),
('Ernest Hemingway', 'Nobel Prize winner known for his economical writing style'),
('Mark Twain', 'American writer known for his wit and social commentary'),
('Virginia Woolf', 'Modernist writer and feminist'),
('Charles Dickens', 'Victorian era novelist known for his memorable characters'),
('Leo Tolstoy', 'Russian writer regarded as one of the greatest authors of all time');

-- Thêm 100 cuốn sách mới
INSERT INTO book (category_id, author_id, book_title, book_summary, book_price, book_cover_photo) VALUES
-- Fiction books (category_id = 1)
(1, 4, 'The Silent Echo', 'A mysterious tale of a town where sounds begin to disappear', 24.99, 'silent_echo.jpg'),
(1, 5, 'Whispers in the Dark', 'A collection of short stories that will keep you up at night', 19.95, 'whispers.jpg'),
(1, 6, 'The Last Letter', 'A story about a letter that changes the course of a family's history', 22.50, 'last_letter.jpg'),
(1, 7, 'Echoes of Tomorrow', 'A tale of time travel and its consequences', 21.99, 'echoes.jpg'),
(1, 8, 'The Forgotten Path', 'A journey of self-discovery through an ancient forest', 18.75, 'forgotten_path.jpg'),
(1, 9, 'Shadows of the Past', 'A story about confronting one's history', 23.50, 'shadows.jpg'),
(1, 10, 'The Glass House', 'A family drama set in a transparent home', 20.25, 'glass_house.jpg'),
(1, 11, 'Beyond the Horizon', 'An adventure across uncharted territories', 25.99, 'horizon.jpg'),
(1, 12, 'The Silent Witness', 'A courtroom drama with a twist', 19.99, 'witness.jpg'),
(1, 13, 'Threads of Fate', 'Lives intertwined by destiny', 22.95, 'threads.jpg'),

-- Non-Fiction books (category_id = 2)
(2, 4, 'The Art of Mindfulness', 'A guide to living in the present moment', 18.99, 'mindfulness.jpg'),
(2, 5, 'Success Principles', 'Key strategies for achieving your goals', 24.50, 'success.jpg'),
(2, 6, 'The Science of Sleep', 'Understanding the importance of rest', 21.75, 'sleep.jpg'),
(2, 7, 'Nutrition Essentials', 'A comprehensive guide to healthy eating', 26.99, 'nutrition.jpg'),
(2, 8, 'Financial Freedom', 'Steps to achieve financial independence', 19.95, 'financial.jpg'),
(2, 9, 'The Power of Habit', 'How habits shape our lives and how to change them', 23.50, 'habit.jpg'),
(2, 10, 'Public Speaking Mastery', 'Overcome fear and speak with confidence', 20.25, 'speaking.jpg'),
(2, 11, 'Digital Detox', 'Reclaiming your life from technology', 17.99, 'detox.jpg'),
(2, 12, 'The Art of Negotiation', 'Strategies for successful negotiations', 22.95, 'negotiation.jpg'),
(2, 13, 'Emotional Intelligence', 'Understanding and managing emotions', 19.99, 'emotional.jpg'),

-- Science Fiction books (category_id = 3)
(3, 4, 'Galactic Empire', 'The rise and fall of an interstellar civilization', 23.99, 'galactic.jpg'),
(3, 5, 'Quantum Leap', 'Adventures in parallel universes', 21.50, 'quantum.jpg'),
(3, 6, 'The Last Astronaut', 'A journey to the edge of the solar system', 25.75, 'astronaut.jpg'),
(3, 7, 'Alien Contact', 'First encounter with extraterrestrial intelligence', 22.99, 'alien.jpg'),
(3, 8, 'Cybernetic Revolution', 'The merging of humans and machines', 20.95, 'cybernetic.jpg'),
(3, 9, 'Time Paradox', 'The consequences of altering the past', 24.50, 'paradox.jpg'),
(3, 10, 'Virtual Reality', 'A world inside the digital realm', 19.25, 'virtual.jpg'),
(3, 11, 'The Mars Colony', 'Establishing human presence on the red planet', 26.99, 'mars.jpg'),
(3, 12, 'Sentient AI', 'The emergence of conscious artificial intelligence', 23.95, 'sentient.jpg'),
(3, 13, 'Space Odyssey', 'A journey through the cosmos', 21.99, 'odyssey.jpg'),

-- Mystery books (category_id = 4)
(4, 4, 'The Missing Key', 'A detective story about a locked room mystery', 22.99, 'missing_key.jpg'),
(4, 5, 'Murder at Midnight', 'A classic whodunit set in a mansion', 20.50, 'midnight_murder.jpg'),
(4, 6, 'The Vanishing Act', 'The mysterious disappearance of a famous magician', 23.75, 'vanishing.jpg'),
(4, 7, 'Cold Case', 'Reopening an unsolved murder from decades ago', 21.99, 'cold_case.jpg'),
(4, 8, 'The Cryptic Cipher', 'Breaking a code to solve a crime', 19.95, 'cipher.jpg'),
(4, 9, 'Silent Witness', 'A murder investigation with no witnesses', 24.50, 'silent_witness.jpg'),
(4, 10, 'The Perfect Alibi', 'A seemingly perfect crime with no suspects', 22.25, 'alibi.jpg'),
(4, 11, 'Deadly Inheritance', 'A family torn apart by a suspicious will', 25.99, 'inheritance.jpg'),
(4, 4, 'The Detective's Dilemma', 'A case that challenges a detective's ethics', 20.95, 'dilemma.jpg'),
(4, 5, 'Unsolved', 'A series of connected crimes across decades', 23.99, 'unsolved.jpg'),

-- Romance books (category_id = 5)
(5, 6, 'Love in Paris', 'A romantic encounter in the city of love', 19.99, 'paris_love.jpg'),
(5, 7, 'Second Chance', 'Rekindling a lost love', 18.50, 'second_chance.jpg'),
(5, 8, 'The Wedding Planner', 'Finding love while planning others' weddings', 21.75, 'wedding.jpg'),
(5, 9, 'Summer Romance', 'A seasonal love story at the beach', 20.99, 'summer.jpg'),
(5, 10, 'Forbidden Love', 'A romance that defies societal norms', 22.95, 'forbidden.jpg'),
(5, 11, 'The Love Letter', 'A mistakenly delivered letter leads to love', 19.50, 'love_letter.jpg'),
(5, 12, 'Unexpected Feelings', 'Finding love in the most unexpected place', 23.25, 'unexpected.jpg'),
(5, 13, 'Across the Distance', 'A long-distance relationship tested by time', 21.99, 'distance.jpg'),
(5, 4, 'The Arrangement', 'A marriage of convenience turns into love', 20.95, 'arrangement.jpg'),
(5, 5, 'Heart's Desire', 'Following one's heart against all odds', 24.99, 'desire.jpg'),

-- Biography books (category_id = 6)
(6, 6, 'The Innovator', 'The life of a revolutionary tech entrepreneur', 26.99, 'innovator.jpg'),
(6, 7, 'Political Giant', 'Biography of an influential world leader', 24.50, 'political.jpg'),
(6, 8, 'The Artist's Life', 'The journey of a renowned painter', 22.75, 'artist.jpg'),
(6, 9, 'Sports Legend', 'The career of an iconic athlete', 25.99, 'sports.jpg'),
(6, 10, 'Scientific Genius', 'The life and discoveries of a groundbreaking scientist', 23.95, 'scientist.jpg'),
(6, 11, 'Hollywood Star', 'Behind the scenes of a famous actor's life', 21.50, 'hollywood.jpg'),
(6, 12, 'Musical Journey', 'The life story of a legendary musician', 27.25, 'musical.jpg'),
(6, 13, 'Literary Icon', 'Biography of a celebrated author', 24.99, 'literary.jpg'),
(6, 4, 'The Explorer', 'Adventures of a world-renowned explorer', 22.95, 'explorer.jpg'),
(6, 5, 'Humanitarian Hero', 'The life dedicated to helping others', 25.50, 'humanitarian.jpg'),

-- History books (category_id = 7)
(7, 6, 'Ancient Civilizations', 'The rise and fall of early human societies', 27.99, 'ancient.jpg'),
(7, 7, 'World War Chronicles', 'A comprehensive history of global conflicts', 25.50, 'war.jpg'),
(7, 8, 'Renaissance Era', 'The rebirth of art and culture in Europe', 23.75, 'renaissance.jpg'),
(7, 9, 'Industrial Revolution', 'How technology changed the world', 26.99, 'industrial.jpg'),
(7, 10, 'Colonial Times', 'The age of exploration and colonization', 24.95, 'colonial.jpg'),
(7, 11, 'Medieval Europe', 'Life during the Middle Ages', 22.50, 'medieval.jpg'),
(7, 12, 'The Cold War', 'The decades-long geopolitical tension', 28.25, 'cold_war.jpg'),
(7, 13, 'Ancient Egypt', 'The civilization of the Nile', 25.99, 'egypt.jpg'),
(7, 4, 'The Roman Empire', 'The rise and fall of Rome', 23.95, 'roman.jpg'),
(7, 5, 'Modern History', 'Key events of the 20th century', 26.50, 'modern.jpg'),

-- Fantasy books (category_id = 8)
(8, 6, 'Dragon's Realm', 'A world where dragons and humans coexist', 23.99, 'dragon.jpg'),
(8, 7, 'The Enchanted Forest', 'A magical journey through a mystical woodland', 21.50, 'enchanted.jpg'),
(8, 8, 'Wizard's Apprentice', 'Learning the arts of magic', 24.75, 'wizard.jpg'),
(8, 9, 'The Mythical Creatures', 'Encounters with legendary beings', 22.99, 'mythical.jpg'),
(8, 10, 'Kingdom of Magic', 'A realm governed by magical laws', 20.95, 'kingdom.jpg'),
(8, 11, 'The Prophecy', 'A foretold destiny that must be fulfilled', 25.50, 'prophecy.jpg'),
(8, 12, 'Elemental Powers', 'Mastering the forces of nature', 23.25, 'elemental.jpg'),
(8, 13, 'The Chosen One', 'A hero destined to save the world', 26.99, 'chosen.jpg'),
(8, 4, 'Magical Artifacts', 'The quest for powerful magical items', 22.95, 'artifacts.jpg'),
(8, 5, 'The Fairy Realm', 'Adventures in the land of fairies', 24.99, 'fairy.jpg'),

-- Self-Help books (category_id = 9)
(9, 6, 'Finding Your Purpose', 'Discovering your life's mission', 19.99, 'purpose.jpg'),
(9, 7, 'Stress Management', 'Techniques to reduce anxiety and stress', 18.50, 'stress.jpg'),
(9, 8, 'Positive Thinking', 'The power of optimism', 21.75, 'positive.jpg'),
(9, 9, 'Time Management', 'Making the most of your time', 20.99, 'time.jpg'),
(9, 10, 'Building Relationships', 'Creating meaningful connections', 22.95, 'relationships.jpg'),
(9, 11, 'Career Success', 'Strategies for professional growth', 19.50, 'career.jpg'),
(9, 12, 'Mindful Living', 'Being present in everyday life', 23.25, 'mindful_living.jpg'),
(9, 13, 'Overcoming Obstacles', 'Turning challenges into opportunities', 21.99, 'obstacles.jpg'),
(9, 4, 'Personal Growth', 'Continuous self-improvement', 20.95, 'growth.jpg'),
(9, 5, 'Happiness Habits', 'Daily practices for a joyful life', 24.99, 'happiness.jpg'),

-- Thriller books (category_id = 10)
(10, 6, 'The Conspiracy', 'Uncovering a global plot', 22.99, 'conspiracy.jpg'),
(10, 7, 'Deadly Pursuit', 'A chase across continents', 21.50, 'pursuit.jpg'),
(10, 8, 'The Hostage', 'A high-stakes negotiation', 24.75, 'hostage.jpg'),
(10, 9, 'Covert Operation', 'A secret mission with global implications', 23.99, 'covert.jpg'),
(10, 10, 'The Assassin', 'A hired killer with a conscience', 20.95, 'assassin.jpg');

-- Add some discounts for the new books
INSERT INTO discount (book_id, discount_price, discount_start_date, discount_end_date) VALUES
(10, 18.20, '2025-05-01', '2025-05-31'), -- Discount for Threads of Fate
(20, 17.99, '2025-05-15', '2025-06-15'), -- Discount for Emotional Intelligence
(30, 19.79, '2025-06-01', '2025-06-30'), -- Discount for Space Odyssey
(40, 18.95, '2025-05-10', '2025-06-10'), -- Discount for Unsolved
(50, 22.49, '2025-06-15', '2025-07-15'); -- Discount for Heart's Desire

-- Add some reviews for the new books
INSERT INTO review (book_id, review_title, review_details, review_date, rating_start) VALUES
(10, 'Captivating Story', 'I couldn''t put this book down! The characters are so well developed.', '2025-04-25 11:20:00', '5'),
(10, 'Interesting Plot', 'A unique storyline with unexpected twists.', '2025-04-26 15:45:00', '4'),
(20, 'Life Changing', 'This book has completely changed how I handle my emotions.', '2025-04-27 09:30:00', '5'),
(30, 'Space Adventure', 'A thrilling journey through space with vivid descriptions.', '2025-04-28 14:15:00', '4'),
(40, 'Gripping Mystery', 'Kept me guessing until the very end!', '2025-04-29 16:40:00', '5'),
(50, 'Beautiful Romance', 'A touching love story that brought tears to my eyes.', '2025-04-30 10:55:00', '4');

-- Add some orders for the new books
INSERT INTO "order" (user_id, order_date, order_amount) VALUES
(1, '2025-05-01 09:15:00', 67.97), -- Alice's new order
(2, '2025-05-02 13:30:00', 45.98); -- Bob's new order

-- Add order items for the new orders
INSERT INTO order_item (order_id, book_id, quantity, price) VALUES
(4, 10, 1, 22.95), -- Order 4: 1 copy of Threads of Fate
(4, 20, 1, 19.99), -- Order 4: 1 copy of Emotional Intelligence
(4, 30, 1, 21.99), -- Order 4: 1 copy of Space Odyssey
(5, 40, 1, 23.99), -- Order 5: 1 copy of Unsolved
(5, 50, 1, 24.99); -- Order 5: 1 copy of Heart's Desire

-- Queries to check the data
SELECT * FROM category;
SELECT * FROM author;
SELECT * FROM "user";
SELECT * FROM book;
SELECT * FROM discount;
SELECT * FROM review;
SELECT * FROM "order";
SELECT * FROM order_item;
