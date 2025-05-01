from auth.password import get_password_hash

# Generate hash for password "test123"
password = "tester"
hashed = get_password_hash(password)
print(f"Password: {password}")
print(f"Hashed: {hashed}")