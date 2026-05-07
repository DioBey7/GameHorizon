import pandas as pd
import numpy as np
import sqlite3
import re
import json
import os
import joblib
import logging
import math
import faiss
import threading
import difflib
from typing import List, Dict, Any, Union, Tuple
from enum import Enum
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["FOR_DISABLE_CONSOLE_CTRL_HANDLER"] = "1"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

try:
    from config import Config
except ImportError:
    class Config:
        DB_PATH = "games.db"
        MODEL_PATH = "models"
        ARTIFACTS_PATH = os.path.join(MODEL_PATH, "artifacts.joblib")
        SVD_COMPONENTS = 120
        FAISS_NLIST = 100
        FAISS_NPROBE = 10
        FAISS_M_CONTENT = 12
        MIN_SIMILARITY = 0.15
        MIN_POPULARITY = 5
        VECTOR_WEIGHT = 0.15
        TAG_WEIGHT = 0.25
        GENRE_WEIGHT = 0.10
        VISUAL_WEIGHT = 0.25
        QUALITY_WEIGHT = 0.15
        POPULARITY_WEIGHT = 0.10

class MatchReason(Enum):
    VISUAL = (1, "Görsel Stil")
    TAG = (2, "Mekanik")
    GENRE = (3, "Tür")
    THEME = (4, "Tema")
    SERIES = (5, "Seri")
    DEVELOPER = (6, "Geliştirici")
    QUALITY = (7, "Yüksek Kalite")
    POPULARITY = (8, "Popülerlik")

    def __init__(self, code, description):
        self.code = code
        self.description = description

