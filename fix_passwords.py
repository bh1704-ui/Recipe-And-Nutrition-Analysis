# fix_passwords.py
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash

# --- DB CONFIG ---
DB_USER = "root"
DB_PASS = quote_plus("oppoa12@bharath")
DB_HOST = "localhost"
DB_NAME = "NutritionDB"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

print("🔍 Checking users for plaintext passwords...\n")

# Step 1 — Fetch all users
with engine.begin() as conn:
    result = conn.execute(text("SELECT User_ID, Password FROM User"))
    rows = result.fetchall()

updated_count = 0

for row in rows:
    user_id = row[0]          # tuple index 0 = User_ID
    password_value = row[1]   # tuple index 1 = Password

    # Detect if password is already hashed
    if isinstance(password_value, str) and password_value.startswith(("pbkdf2:", "scrypt:", "argon2")):
        print(f"✔ User_ID {user_id} already hashed. Skipping.")
        continue

    # Otherwise hash the plaintext password
    hashed = generate_password_hash(password_value)

    with engine.begin() as conn:
        conn.execute(
            text("UPDATE User SET Password = :pwd WHERE User_ID = :uid"),
            {"pwd": hashed, "uid": user_id}
        )

    updated_count += 1
    print(f"🔒 Hashed password for User_ID {user_id}")

print("\n✅ Completed!")
print(f"Total updated users: {updated_count}")
