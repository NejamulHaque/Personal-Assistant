import bcrypt

plain_password = "nejamul@123"  # 👈 Replace with your desired password
hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
print("Hashed Password:", hashed.decode())