#Veri setinden verilerin çekildiği ve istenilen verilere göre işlendiği database.py dosyası.
import sqlite3
import json
import re
import logging
import math
import os
import time
import sys
import hashlib
import concurrent.futures
import psutil
from typing import Dict, Any, Iterator, Tuple, Optional
from pathlib import Path
import threading
import queue
import gc
from dataclasses import dataclass
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

try:
    from config import Config
except ImportError:
    sys.exit(1)

BATCH_SIZE = min(Config.BATCH_SIZE, 2000)
MAX_WORKERS = min(32, (os.cpu_count() or 4) * 4)
DB_PRAGMAS = {
    "journal_mode": Config.DB_JOURNAL_MODE,
    "synchronous": Config.DB_SYNCHRONOUS,
    "cache_size": f"-{Config.DB_CACHE_SIZE}",
    "temp_store": "MEMORY",
    "busy_timeout": 60000,
    "mmap_size": Config.DB_MMAP_SIZE,
    "auto_vacuum": "FULL",
    "optimize": "0x10002"
}
RETRY_DELAY = 2
MEMORY_CHECK_INTERVAL = 1000

processed_count = 0
total_records = 0
start_time = time.time()
memory_warning_issued = False

@dataclass
class ProcessingStats:
    total_processed: int = 0
    successful_records: int = 0
    failed_records: int = 0
    database_errors: int = 0
    start_time: float = 0.0

stats = ProcessingStats()

def setup_directories():
    Path(Config.LOG_DIR).mkdir(parents=True, exist_ok=True)
    Path(Config.CACHE_DIR).mkdir(parents=True, exist_ok=True)

def clean_text_cached(text: str, max_length: int = 5000) -> str:
    if not isinstance(text, str): return ""
    text = re.sub(r'[^\w\s.,!?;:\'"-]', '', text.strip())
    text = re.sub(r'\s+', ' ', text)
    return text[:max_length] if max_length else text

def calculate_popularity_score_optimized(positive: int, negative: int) -> float:
    total = positive + negative
    if total == 0: return 0.0
    if total < 10:
        return max(0.0, min(1.0, (Config.BAYESIAN_PRIOR_WEIGHT * Config.BAYESIAN_PRIOR_MEAN + positive) / (Config.BAYESIAN_PRIOR_WEIGHT + total)))
    try:
        z = 1.96
        phat = positive / total
        denominator = 1 + (z**2 / total)
        adjusted_phat = phat + (z**2) / (2 * total)
        adjusted_variance = z * math.sqrt((phat * (1 - phat)) / total)
        lower_bound = (adjusted_phat - adjusted_variance) / denominator
        return max(0.0, min(1.0, lower_bound))
    except (ValueError, ZeroDivisionError):
        return max(0.0, min(1.0, positive / total))

def check_memory_usage():
    global memory_warning_issued
    process = psutil.Process()
    memory_percent = process.memory_percent()
    if memory_percent > 85 and not memory_warning_issued:
        logger.warning(f"High Memory: {memory_percent:.1f}%")
        memory_warning_issued = True
        gc.collect()
    elif memory_percent < 70:
        memory_warning_issued = False
    return memory_percent

def create_database(db_path: str = Config.DB_PATH) -> None:
    try:
        with sqlite3.connect(db_path) as conn:
            for pragma, value in DB_PRAGMAS.items():
                conn.execute(f"PRAGMA {pragma}={value}")
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                AppID INTEGER PRIMARY KEY,
                Name TEXT NOT NULL COLLATE NOCASE,
                CleanName TEXT NOT NULL COLLATE NOCASE,
                genres TEXT NOT NULL,
                developer TEXT,
                publisher TEXT,
                price REAL DEFAULT 0.0 CHECK(price >= 0),
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
                average_playtime_forever INTEGER DEFAULT 0,
                processed_timestamp INTEGER DEFAULT (strftime('%s','now'))
            )""")
            cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS games_fts 
            USING fts5(AppID, Name, CleanName, genres, developer, tags, detailed_description, tokenize="porter unicode61")
            """)
            indexes = [
                ("idx_name", "games(Name)"),
                ("idx_clean_name", "games(CleanName)"),
                ("idx_popularity", "games(popularity_score)"),
                ("idx_genres", "games(genres)"),
                ("idx_price", "games(price)"),
                ("idx_developer", "games(developer)"),
                ("idx_playtime", "games(average_playtime_forever)"),
                ("idx_combined_search", "games(popularity_score, price, genres)")
            ]
            for idx_name, idx_def in indexes:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")
            conn.commit()
    except Exception as e:
        logger.error(f"DB Create Error: {e}")
        raise

