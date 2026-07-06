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
    return s.replace("آ", "ا").replace('أ', 'ا').replace('ي', 'ی')

def letter_counts(s: str) -> dict:
    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    return counts

def can_make_word_fast(word_counts, letters_counts):
    for ch, count in word_counts.items():
        if letters_counts.get(ch, 0) < count:
            return False
    return True

@app.route("/")
def index():
    return render_template("index.html", categories=CATEGORIES)

@app.route("/help")
def help():
    return render_template("help.html")

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

    # --- determine search mode ---
    search_mode = "anagram"
    search_term = letters

    if letters.startswith('#') and letters.endswith('#') and len(letters) > 2:
        search_mode = "startswith"
        search_term = letters[1:-1]

    elif letters.startswith('@') and letters.endswith('@') and len(letters) > 2:
        search_mode = "endswith"
        search_term = letters[1:-1]

    # --- Validation ---
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
            "error": "برای جستجو در یک دسته‌بندی یکی از فیلد های طول یا حروف را پر کنید.",
            "fields": ["lettersInput", "lengthInput"],
            "server_ms": 0
        })

    # --- database query construction ---
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()

    query = "SELECT word FROM words WHERE 1=1"
    params = []

    # exclude bad words when selected all
    if category_filter and category_filter != "همه":
        query += " AND category = ?"
        params.append(category_filter)
    else:
        query += " AND category != ?"
        params.append("فحش ها")

    # length filter
    if length_filter:
        query += " AND LENGTH(word) = ?"
        params.append(length_filter)

    # letters filter based on mode
    if letters:
        if search_mode == "startswith":
            query += " AND word LIKE ?"
            params.append(search_term + "%")
        elif search_mode == "endswith":
            query += " AND word LIKE ?"
            params.append("%" + search_term)
        else: # anagram mode
            if not length_filter:
                query += " AND LENGTH(word) <= ?"
                params.append(len(search_term))

    cur.execute(query, tuple(params))
    candidates = [row[0] for row in cur.fetchall()]
    con.close()

    if letters and search_mode == "anagram":
        normalized_letters = normalize_letters(search_term)
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
    return jsonify({
        "results": results,
        "count": len(results),
        "server_ms": duration_ms
    })

if __name__ == "__main__":
    app.run(debug=False)