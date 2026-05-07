from flask import Flask, request, jsonify, send_from_directory, render_template
from model import GameRecommender
from config import Config
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import logging
import sys
import sqlite3
import os
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

recommender = None
init_done = False
init_error = None

def get_db_connection():
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def load_model_sync():
    global recommender, init_done, init_error
    try:
        recommender = GameRecommender(Config)
        if recommender.initialize(force_rebuild=False):
            init_done = True
        else:
            init_error = "Model initialization failed."
    except Exception as e:
        init_error = str(e)
        logger.error(f"Initialization error: {e}", exc_info=True)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[f"{Config.RATE_LIMIT_PER_HOUR} per hour"],
    storage_uri="memory://" 
)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/search')
@limiter.limit("60 per minute")
def search():
    if not init_done: 
        return jsonify({"error": "System initializing", "status": "error"}), 503
    
    try:
        query = request.args.get('q', '').strip()
        if not query: return jsonify({"error": "Missing query"}), 400
        
        weights = {}
        weight_params = ['vector', 'tag', 'genre', 'visual', 'quality', 'playtime', 'era']
        for p in weight_params:
            val = request.args.get(f'w_{p}')
            if val is not None:
                try:
                    weights[p] = float(val)
                except ValueError:
                    pass

        filters = {
            "genres": request.args.get('genres', '').split(',') if request.args.get('genres') else None,
            "exclude": request.args.get('exclude', '').split(',') if request.args.get('exclude') else None,
            "year_min": request.args.get('year_min'),
            "year_max": request.args.get('year_max'),
            "playtime_min": request.args.get('playtime_min'),
            "playtime_max": request.args.get('playtime_max'),
            "max_price": request.args.get('max_price'),
            "language": request.args.get('language'),
            "is_indie": request.args.get('is_indie') == 'true',
            "weights": weights
        }
        
        results = recommender.recommend_games(query, n=Config.RECOMMENDATION_COUNT, filters=filters)
        return jsonify({
            "results": results, 
            "count": len(results),
            "query": query
        })
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/autocomplete')
@cache.cached(timeout=300, query_string=True)
def autocomplete():
    if not init_done: return jsonify([])
    q = request.args.get('q', '')
    if len(q) < 2: return jsonify([])
    return jsonify(recommender.autocomplete(q))

@app.route('/api/surprise')
def surprise():
    if not init_done: return jsonify({"error": "System not ready"}), 503
    source_game = recommender.get_random_high_rated_game()
    if source_game:
        results = recommender.recommend_games(source_game['Name'], n=Config.RECOMMENDATION_COUNT)
        return jsonify({"source": source_game, "results": results})
    return jsonify({"error": "No games found"}), 404

@app.route('/api/health')
def health():
    return jsonify({
        "status": "ready" if init_done else "initializing",
        "error": init_error
    })

@app.route('/api/comments', methods=['GET', 'POST'])
def comments():
    conn = get_db_connection()
    try:
        if request.method == 'GET':
            appid = request.args.get('appid')
            cursor = conn.cursor()
            cursor.execute("SELECT content, created_at FROM comments WHERE appid = ? ORDER BY created_at DESC", (appid,))
            return jsonify([dict(row) for row in cursor.fetchall()])
        elif request.method == 'POST':
            data = request.json
            conn.execute("INSERT INTO comments (appid, content) VALUES (?, ?)", (data.get('appid'), data.get('content')))
            conn.commit()
            return jsonify({"success": True})
    finally:
        conn.close()

if __name__ == '__main__':
    load_model_sync()
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG)