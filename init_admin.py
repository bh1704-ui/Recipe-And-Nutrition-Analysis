# init_admin.py
import getpass
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash
from urllib.parse import quote_plus

# -----------------------------
# DATABASE CONFIG
# -----------------------------
DB_USER = "root"
DB_PASS = quote_plus("oppoa12@bharath")
DB_HOST = "localhost"
DB_NAME = "NutritionDB"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}")

# -----------------------------
# CREATE ADMIN USER
# -----------------------------
def create_admin():
    print("=== Create Admin User ===")

    name = input("Admin Name: ")
    email = input("Admin Email: ")

    password = getpass.getpass("Admin Password: ")
    confirm = getpass.getpass("Confirm Password: ")

    if password != confirm:
        print("❌ Passwords do not match!")
        return

    hashed = generate_password_hash(password)

    try:
        with engine.begin() as conn:
            # Check duplicate email
            check = conn.execute(text("SELECT 1 FROM `User` WHERE Email = :e"), {"e": email}).fetchone()
            if check:
                print("❌ This email already exists in the database!")
                return

            # Insert admin
            conn.execute(
                text("""
                    INSERT INTO `User`
                    (Name, Email, Password, role)
                    VALUES (:n, :e, :p, 'admin')
                """),
                {"n": name, "e": email, "p": hashed},
            )

        print("\n✅ Admin created successfully!")
        print(f"📧 Email: {email}")
        print("🔐 Password: (hidden)")
        print("Role: admin")

    except Exception as e:
        print(f"❌ Failed to create admin: {e}")


if __name__ == "__main__":
    create_admin()
