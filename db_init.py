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
    ("Astronomy_Club", "astronomy123"),
    ("Coding_Club", "coding123"),
    ("Cooking_Club", "cooking123"),
    ("Creative_Arts_Club", "creativearts123"),
    ("Dance_Club", "dance123"),
    ("Eco_Club", "eco123"),
    ("Lets_Talk_Club", "letstalk123"),
    ("Entrepreneurs_Club", "entrepreneurs123"),
    ("GDSC_Club", "gdsc123"),
    ("iTech_Broadcast_Club", "itechbroadcast123"),
    ("Visual_Arts_Club", "visualarts123"),
    ("Paws_and_Wings_Club", "pawsandwings123"),
    ("itech_Intellect_Quiz_Club", "itechintellectquiz123"),
    ("iTech_Music_Club", "itechmusic123"),
    ("NCC_Club", "ncc123"),
    ("NSS_Club", "nss123"),
    ("Rotaract_Club", "rotaract123"),
    ("Science_and_Humanities_Association_Club", "sha123"),
    ("Women_Empowerment_Cell_Club", "wec123"),
    ("YRC_RRC_Club", "yrcrrc123"),
    ("Inthinai_Tamil_Mandram_Club", "tamilmandram123"),
    ("Photography_Club", "photography123"),
    ("Readers_Club", "readers123")
]

cur.executemany(
    "INSERT OR IGNORE INTO student_passwords VALUES (?, ?)",
    clubs
)

conn.commit()
conn.close()

print("Database initialized successfully")
