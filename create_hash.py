from werkzeug.security import generate_password_hash

password = "password"  # 実際のパスワードをここに書く
hashed = generate_password_hash(password)

print("このハッシュを.envにコピペしてください：")
print(hashed)
