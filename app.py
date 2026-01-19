# API ve bağlantı ayarlarının yapıldığı app.py dosyası
from flask import Flask, request, jsonify, send_from_directory, render_template
from model import GameRecommender
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import logging
import os
import threading
import time
import sys
import sqlite3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class Config:
    DB_PATH = "games.db"
    MODEL_PATH = "models"
    CACHE_TIMEOUT = 3600
    RATE_LIMIT = "300 per hour"

recommender = None
init_done = False
init_error = None
init_lock = threading.Lock()

def get_db_connection():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_backend():
    global recommender, init_done, init_error
    
    with init_lock:
        if init_done:
            return

        print("\n" + "="*50)
        print(">>> [SİSTEM] MODEL EĞİTİMİ/YÜKLEMESİ BAŞLATILIYOR...")
        print(">>> [SİSTEM] Bu işlem veritabanı boyutuna göre 1-2 dakika sürebilir.")
        print("="*50 + "\n")
        
        try:
            recommender = GameRecommender()
            success = recommender.initialize()
            
            if success:
                init_done = True
                print("\n" + "="*50)
                print(">>> [SİSTEM] MODEL HAZIR! API İSTEKLERİNE AÇIK.")
                print("="*50 + "\n")
            else:
                init_error = "Model initialization returned False"
                logger.error("Model başlatılamadı (Return False)")
                
        except Exception as e:
            init_error = str(e)
            logger.error(f"Model başlatma hatası: {e}", exc_info=True)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[Config.RATE_LIMIT],
    storage_uri="memory://" 
)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/health')
def health():
    return jsonify({
        "status": "ready" if init_done else "initializing",
        "error": init_error,
        "message": "Sistem yükleniyor..." if not init_done else "Sistem aktif"
    })

@app.route('/api/search')
@limiter.limit("60 per minute")
def search():
    if not init_done: 
        return jsonify({
            "error": "Sistem hazırlanıyor, lütfen bekleyiniz...", 
            "status": "initializing",
            "progress": 50
        }), 503
    
    try:
        query = request.args.get('q', '').strip()
        if not query: return jsonify({"error": "Lütfen bir oyun adı girin"}), 400
        
        filters = {
            "genres": request.args.get('genres', '').split(',') if request.args.get('genres') else None,
            "exclude": request.args.get('exclude', '').split(',') if request.args.get('exclude') else None,
            "year_min": request.args.get('year_min'),
            "year_max": request.args.get('year_max'),
            "playtime_min": request.args.get('playtime_min'),
            "playtime_max": request.args.get('playtime_max')
        }
        
        results = recommender.recommend_games(query, n=15, filters=filters)
        return jsonify({
            "results": results, 
            "count": len(results),
            "query": query
        })
    except Exception as e:
        logger.error(f"Arama hatası: {e}")
        return jsonify({"error": "Arama sırasında hata oluştu"}), 500

@app.route('/api/autocomplete')
@cache.cached(timeout=300, query_string=True)
def autocomplete():
    if not init_done: return jsonify([])
    q = request.args.get('q', '')
    if len(q) < 2: return jsonify([])
    return jsonify(recommender.autocomplete(q))

@app.route('/api/surprise')
def surprise():
    if not init_done: return jsonify({"error": "Sistem hazırlanıyor"}), 503
    
    source_game = recommender.get_random_high_rated_game()
    if source_game:
        results = recommender.recommend_games(source_game['Name'], n=15)
        return jsonify({
            "source": source_game,
            "results": results
        })
    return jsonify({"error": "Sürpriz oyun bulunamadı"}), 404

@app.route('/api/comments', methods=['GET'])
def get_comments():
    appid = request.args.get('appid')
    if not appid:
        return jsonify({"error": "AppID required"}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content, created_at FROM comments WHERE appid = ? ORDER BY created_at DESC", (appid,))
        comments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(comments)
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        return jsonify({"error": "Failed to fetch comments"}), 500

@app.route('/api/comments', methods=['POST'])
@limiter.limit("5 per minute")
def post_comment():
    data = request.json
    appid = data.get('appid')
    content = data.get('content', '').strip()
    
    if not appid or not content:
        return jsonify({"error": "AppID and content required"}), 400
    
    if len(content) > 500:
        return jsonify({"error": "Comment too long (max 500 chars)"}), 400
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO comments (appid, content) VALUES (?, ?)", (appid, content))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error saving comment: {e}")
        return jsonify({"error": "Failed to save comment"}), 500

def start_background_thread():
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        init_thread = threading.Thread(target=initialize_backend, daemon=True)
        init_thread.start()

if __name__ == '__main__':
    start_background_thread()
    app.run(host='0.0.0.0', port=5000, debug=True)