def download_image_optimized(image_url: str, app_id: int) -> str:
    if not image_url or not image_url.startswith("http"):
        return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
    return image_url

def enhance_game_data_optimized(game_data: Dict[str, Any]) -> Dict[str, Any]:
    enhanced = game_data.copy()
    if enhanced.get('detailed_description') == enhanced.get('about_the_game'):
        enhanced['about_the_game'] = ""
    for field in ['genres', 'developers', 'publishers', 'categories', 'supported_languages']:
        if field in enhanced and not enhanced[field]:
            enhanced[field] = []
    return enhanced

def process_game_record_optimized(game_data: Dict[str, Any], app_id: int) -> Optional[Tuple]:
    global stats
    try:
        if app_id == 0: return None
        if stats.total_processed % MEMORY_CHECK_INTERVAL == 0: check_memory_usage()
        game_data = enhance_game_data_optimized(game_data)
        
        if not game_data.get('name') or not game_data.get('genres'):
            stats.failed_records += 1
            return None
        
        header_image = game_data.get('header_image', '')
        if not header_image or not header_image.startswith('http'):
            header_image = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
        
        price = game_data.get('price', 0.0)
        if isinstance(price, str):
            try: price = float(price)
            except: price = 0.0
            
        name = game_data.get('name', '')[:200]
        clean_name = re.sub(r'[^\w\s]', '', name.lower())[:150]
        genres = ', '.join(filter(None, game_data.get('genres', [])))[:500]
        developer = ', '.join(filter(None, game_data.get('developers', [])))[:200]
        publisher = ', '.join(filter(None, game_data.get('publishers', [])))[:200]
        categories = ', '.join(filter(None, game_data.get('categories', [])))[:500]
        languages = ', '.join(filter(None, game_data.get('supported_languages', [])))[:500]
        tags = json.dumps(game_data.get('tags', {}), ensure_ascii=False, separators=(',', ':'))
        
        positive = int(game_data.get('positive', 0))
        negative = int(game_data.get('negative', 0))
        popularity = calculate_popularity_score_optimized(positive, negative) * 100
        
        detailed_desc = game_data.get('detailed_description', '')
        short_desc = game_data.get('short_description', '')
        combined_desc = detailed_desc if detailed_desc else short_desc
        cleaned_desc = clean_text_cached(combined_desc, 5000)
        short_desc = clean_text_cached(short_desc, 1000)
        
        windows = 1 if game_data.get('windows', False) else 0
        mac = 1 if game_data.get('mac', False) else 0
        linux = 1 if game_data.get('linux', False) else 0
        release_date = str(game_data.get('release_date', ''))[:10]
        achievements = int(game_data.get('achievements', 0))
        estimated_owners = game_data.get('estimated_owners', '')[:50]
        avg_playtime = int(game_data.get('average_playtime_forever', 0))
        
        stats.successful_records += 1
        return (
            app_id, name, clean_name, genres, developer, publisher, price,
            header_image, f"https://store.steampowered.com/app/{app_id}",
            popularity, tags, short_desc, cleaned_desc, positive, negative,
            release_date, achievements, categories, languages, windows, mac, linux,
            estimated_owners, avg_playtime
        )
    except Exception:
        stats.failed_records += 1
        return None

def stream_json_records_optimized(file_path: Path) -> Iterator[Tuple[int, Dict[str, Any]]]:
    try:
        with file_path.open('r', encoding='utf-8', buffering=1024*1024) as f:
            for line in f:
                try:
                    data = json.loads(line)
                    for app_id, game_data in data.items():
                        yield int(app_id), game_data
                except: continue
    except Exception as e:
        logger.error(f"File Read Error: {e}")
        raise

