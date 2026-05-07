import sqlite3
import json
import re
import html
import ijson
import threading
import queue
import math
import sys
from pathlib import Path
from dataclasses import dataclass

try:
    from config import Config
except ImportError:
    sys.exit(1)

HTML_TAG_RE = re.compile(r'<[^>]+>')
URL_RE = re.compile(r'http\S+')
CLEAN_RE = re.compile(r'[^\w\s.,!?;:\'"-]')
SPACE_RE = re.compile(r'\s+')
CLEAN_NAME_RE = re.compile(r'[^\w\s]')

DB_PRAGMAS = {
    "journal_mode": Config.DB_JOURNAL_MODE,
    "synchronous": "NORMAL",
    "cache_size": f"-{Config.DB_CACHE_SIZE}",
    "temp_store": "MEMORY",
    "mmap_size": Config.DB_MMAP_SIZE,
    "page_size": 4096,
    "busy_timeout": 60000,
    "auto_vacuum": "NONE"
}

@dataclass
class ProcessingStats:
    successful_records: int = 0
    failed_records: int = 0

stats = ProcessingStats()

def clean_text(text: str, max_length: int = 5000) -> str:
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = HTML_TAG_RE.sub(' ', text)
    text = URL_RE.sub('', text)
    text = CLEAN_RE.sub('', text.strip())
    text = SPACE_RE.sub(' ', text)
    return text[:max_length]

def calculate_popularity_score(positive: int, negative: int) -> float:
    total = positive + negative
    if total == 0:
        return 0.0
    
    if total < 50:
        prior_weight = getattr(Config, 'BAYESIAN_PRIOR_WEIGHT', 10.0)
        prior_mean = getattr(Config, 'BAYESIAN_PRIOR_MEAN', 0.5)
        return max(0.0, min(1.0, (prior_weight * prior_mean + positive) / (prior_weight + total)))
    
    z = 1.96
    phat = positive / total
    denominator = 1 + (z**2 / total)
    adjusted_phat = phat + (z**2) / (2 * total)
    lower_bound = (adjusted_phat - (z * math.sqrt((phat * (1 - phat)) / total))) / denominator
    
    log_boost = math.log10(total + 1) / 9.0
    final_score = lower_bound + (log_boost * 0.15)
    
    return max(0.0, min(1.0, final_score))

def init_db(db_path: str = Config.DB_PATH):
    with sqlite3.connect(db_path) as conn:
        for pragma, value in DB_PRAGMAS.items():
            conn.execute(f"PRAGMA {pragma}={value}")
            
        conn.execute("""
            CREATE TABLE IF NOT EXISTS games (
                AppID INTEGER PRIMARY KEY,
                Name TEXT NOT NULL COLLATE NOCASE,
                CleanName TEXT NOT NULL COLLATE NOCASE,
                genres TEXT NOT NULL,
                developer TEXT,
                publisher TEXT,
                price REAL DEFAULT 0.0,
                header_image TEXT,
                SteamURL TEXT,
                popularity_score REAL DEFAULT 0.0,
                tags TEXT,
                short_description TEXT,
                detailed_description TEXT,
                positive_ratings INTEGER DEFAULT 0,
                negative_ratings INTEGER DEFAULT 0,
                release_date TEXT,
                achievements INTEGER DEFAULT 0,
                categories TEXT,
                supported_languages TEXT,
                windows BOOLEAN DEFAULT 0,
                mac BOOLEAN DEFAULT 0,
                linux BOOLEAN DEFAULT 0,
                estimated_owners TEXT,
                average_playtime_forever INTEGER DEFAULT 0
            )""")
            
        conn.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appid INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(appid) REFERENCES games(AppID)
            )""")

        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS games_fts 
            USING fts5(
                Name, CleanName, genres, developer, tags, detailed_description,
                content='games', content_rowid='AppID',
                tokenize="porter unicode61"
            )""")
            
        indexes = [
            ("idx_clean_name", "games(CleanName)"),
            ("idx_popularity", "games(popularity_score)"),
            ("idx_genres", "games(genres)"),
            ("idx_price", "games(price)")
        ]
        for idx_name, idx_def in indexes:
            conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")

def process_record(app_id: int, data: dict) -> tuple:
    try:
        if not data.get('name') or not data.get('genres'):
            return None
            
        header_image = data.get('header_image') or f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
        
        raw_price = data.get('price', 0.0)
        try:
            price = float(str(raw_price).replace(',', '.'))
        except (ValueError, TypeError):
            price = 0.0
            
        name = data.get('name', '')[:200]
        clean_name = CLEAN_NAME_RE.sub('', name.lower()).strip()[:150]
        genres = ', '.join(filter(None, data.get('genres', [])))[:500]
        developer = ', '.join(filter(None, data.get('developers', [])))[:200]
        publisher = ', '.join(filter(None, data.get('publishers', [])))[:200]
        categories = ', '.join(filter(None, data.get('categories', [])))[:500]
        languages = ', '.join(filter(None, data.get('supported_languages', [])))[:500]
        
        tags_data = data.get('tags', {})
        tags = json.dumps({t: 1 for t in tags_data} if isinstance(tags_data, list) else tags_data, ensure_ascii=False)
        
        positive = int(data.get('positive', 0))
        negative = int(data.get('negative', 0))
        popularity = calculate_popularity_score(positive, negative) * 100
        
        desc = f"{data.get('short_description', '')} {data.get('about_the_game', '')} {data.get('detailed_description', '')}"
        cleaned_desc = clean_text(desc, 8000)
        short_desc = clean_text(data.get('short_description', ''), 1000)
        
        stats.successful_records += 1
        return (
            app_id, name, clean_name, genres, developer, publisher, price,
            header_image, f"https://store.steampowered.com/app/{app_id}",
            popularity, tags, short_desc, cleaned_desc, positive, negative,
            str(data.get('release_date', ''))[:10], int(data.get('achievements', 0)),
            categories, languages, 
            1 if data.get('windows') else 0, 1 if data.get('mac') else 0, 1 if data.get('linux') else 0,
            data.get('estimated_owners', '')[:50], int(data.get('average_playtime_forever', 0))
        )
    except Exception:
        stats.failed_records += 1
        return None

def db_worker(db_path: str, q: queue.Queue):
    conn = sqlite3.connect(db_path, timeout=60)
    for pragma, value in DB_PRAGMAS.items():
        conn.execute(f"PRAGMA {pragma}={value}")
    
    buffer = []
    sql = """INSERT OR REPLACE INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    
    while True:
        item = q.get()
        if item is None:
            if buffer:
                conn.executemany(sql, buffer)
                conn.commit()
            break
        
        buffer.append(item)
        if len(buffer) >= 10000:
            conn.executemany(sql, buffer)
            conn.commit()
            buffer.clear()
        q.task_done()
    
    conn.execute("INSERT INTO games_fts(games_fts) VALUES('rebuild')")
    conn.commit()
    conn.execute("INSERT INTO games_fts(games_fts) VALUES('optimize')")
    conn.commit()
    conn.close()

def load_data(json_path: Path):
    init_db()
    q = queue.Queue(maxsize=20000)
    writer = threading.Thread(target=db_worker, args=(Config.DB_PATH, q))
    writer.start()
    
    try:
        with json_path.open('rb') as f:
            for app_id, data in ijson.kvitems(f, ''):
                record = process_record(int(app_id), data)
                if record:
                    q.put(record)
    finally:
        q.put(None)
        writer.join()

if __name__ == '__main__':
    target_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("games.json")
    if target_path.exists():
        load_data(target_path)