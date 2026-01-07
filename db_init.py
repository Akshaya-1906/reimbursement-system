import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Admin table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")

# Student club passwords
cur.execute("""
CREATE TABLE IF NOT EXISTS student_passwords (
    club_name TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")

# Insert admin (fixed)
cur.execute(
    "INSERT OR IGNORE INTO users VALUES (?, ?)",
    ("admin", "admin123")
)

# Insert student club passwords
clubs = [
    ("sportsteam", "sport123"),
    ("libraryteam", "lib123"),
    ("ecoteam", "eco123")
]

cur.executemany(
    "INSERT OR IGNORE INTO student_passwords VALUES (?, ?)",
    clubs
)

conn.commit()
conn.close()

print("Database initialized successfully")