class DatabaseWriter:
    def __init__(self, db_path: str, batch_queue: queue.Queue, stop_event: threading.Event):
        self.db_path = db_path
        self.batch_queue = batch_queue
        self.stop_event = stop_event
        self.conn = None
        
    def connect(self):
        for attempt in range(5):
            try:
                self.conn = sqlite3.connect(self.db_path, timeout=120)
                for pragma, value in DB_PRAGMAS.items():
                    self.conn.execute(f"PRAGMA {pragma}={value}")
                return True
            except sqlite3.OperationalError:
                time.sleep(2)
        return False
    
    def run(self):
        global processed_count
        if not self.connect(): return
        
        insert_query = """
        INSERT OR REPLACE INTO games (
            AppID, Name, CleanName, genres, developer, publisher, price,
            header_image, SteamURL, popularity_score, tags, short_description,
            detailed_description, positive_ratings, negative_ratings,
            release_date, achievements, categories, supported_languages,
            windows, mac, linux, estimated_owners, average_playtime_forever
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        current_batch = []
        while not self.stop_event.is_set() or not self.batch_queue.empty():
            try:
                batch = self.batch_queue.get(timeout=5)
                if batch: current_batch.extend(batch)
                if len(current_batch) >= 5000:
                    self.conn.executemany(insert_query, current_batch)
                    self.conn.commit()
                    processed_count += len(current_batch)
                    current_batch = []
                    logger.info(f"Processed: {processed_count}")
                self.batch_queue.task_done()
            except queue.Empty: continue
            except Exception as e:
                logger.error(f"Write Error: {e}")
        
        if current_batch:
            self.conn.executemany(insert_query, current_batch)
            self.conn.commit()
            processed_count += len(current_batch)
        self.conn.close()

def load_data_optimized(json_file: Path, db_path: str = Config.DB_PATH) -> None:
    global total_records, processed_count, start_time, stats
    start_time = time.time()
    stats.start_time = start_time
    
    batch_queue = queue.Queue(maxsize=100)
    stop_event = threading.Event()
    
    writer = DatabaseWriter(db_path, batch_queue, stop_event)
    writer_thread = threading.Thread(target=writer.run, daemon=True)
    writer_thread.start()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for idx, (app_id, game_data) in enumerate(stream_json_records_optimized(json_file), 1):
            future = executor.submit(process_and_download_wrapper, game_data, app_id)
            futures.append(future)
            if len(futures) >= BATCH_SIZE:
                batch = []
                for f in concurrent.futures.as_completed(futures):
                    res = f.result()
                    if res: batch.append(res)
                if batch: batch_queue.put(batch)
                futures = []
                stats.total_processed = idx
        
        batch = []
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res: batch.append(res)
        if batch: batch_queue.put(batch)

    stop_event.set()
    writer_thread.join()
    populate_fts_table(db_path)

def process_and_download_wrapper(game_data, app_id):
    return process_game_record_optimized(game_data, app_id)

def populate_fts_table(db_path):
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO games_fts (AppID, Name, CleanName, genres, developer, tags, detailed_description) SELECT AppID, Name, CleanName, genres, developer, tags, detailed_description FROM games")
        conn.execute("INSERT INTO games_fts(games_fts) VALUES('optimize')")
        conn.commit()

def convert_json_to_stream_optimized(input_file: Path, output_file: Path) -> None:
    try:
        with open(input_file, 'r', encoding='utf-8') as fin:
            data = json.load(fin)
        with open(output_file, 'w', encoding='utf-8', buffering=8192) as fout:
            for app_id, game_data in tqdm(data.items()):
                json.dump({app_id: game_data}, fout, ensure_ascii=False, separators=(',', ':'))
                fout.write('\n')
    except Exception: raise

def main():
    setup_directories()
    create_database()
    json_stream_file = Path("games.json.stream")
    if not json_stream_file.exists():
        source = Path("games.json")
        if source.exists(): convert_json_to_stream_optimized(source, json_stream_file)
        else: sys.exit(1)
    load_data_optimized(json_stream_file)

if __name__ == '__main__':
    main()
