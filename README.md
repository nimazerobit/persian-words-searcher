
# Persian Words Searcher
A simple Flask-based web application for searching Persian words stored in an SQLite database.

<img width="2480" height="1062" alt="web page screenshot" src="https://github.com/user-attachments/assets/54d5596f-21ef-4a8b-826e-ddade08e65a8" />


## Categories
- همه (All)
- فحش ها (Insults)
- اسم دختر (Girl names)
- اسم پسر (Boy names)
- شغل ها (Jobs)
- رنگ ها (Colors)
- اسم ماشین (Car names)
- اسم حیوانات (Animal names)
- آمیرزا (Amirza)

## Requirements
- Python 3.8+
- Flask

Install dependencies:
```bash
pip install flask
```

## Run the App
Start the Flask server:
```bash
python main.py
```
By default, the app runs on `http://127.0.0.1:5000/`

## API Endpoints

  

### `GET /`

Renders the index page with category selection.

  

### `GET /search`

Search for words based on filters.

**Query Parameters:**

-  `letters` (string) – available letters to build words

-  `length` (int) – filter by word length

-  `category` (string) – filter by category

**Response JSON:**

```json
{
  "results": ["علی", "لیلا"],
  "count": 2,
  "server_ms": 5
}

```
## Sources
- [jadijadi/persianwords](https://github.com/jadijadi/persianwords)
- [Digikala Magazine - Complete Amirza Guide](https://www.digikala.com/mag/complete-amirza-guide/)
