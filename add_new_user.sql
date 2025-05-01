-- Thêm một người dùng mới với mật khẩu đã hash
INSERT INTO "user" (first_name, last_name, email, password, admin) 
VALUES (
    'John', 
    'Doe', 
    'john.doe@example.com', 
    '$2b$12$Qib/vvgtWsPULl1gsY7sPuqj8pGiPCxSrlpidFHXjXWw1L0o4faHe', 
    FALSE
);

-- Kiểm tra người dùng đã được thêm
SELECT * FROM "user" WHERE email = 'john.doe@example.com';
