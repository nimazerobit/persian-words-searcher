import sqlite3
import time
from flask import Flask, request, render_template, jsonify

DB_FILE = "words.db"
app = Flask(__name__)

CATEGORIES = [
    "همه",
    "فحش ها",
    "اسم دختر",
    "اسم پسر",
    "شغل ها",
    "رنگ ها",
    "اسم ماشین",
    "اسم حیوانات",
    "آمیرزا"
]

def normalize_letters(s: str) -> str:
    """Normalizes Persian letters for search purposes."""
    return s.replace("آ", "ا")

def letter_counts(s: str) -> dict:
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    return counts

def can_make_word_fast(word_counts, letters_counts):
    for ch, count in word_counts.items():
        if letters_counts.get(ch, 0) < count:
            return False
    return True

@app.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES)

@app.route("/search")
def search():
    start = time.time()

    letters = request.args.get("letters", "").strip()
    length_filter = request.args.get("length", "").strip()
    category_filter = request.args.get("category", "").strip()

    try:
        length_filter = int(length_filter) if length_filter else None
    except ValueError:
        length_filter = None

    # Validation: avoid full-table queries
    if not letters and not length_filter and (not category_filter or category_filter == "همه"):
        return jsonify({
            "results": [],
            "error": "حداقل یکی از فیلدهای حروف یا طول یا دسته‌بندی خاص را وارد کنید.",
            "fields": ["lettersInput", "lengthInput", "categorySelect"],
            "server_ms": 0
        })

    if not letters and category_filter != "همه" and not length_filter:
        return jsonify({
            "results": [],
            "error": "برای جستجو در یک دسته‌بندی خاص، فیلد طول یا حروف را پر کنید.",
            "fields": ["lettersInput", "lengthInput"],
            "server_ms": 0
        })

    # Database query
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    query = "SELECT word FROM words WHERE 1=1"
    params = []

    if category_filter and category_filter != "همه":
        query += " AND category = ?"
        params.append(category_filter)

    if length_filter:
        query += " AND LENGTH(word) = ?"
        params.append(length_filter)
    elif letters:
        query += " AND LENGTH(word) <= ?"
        params.append(len(letters))

    cur.execute(query, tuple(params))
    candidates = [row[0] for row in cur.fetchall()]
    con.close()

    if letters:
        # Normalize input letters
        normalized_letters = normalize_letters(letters)
        letters_counts = letter_counts(normalized_letters)

        results = [
            w for w in candidates
            if can_make_word_fast(
                letter_counts(normalize_letters(w)),
                letters_counts
            )
        ]
    else:
        results = candidates

    duration_ms = int((time.time() - start) * 1000)
    return jsonify({"results": results,
                    "count": len(results),
                    "server_ms": duration_ms
                    })

if __name__ == "__main__":
    app.run(debug=False)