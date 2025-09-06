import sqlite3
from pathlib import Path

# Map file names -> Persian category labels
CATEGORY_FILES = {
    "persian_swear_words.txt": "فحش ها",
    "name_girl.txt": "اسم دختر",
    "name_boy.txt": "اسم پسر",
    "jobs.txt": "شغل ها",
    "colors.txt": "رنگ ها",
    "cars.txt": "اسم ماشین",
    "animals.txt": "اسم حیوانات",
    "amirza.txt": "آمیرزا",
}

DB_FILE = "words.db"

con = sqlite3.connect(DB_FILE)
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS words")
cur.execute("""
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    category TEXT NOT NULL
)
""")
cur.execute("CREATE INDEX idx_word_length ON words(LENGTH(word))")
cur.execute("CREATE INDEX idx_category ON words(category)")

for filename, category in CATEGORY_FILES.items():
    path = Path(filename)
    if not path.exists():
        print(f"[-] Skipping missing file: {filename}")
        continue
    
    with path.open("r", encoding="utf-8") as f:
        words = {w.strip() for w in f if w.strip()}  # remove empties + duplicates
    cur.executemany(
        "INSERT INTO words (word, category) VALUES (?, ?)",
        [(w, category) for w in words]
    )
    print(f"[+] Added {len(words)} words from {filename} ({category})")

con.commit()
con.close()
print(f"[+] Database saved to {DB_FILE}")