class GameRecommender:
    def __init__(self, config=None):
        self.config = config or Config
        self.db_path = self.config.DB_PATH
        self.model_path = Path(self.config.MODEL_PATH)
        self.artifacts_path = Path(self.config.ARTIFACTS_PATH)
        self.model_path.mkdir(parents=True, exist_ok=True)
        self.df = None
        self.models = {}
        self.content_index = None
        self.name_model = None
        self.name_embeddings = None
        self.name_index = None
        self.init_lock = threading.Lock()
        self._init_dictionaries()

    def _init_dictionaries(self):
        self.visual_tags = {'pixel art', 'voxel', 'low poly', 'realistic', 'anime', 'cartoon', 'hand-drawn', 'isometric', 'top-down', 'first-person', 'third-person', '2d', '3d', 'vr', 'retro', 'minimalist', 'noir', 'colorful', 'dark', 'atmospheric', 'stylized', 'cinematic', 'side scroller', 'text-based', 'psychedelic', 'surreal', 'abstract'}
        self.series_patterns = {r'witcher': "The Witcher", r'dark souls|elden ring|bloodborne|sekiro': "Soulsborne", r'elder scrolls|skyrim|oblivion|morrowind': "The Elder Scrolls", r'gta|grand theft auto': "GTA", r'resident evil': "Resident Evil", r'fallout': "Fallout", r'mass effect': "Mass Effect", r'bioshock': "BioShock"}

    def initialize(self, force_rebuild=False):
        with self.init_lock:
            try:
                from sentence_transformers import SentenceTransformer
                self.name_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                if not force_rebuild and self.artifacts_path.exists():
                    if self._load_artifacts(): return True
                return self._train_and_save_model()
            except Exception as e:
                logger.error(f"Init Error: {e}")
                return False

    def _train_and_save_model(self):
        if not os.path.exists(self.db_path): return False
        try:
            conn = sqlite3.connect(self.db_path)
            self.df = pd.read_sql_query("SELECT * FROM games WHERE popularity_score > 5", conn)
            conn.close()
            if self.df.empty: return False
            
            self.df['developer'] = self.df['developer'].apply(lambda x: str(x) if (x and x != "None") else "BELİRTİLMEMİŞ")
            
            total_votes = self.df['positive_ratings'] + self.df['negative_ratings']
            self.df['positive_ratio'] = (self.df['positive_ratings'] / (total_votes + 1)) * 100
            self.df['quality_score'] = ((self.df['positive_ratings'] / (total_votes + 1)) * 0.7) + ((self.df['popularity_score'] / 100.0) * 0.3)
            
            tfidf = TfidfVectorizer(stop_words='english', max_features=25000, dtype=np.float32)
            tfidf_matrix = tfidf.fit_transform(self.df['genres'].fillna('') + " " + self.df['tags'].fillna('') + " " + self.df['short_description'].fillna(''))
            svd = TruncatedSVD(n_components=self.config.SVD_COMPONENTS)
            lsa_matrix = svd.fit_transform(tfidf_matrix)
            faiss.normalize_L2(lsa_matrix)
            self.models['lsa_matrix'] = lsa_matrix.astype(np.float32)
            
            self.name_embeddings = self.name_model.encode(self.df['Name'].tolist(), batch_size=32, show_progress_bar=True).astype(np.float32)
            self._build_indices()
            
            joblib.dump({'df': self.df, 'lsa_matrix': self.models['lsa_matrix'], 'name_embeddings': self.name_embeddings}, self.artifacts_path, compress=3)
            return True
        except Exception as e:
            logger.error(f"Train Error: {e}")
            return False

    def _load_artifacts(self):
        try:
            art = joblib.load(self.artifacts_path)
            self.df, self.models['lsa_matrix'], self.name_embeddings = art['df'], art['lsa_matrix'], art['name_embeddings']
            self._build_indices()
            return True
        except: return False

    def _build_indices(self):
        d_c = self.models['lsa_matrix'].shape[1]
        self.content_index = faiss.IndexFlatL2(d_c)
        self.content_index.add(self.models['lsa_matrix'])
        d_n = self.name_embeddings.shape[1]
        self.name_index = faiss.IndexHNSWFlat(d_n, 32)
        faiss.normalize_L2(self.name_embeddings)
        self.name_index.add(self.name_embeddings)

    def recommend_games(self, game_names: Union[str, List[str]], n: int = 15, filters: dict = None):
        if self.df is None or self.content_index is None: return []
        if isinstance(game_names, str): game_names = [game_names]
        indices = [self._find_game_idx(name) for name in game_names]
        indices = [i for i in indices if i is not None]
        if not indices: return []
        query_vec = np.mean([self.models['lsa_matrix'][i] for i in indices], axis=0).reshape(1, -1)
        faiss.normalize_L2(query_vec)
        D, I = self.content_index.search(query_vec, min(len(self.df), 500))
        candidates = []
        base_game = self.df.iloc[indices[0]]
        base_visuals = self._extract_visual_tags(base_game)
        base_genres = set(g.strip().lower() for g in str(base_game['genres']).split(','))
        seen_ids = {int(self.df.iloc[i]['AppID']) for i in indices}
        if filters and filters.get('exclude'):
            for exc in filters['exclude']:
                idx = self._find_game_idx(exc)
                if idx is not None: seen_ids.add(int(self.df.iloc[idx]['AppID']))
        w = filters.get('weights', {}) if filters else {}
        cfg_w = (float(w.get('vector', 0.15)), float(w.get('tag', 0.25)), float(w.get('genre', 0.10)), float(w.get('visual', 0.25)), float(w.get('quality', 0.15)), float(w.get('popularity', 0.10)))

        for idx, dist in zip(I[0], D[0]):
            if idx == -1: continue
            cand = self.df.iloc[idx]
            cand_id = int(cand["AppID"])
            if cand_id in seen_ids: continue
            if filters:
                if filters.get('genres'):
                    if not set(g.strip().lower() for g in str(cand['genres']).split(',')).intersection(set(g.strip().lower() for g in filters['genres'])): continue
                if filters.get('max_price') is not None and float(cand['price']) > float(filters['max_price']): continue
                if filters.get('is_indie') and 'Indie' not in str(cand['genres']): continue

            score, reasons, breakdown = self._calculate_smart_score(base_game, cand, dist, base_visuals, base_genres, cfg_w)
            if score < self.config.MIN_SIMILARITY: continue
            candidates.append({"AppID": cand_id, "Name": str(cand["Name"]), "ImageURL": str(cand["header_image"]), "price": float(cand["price"]), "developer": str(cand["developer"]), "similarity": float(round(score, 4)), "match_reasons": [{"description": r.description} for r in reasons], "breakdown": breakdown, "approval_ratio": float(cand['positive_ratio'])})
            seen_ids.add(cand_id)
        return sorted(candidates, key=lambda x: x['similarity'], reverse=True)[:n]

    def _calculate_smart_score(self, base, cand, dist, b_vis, b_gen, weights):
        v_w, t_w, g_w, vi_w, q_w, p_w = weights
        vec_s = max(0.0, 1.0 - (dist / 1.4))
        t1, t2 = set(json.loads(base.get('tags', '{}')).keys()), set(json.loads(cand.get('tags', '{}')).keys())
        tag_s = len(t1 & t2) / len(t1 | t2) if (t1 | t2) else 0.0
        c_gen = set(g.strip().lower() for g in str(cand['genres']).split(','))
        gen_s = len(b_gen & c_gen) / len(b_gen | c_gen) if (b_gen and c_gen) else 0.0
        c_vis = self._extract_visual_tags(cand)
        vis_s = len(b_vis & c_vis) / len(b_vis | c_vis) if (b_vis and c_vis) else 0.0
        q_s = float(cand.get('quality_score', 0.5))
        pop_s = float(cand.get('popularity_score', 0)) / 100.0
        score = ((vec_s * v_w) + (tag_s * t_w) + (gen_s * g_w) + (vis_s * vi_w) + (q_s * q_w) + (pop_s * p_w)) / sum(weights)
        reasons = []
        if vis_s > 0.4: reasons.append(MatchReason.VISUAL)
        if tag_s > 0.35: reasons.append(MatchReason.TAG)
        if q_s > 0.80: reasons.append(MatchReason.QUALITY)
        if pop_s > 0.70: reasons.append(MatchReason.POPULARITY)
        return float(min(score, 0.99)), reasons, {'vector': int(vec_s*100), 'tag': int(tag_s*100), 'genre': int(gen_s*100), 'visual': int(vis_s*100), 'quality': int(q_s*100), 'popularity': int(pop_s*100)}

    def _extract_visual_tags(self, row):
        return {t.lower() for t in set(json.loads(row.get('tags', '{}')).keys())}.intersection(self.visual_tags)

    def _find_game_idx(self, name):
        s_n = re.sub(r'[^\w]', '', name.lower().strip())
        m = self.df[self.df['CleanName'] == s_n]
        if not m.empty: return m.index[0]
        cl = difflib.get_close_matches(name, self.df['Name'].tolist(), n=1, cutoff=0.6)
        if cl: return self.df[self.df['Name'] == cl[0]].index[0]
        return None

    def autocomplete(self, q):
        s_q = q.lower().strip()
        res = self.df[self.df['CleanName'].str.startswith(re.sub(r'[^\w]', '', s_q), na=False)]
        return res.sort_values('popularity_score', ascending=False)['Name'].head(5).tolist()

    def get_random_high_rated_game(self):
        hq = self.df[self.df['quality_score'] > 0.75]
        r = hq.sample(1).iloc[0]
        return {"Name": r["Name"], "AppID": int(r["AppID"])}