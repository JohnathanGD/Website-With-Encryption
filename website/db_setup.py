import sqlite3
from config import FERNET_KEY
from cryptography.fernet import Fernet

f = Fernet(FERNET_KEY)
conn = sqlite3.connect('database/contest.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS BakingContestUSERS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK(age > 0 AND age < 121),
    phone_number TEXT NOT NULL,
    security_level INTEGER NOT NULL CHECK(security_level BETWEEN 1 AND 3),
    password TEXT NOT NULL
)
""")

cursor.execute("SELECT COUNT(*) FROM BakingContestUSERS WHERE name = ?", (f.encrypt(b'admin').decode('utf-8'),))
admin_exists = cursor.fetchone()[0]

if not admin_exists:
    # Create the admin user
    admin_username = 'admin'
    admin_password = 'adminpassword'  # Replace with a secure password
    admin_phone = '1111111111'
    encrypted_name = f.encrypt(admin_username.encode('utf-8'))
    encrypted_password = f.encrypt(admin_password.encode('utf-8'))
    encrypted_phone = f.encrypt(admin_phone.encode('utf-8'))

    cursor.execute("""
    INSERT INTO BakingContestUSERS (name, age, phone_number, security_level, password)
    VALUES (?, ?, ?, ?, ?)
    """, (encrypted_name, 1, encrypted_phone, 3, encrypted_password))

    print("Admin account created with username: 'admin' and password: 'adminpassword'")


cursor.execute("""
CREATE TABLE IF NOT EXISTS BakingContestENTRIES (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    baking_item_name TEXT NOT NULL,
    excellent_votes INTEGER DEFAULT 0,
    ok_votes INTEGER DEFAULT 0,
    bad_votes INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES BakingContestUSERS (id)
)
""")

print("Database has been successfully set up!")

conn.commit()
conn.close()
