# Modelin eğitildiği, özelliklerinin ve parametrelerinin kullanıldığı, config dosyasının bağlandığı model.py dosyası.
import pandas as pd
import numpy as np
import sqlite3
import re
import json
import os
import joblib
import logging
import hashlib
import time
import math
from typing import List, Dict, Any, Optional, Set, Tuple, Union
from enum import Enum
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from collections import defaultdict
import faiss
from pathlib import Path
import gc
from dataclasses import dataclass
from difflib import SequenceMatcher
import shutil
from tqdm import tqdm

logger = logging.getLogger(__name__)

try:
    from config import Config
except ImportError:
    class Config:
        DB_PATH = "games.db"
        MODEL_PATH = "models"
        MIN_SIMILARITY = 0.25
        MIN_POPULARITY = 15
        RECOMMENDATION_COUNT = 15
        SVD_COMPONENTS = 192
        BATCH_SIZE = 2048
        MAX_RECOMMENDATIONS = 400
        GENRE_WEIGHT = 0.35
        GAMEPLAY_WEIGHT = 0.25
        THEME_WEIGHT = 0.20
        PRICE_WEIGHT = 0.10
        VISUAL_WEIGHT = 0.30
        DESCRIPTION_WEIGHT = 0.15
        TAG_WEIGHT = 0.25
        CATEGORY_WEIGHT = 0.10
        RARE_GENRE_BONUS = 0.12
        VISUAL_STYLE_BONUS = 0.15
        SERIES_BONUS = 0.25
        DEVELOPER_BONUS = 0.18
        EXCLUSION_PENALTY = -0.45
        MIN_EXCLUSION_MATCH = 0.20
        PRICE_QUOTA = {'low': 6, 'mid': 5, 'high': 4}
        MAX_DEVELOPER_RECOMMENDATIONS = 2
        RARE_GENRES = {"Visual Novel", "Psychological Horror", "Walking Simulator", "Metroidvania", "Roguelike", "Soulslike", "Immersive Sim", "Grand Strategy", "4X"}

@dataclass
class ModelStats:
    load_time: float = 0.0
    recommendation_time: float = 0.0
    cache_hits: int = 0
    total_recommendations: int = 0

class MatchReason(Enum):
    GENRE = (1, "Benzer tür")
    GAMEPLAY = (2, "Benzer oynanış")
    THEME = (3, "Benzer tema")
    PRICE = (4, "Benzer fiyat")
    DEVELOPER = (5, "Aynı geliştirici")
    SERIES = (6, "Aynı seri")
    POPULAR = (7, "Popüler oyun")
    TAG = (8, "Benzer etiket")
    PLATFORM = (10, "Platform uyumlu")
    DESCRIPTION = (11, "Benzer açıklama")
    VISUAL = (12, "Görsel benzerlik")
    CATEGORY = (13, "Benzer kategori")
    CONTENT_MATCH = (14, "İçerik benzerliği")
    EXCLUDED = (15, "Dışlanan içerik")
    MULTI_GAME = (16, "Ortak Öneri")

    def __init__(self, code, description):
        self.code = code
        self.description = description

class OptimizedGameRecommender:
    def __init__(self, db_path: str = None, model_path: str = None, config=None):
        self.config = config or Config
        self.db_path = db_path or self.config.DB_PATH
        self.model_path = Path(model_path or self.config.MODEL_PATH)
        self.model_path.mkdir(exist_ok=True)
        
        self.MIN_SIMILARITY = self.config.MIN_SIMILARITY
        self.MIN_POPULARITY = self.config.MIN_POPULARITY
        self.RECOMMENDATION_COUNT = self.config.RECOMMENDATION_COUNT
        self.SVD_COMPONENTS = self.config.SVD_COMPONENTS
        self.MAX_RECOMMENDATIONS = self.config.MAX_RECOMMENDATIONS
        
        self._models_loaded = False
        self._data_loaded = False
        self.stats = ModelStats()
        
        self.df: Optional[pd.DataFrame] = None
        self.models: dict = {}
        self.dynamic_weights = {
            MatchReason.GENRE: self.config.GENRE_WEIGHT,
            MatchReason.GAMEPLAY: self.config.GAMEPLAY_WEIGHT,
            MatchReason.THEME: self.config.THEME_WEIGHT,
            MatchReason.PRICE: self.config.PRICE_WEIGHT,
            MatchReason.POPULAR: 0.05,
            MatchReason.VISUAL: self.config.VISUAL_WEIGHT,
            MatchReason.DESCRIPTION: self.config.DESCRIPTION_WEIGHT,
            MatchReason.TAG: self.config.TAG_WEIGHT,
            MatchReason.CATEGORY: self.config.CATEGORY_WEIGHT,
        }
        
        self.text_model = None
        self.name_index = None
        self.content_index = None
        self.genre_weights = self._initialize_genre_weights()
        self.recommendation_cache = {}
        
        self._init_developer_map()
        self._init_series_patterns()
        self._init_enhanced_keywords()
        self._init_visual_keywords()

    def initialize(self, force_rebuild=False):
        try:
            print(">>> [MODEL] Başlatılıyor...")
            
            if not self._load_data():
                logger.error("Veri yüklenemedi!")
                return False
            
            print(f">>> [MODEL] {len(self.df)} oyun yüklendi. Vektörleştirme başlıyor...")

            self.text_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            self._build_models()
            
            self._models_loaded = True
            print(">>> [MODEL] Tüm modeller başarıyla hazırlandı.")
            return True

        except Exception as e:
            logger.error(f"Model başlatma hatası: {e}", exc_info=True)
            return False

    def _load_data(self):
        try:
            if not os.path.exists(self.db_path):
                logger.error(f"Veritabanı bulunamadı: {self.db_path}")
                return False

            conn = sqlite3.connect(self.db_path)
            query = """
                SELECT AppID, Name, CleanName, genres, developer, publisher, price, 
                       header_image, SteamURL, popularity_score, tags, short_description, 
                       detailed_description, release_date, average_playtime_forever, 
                       windows, mac, linux, categories 
                FROM games WHERE popularity_score > ?
            """
            self.df = pd.read_sql_query(query, conn, params=(self.MIN_POPULARITY,))
            conn.close()
            
            if self.df.empty: 
                logger.warning("Veritabanı boş veya filtreye uygun oyun yok.")
                return False
            
            self.df['price'] = self.df['price'].astype('float32')
            self.df['popularity_score'] = self.df['popularity_score'].astype('float16')
            
            self.df['normalized_dev'] = self.df['developer'].fillna("").str.lower().apply(self._normalize_developer)
            self.df['series'] = self.df['Name'].fillna("").apply(self._extract_series)
            
            tqdm.pandas(desc="Gameplay Features")
            self.df['gameplay_features'] = self.df.apply(lambda r: self._extract_enhanced_keywords(r, self.gameplay_keywords), axis=1)
            self.df['theme_features'] = self.df.apply(lambda r: self._extract_enhanced_keywords(r, self.theme_keywords), axis=1)
            self.df['visual_features'] = self.df.apply(lambda r: self._extract_enhanced_keywords(r, self.visual_keywords), axis=1)
            
            return True
        except Exception as e:
            logger.error(f"Veri yükleme hatası: {e}")
            return False

    def _build_models(self):
        print(">>> [MODEL] TF-IDF Matrisi oluşturuluyor...")
        combined_features = self.df['genres'].astype(str) + " " + \
                           self.df['tags'].astype(str) + " " + \
                           self.df['short_description'].astype(str) + " " + \
                           self.df['developer'].astype(str) + " " + \
                           self.df['visual_features'].apply(lambda x: " ".join(x)).astype(str)
        
        tfidf = TfidfVectorizer(max_features=20000, stop_words='english', dtype=np.float32, min_df=2, ngram_range=(1, 2))
        tfidf_matrix = tfidf.fit_transform(combined_features)
        
        print(">>> [MODEL] SVD (LSA) Boyut indirgeme uygulanıyor...")
        svd = TruncatedSVD(n_components=self.config.SVD_COMPONENTS)
        self.models['lsa_matrix'] = svd.fit_transform(tfidf_matrix).astype('float32')
        faiss.normalize_L2(self.models['lsa_matrix'])
        
        print(">>> [MODEL] FAISS İçerik indeksi kuruluyor (IVF)...")
        d = self.models['lsa_matrix'].shape[1]
        nlist = 200 
        quantizer = faiss.IndexFlatL2(d)
        self.content_index = faiss.IndexIVFFlat(quantizer, d, nlist)
        self.content_index.train(self.models['lsa_matrix'])
        self.content_index.add(self.models['lsa_matrix'])
        
        print(">>> [MODEL] İsim arama indeksi oluşturuluyor...")
        self._build_name_index()

    def _build_name_index(self):
        names = self.df['Name'].fillna('').tolist()
        batch_size = 512
        name_vecs_list = []
        
        for i in range(0, len(names), batch_size):
            batch = names[i:i + batch_size]
            vecs = self.text_model.encode(batch, show_progress_bar=False, device='cpu').astype('float32')
            name_vecs_list.append(vecs)
        
        name_vecs = np.vstack(name_vecs_list)
        faiss.normalize_L2(name_vecs)
        d = name_vecs.shape[1]
        self.name_index = faiss.IndexFlatIP(d)
        self.name_index.add(name_vecs)

    def recommend_games(self, game_names: Union[str, List[str]], n: int = None, filters: dict = None) -> List[Dict[str, Any]]:
        if n is None: n = self.RECOMMENDATION_COUNT
        
        filters = filters or {}
        genre_filter = filters.get('genres')
        exclude_filter = filters.get('exclude')
        year_min = filters.get('year_min')
        year_max = filters.get('year_max')
        playtime_min = filters.get('playtime_min')
        playtime_max = filters.get('playtime_max')

        if isinstance(game_names, str):
            game_names = [g.strip() for g in game_names.split('+') if g.strip()]

        cache_key = f"rec_{hash(tuple(game_names))}_{n}_{hash(json.dumps(filters, sort_keys=True))}"
        if cache_key in self.recommendation_cache:
            self.stats.cache_hits += 1
            return self.recommendation_cache[cache_key]

        if not self._models_loaded: return []

        target_indices = []
        for name in game_names:
            idx = self._find_game_index(name)
            if idx is not None: target_indices.append(idx)
        
        if not target_indices: return []

        if len(target_indices) > 1:
            vectors = [self.models['lsa_matrix'][i] for i in target_indices]
            query_vector = np.mean(vectors, axis=0).reshape(1, -1)
            base_game = self.df.iloc[target_indices[0]] 
        else:
            base_idx = target_indices[0]
            query_vector = self.models['lsa_matrix'][base_idx].reshape(1, -1)
            base_game = self.df.iloc[base_idx]

        faiss.normalize_L2(query_vector)
        self.content_index.nprobe = 40 
        k_search = min(len(self.df), self.MAX_RECOMMENDATIONS * 6)
        distances, indices = self.content_index.search(query_vector.astype(np.float32), k_search)
        indices = indices[0]
        distances = distances[0]

        candidates = []
        seen_ids = set([int(self.df.iloc[i]["AppID"]) for i in target_indices])
        developer_counts = defaultdict(int)

        for cand_idx, dist in zip(indices, distances):
            if cand_idx in target_indices: continue
            if cand_idx >= len(self.df): continue 
            
            candidate = self.df.iloc[cand_idx]
            cand_id = int(candidate["AppID"])
            if cand_id in seen_ids: continue
            
            if genre_filter:
                candidate_genres = self._get_genres(candidate)
                if not self._matches_genre_filter_enhanced(candidate_genres, genre_filter): continue
            
            try:
                rel_date = str(candidate['release_date'])[:4]
                if rel_date.isdigit():
                    year = int(rel_date)
                    if year_min and year < int(year_min): continue
                    if year_max and year > int(year_max): continue
            except: pass

            try:
                pt = int(candidate.get('average_playtime_forever', 0))
                pt_hours = pt / 60
                if playtime_min and pt_hours < int(playtime_min): continue
                if playtime_max and pt_hours > int(playtime_max): continue
            except: pass

            is_multi = len(target_indices) > 1
            score, reasons, explain, breakdown = self._calculate_score_enhanced(base_game, candidate, dist, exclude_filter, is_multi)
            
            if score is None or score < self.MIN_SIMILARITY: continue
            if reasons and reasons[0] == MatchReason.EXCLUDED: continue
            
            dev = candidate.get('normalized_dev', '')
            if dev and developer_counts.get(dev, 0) >= self.config.MAX_DEVELOPER_RECOMMENDATIONS: continue
            
            candidates.append({
                "AppID": cand_id,
                "Name": candidate["Name"],
                "ImageURL": self._fix_image_url(candidate),
                "genres": [g.strip() for g in str(candidate["genres"]).split(",") if g.strip()],
                "price": float(candidate["price"]),
                "SteamURL": str(candidate.get("SteamURL", "")),
                "similarity": round(float(score), 4),
                "match_reasons": [{"code": r.code, "description": r.description} for r in reasons],
                "primary_match": int(reasons[0].code) if reasons else 0,
                "explanation": explain,
                "breakdown": breakdown,
                "year": str(candidate.get('release_date', ''))[:4],
                "playtime": int(candidate.get('average_playtime_forever', 0)),
                "popularity_score": float(candidate.get("popularity_score", 0))
            })
            if dev: developer_counts[dev] += 1
            seen_ids.add(cand_id)

        candidates.sort(key=lambda x: x['similarity'], reverse=True)
        final_recs = self._refine_recommendations(candidates, n)
        
        self.recommendation_cache[cache_key] = final_recs
        return final_recs

    def _find_game_index(self, name):
        name = name.lower().strip()
        vec = self.text_model.encode([name], device='cpu').astype('float32')
        faiss.normalize_L2(vec)
        D, I = self.name_index.search(vec, 1)
        if D[0][0] > 0.70:
            return I[0][0]
        
        clean = re.sub(r'[^\w]', '', name)
        clean_names = self.df['CleanName'].astype(str)
        matches = clean_names[clean_names == clean]
        if not matches.empty:
            return matches.index[0]
        return None

    def autocomplete(self, query, limit=5):
        if not self._models_loaded: return []
        query = query.lower()
        vec = self.text_model.encode([query], device='cpu').astype('float32')
        faiss.normalize_L2(vec)
        D, I = self.name_index.search(vec, limit*3)
        candidates = []
        for idx in I[0]:
            if idx < 0 or idx >= len(self.df): continue
            name = self.df.iloc[idx]['Name']
            if query in name.lower(): candidates.append(name)
        return candidates[:limit]

    def get_random_high_rated_game(self):
        if self.df is None or self.df.empty: return None
        subset = self.df[(self.df['popularity_score'] > 75) & (self.df['price'] > 0)]
        if subset.empty: return None
        game = subset.sample(1).iloc[0]
        return {"Name": game['Name'], "AppID": int(game['AppID'])}

    def _matches_genre_filter_enhanced(self, game_genres, filters, match_threshold=0.3):
        if not filters: return True
        if not game_genres: return False
        
        game_genres_lower = set([g.lower().strip() for g in game_genres])
        filter_terms_lower = [t.lower().strip() for t in filters]
        
        for filter_term in filter_terms_lower:
            if filter_term in game_genres_lower:
                return True
            pattern = r'\b' + re.escape(filter_term) + r'\b'
            for g in game_genres_lower:
                if re.search(pattern, g):
                    return True
        return False

    def _calculate_score_enhanced(self, base, candidate, dist, exclude_filter, is_multi=False):
        score, reasons, explain = self._calculate_score(base, candidate, dist)
        if score is None: return None, [], None, None
        
        breakdown = self._get_similarity_breakdown(base, candidate)
        
        if is_multi:
            reasons.insert(0, MatchReason.MULTI_GAME)
            score += 0.05

        if exclude_filter and score > 0:
            candidate_genres = self._get_genres(candidate)
            exclusion_ratio = self._matches_exclusion_ratio(candidate_genres, exclude_filter)
            if exclusion_ratio >= self.config.MIN_EXCLUSION_MATCH:
                score += self.config.EXCLUSION_PENALTY
                if score <= 0.10:
                    return None, [MatchReason.EXCLUDED], None, breakdown
                explain += f" (Dışlama Cezası)"
                reasons.append(MatchReason.EXCLUDED)
                breakdown['excluded'] = round(exclusion_ratio * 100)
            else:
                breakdown['excluded'] = 0
                
        return score, reasons, explain, breakdown

    def _calculate_score(self, base, candidate, dist):
        base_genres = self._get_genres(base)
        cand_genres = self._get_genres(candidate)
        genre_intersection = set(base_genres) & set(cand_genres)
        is_rare = len(self.config.RARE_GENRES & set(base_genres)) > 0
        
        vector_sim = max(0, 1.0 - (math.sqrt(dist) / 1.35))

        if not genre_intersection and not is_rare and vector_sim < 0.45:
            return None, [], None
        
        genre_sim = self._weighted_jaccard(set(base_genres), set(cand_genres))
        gameplay_sim = self._set_similarity(set(base['gameplay_features']), set(candidate['gameplay_features']))
        theme_sim = self._set_similarity(set(base['theme_features']), set(candidate['theme_features']))
        visual_sim = self._set_similarity(set(base['visual_features']), set(candidate['visual_features']))
        
        price_sim = self._price_similarity(float(base['price']), float(candidate['price']))
        
        base_dev = str(base.get('normalized_dev', '')).strip()
        cand_dev = str(candidate.get('normalized_dev', '')).strip()
        base_series = str(base.get('series', '')).strip()
        cand_series = str(candidate.get('series', '')).strip()
        
        series_match = (base_series == cand_series) and base_series
        dev_match = (base_dev == cand_dev) and base_dev
        
        visual_style_bonus = 0.0
        if self._has_similar_visual_style(base, candidate):
            visual_style_bonus = self.config.VISUAL_STYLE_BONUS
            
        contributions = {
            MatchReason.GENRE: self.dynamic_weights[MatchReason.GENRE] * genre_sim,
            MatchReason.GAMEPLAY: self.dynamic_weights[MatchReason.GAMEPLAY] * gameplay_sim,
            MatchReason.THEME: self.dynamic_weights[MatchReason.THEME] * theme_sim,
            MatchReason.VISUAL: self.dynamic_weights[MatchReason.VISUAL] * visual_sim,
            MatchReason.PRICE: self.dynamic_weights[MatchReason.PRICE] * price_sim,
            MatchReason.TAG: self.dynamic_weights[MatchReason.TAG] * 0.15, 
            MatchReason.DEVELOPER: self.config.DEVELOPER_BONUS if dev_match else 0,
            MatchReason.SERIES: self.config.SERIES_BONUS if series_match else 0
        }
        
        score = sum(contributions.values()) + (vector_sim * 0.40) + visual_style_bonus
        if is_rare: score += self.config.RARE_GENRE_BONUS
        
        if score < self.MIN_SIMILARITY: return None, [], None
        
        reasons = []
        if series_match: reasons.append(MatchReason.SERIES)
        if dev_match: reasons.append(MatchReason.DEVELOPER)
        if genre_sim > 0.3: reasons.append(MatchReason.GENRE)
        if gameplay_sim > 0.3: reasons.append(MatchReason.GAMEPLAY)
        if theme_sim > 0.3: reasons.append(MatchReason.THEME)
        if visual_sim > 0.3: reasons.append(MatchReason.VISUAL)
        
        if reasons:
            primary = max(contributions, key=contributions.get)
            if primary in reasons: reasons.remove(primary)
            reasons.insert(0, primary)
        else:
            reasons.append(MatchReason.POPULAR)
            
        return score, reasons, "Similarity Match"

    def _get_similarity_breakdown(self, base, candidate):
        base_genres = set(self._get_genres(base))
        cand_genres = set(self._get_genres(candidate))
        
        visual_score = 0
        if 'lsa_matrix' in self.models:
             try:
                base_vec = self.models['lsa_matrix'][self.df.index.get_loc(base.name)].reshape(1,-1)
                cand_vec = self.models['lsa_matrix'][self.df.index.get_loc(candidate.name)].reshape(1,-1)
                visual_score = int(cosine_similarity(base_vec, cand_vec)[0][0] * 100)
             except: pass

        return {
            "genre": int(self._weighted_jaccard(base_genres, cand_genres) * 100),
            "gameplay": int(self._set_similarity(set(base['gameplay_features']), set(candidate['gameplay_features'])) * 100),
            "theme": int(self._set_similarity(set(base['theme_features']), set(candidate['theme_features'])) * 100),
            "price": int(self._price_similarity(float(base['price']), float(candidate['price'])) * 100),
            "visual": max(0, visual_score),
            "popularity": int(candidate.get('popularity_score', 0))
        }

    def _normalize_developer(self, dev):
        dev = str(dev).lower()
        for k, v in self.developer_map.items():
            if k in dev: return v
        return dev

    def _extract_series(self, name):
        name = str(name).lower()
        for p, s in self.series_patterns.items():
            if re.search(p, name): return s
        return ""

    def _get_genres(self, series):
        return [g.strip() for g in str(series.get('genres', '')).split(',') if g.strip()]

    def _weighted_jaccard(self, s1, s2):
        if not s1 or not s2: return 0.0
        inter = s1 & s2
        union = s1 | s2
        w_inter = sum(self.genre_weights.get(g, 1.0) for g in inter)
        w_union = sum(self.genre_weights.get(g, 1.0) for g in union)
        return w_inter / w_union if w_union else 0.0

    def _set_similarity(self, s1, s2):
        if not s1 or not s2: return 0.0
        return len(s1 & s2) / len(s1 | s2)

    def _price_similarity(self, p1, p2):
        if p1 == 0 and p2 == 0: return 1.0
        if p1 == 0 or p2 == 0: return 0.2
        ratio = min(p1, p2) / max(p1, p2)
        return ratio

    def _matches_exclusion_ratio(self, genres, exclude_list):
        if not exclude_list: return 0.0
        g_lower = set(g.lower() for g in genres)
        e_lower = set(e.lower() for e in exclude_list)
        inter = g_lower & e_lower
        return len(inter) / len(e_lower) if e_lower else 0.0

    def _extract_enhanced_keywords(self, row, keywords):
        text = (str(row.get('tags','')) + " " + str(row.get('short_description',''))).lower()
        found = set()
        for k in keywords:
            if k in text: found.add(k)
        return found
    
    def _calculate_tag_similarity(self, t1, t2):
        if not t1 or not t2: return 0.0
        common = set(t1.keys()) & set(t2.keys())
        if not common: return 0.0
        weight = sum(min(t1[t], t2[t]) for t in common)
        total = sum(t1.values())
        return weight / total if total > 0 else 0.0

    def _has_similar_visual_style(self, base, cand):
        b_text = (str(base['Name']) + " " + str(base.get('short_description',''))).lower()
        c_text = (str(cand['Name']) + " " + str(cand.get('short_description',''))).lower()
        
        visual_overlap = set(base['visual_features']) & set(cand['visual_features'])
        if visual_overlap: return True

        styles = ["pixel art", "retro", "realistic", "cartoon", "anime", "hand-drawn", "low poly", "isometric", "first-person", "third-person"]
        for s in styles:
            if s in b_text and s in c_text: return True
        return False
        
    def _refine_recommendations(self, candidates, n):
        final = []
        seen = set()
        prices = defaultdict(int)
        
        # Eğer çok az aday varsa skor barajını düşür
        if len(candidates) < n:
            return candidates

        for c in candidates:
            if len(final) >= n: break
            if c['AppID'] in seen: continue
            
            p_cat = 'high' if c['price'] > 30 else 'mid' if c['price'] > 10 else 'low'
            if prices[p_cat] >= self.config.PRICE_QUOTA[p_cat]: continue
            
            final.append(c)
            seen.add(c['AppID'])
            prices[p_cat] += 1
        return final

    def _fix_image_url(self, game):
        url = game.get('header_image', '')
        if url and url.startswith('http'): return url
        return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{game.get('AppID')}/header.jpg"

    def _initialize_genre_weights(self):
        return {
            'RPG': 4.5, 'Action-RPG': 4.8, 'Adventure': 4.2, 'Story Rich': 4.6,
            'Visual Novel': 4.3, 'Simulation': 3.8, 'Strategy': 3.7, 'Indie': 3.6,
            'Horror': 3.9, 'Roguelike': 4.2, 'Metroidvania': 4.1, 'Open World': 4.0,
            'FPS': 3.8, 'Platformer': 3.5, 'Multiplayer': 3.2, 'Co-op': 3.4
        }

    def _init_developer_map(self):
        self.developer_map = {
            "cd projekt": "CD Projekt Red", "ubisoft": "Ubisoft", "electronic arts": "EA",
            "valve": "Valve", "bethesda": "Bethesda", "rockstar": "Rockstar",
            "naughty dog": "Naughty Dog", "fromsoftware": "FromSoftware", "capcom": "Capcom",
            "square enix": "Square Enix", "nintendo": "Nintendo", "sega": "Sega",
            "bioware": "BioWare", "blizzard": "Blizzard", "obsidian": "Obsidian",
            "bandai namco": "Bandai Namco", "activision": "Activision", "2k": "2K Games",
            "paradox": "Paradox Interactive", "devolver": "Devolver Digital",
            "re-logic": "Re-Logic", "concernedape": "ConcernedApe"
        }

    def _init_series_patterns(self):
        self.series_patterns = {
            r'witcher': "The Witcher", r'assassin.?s creed': "Assassin's Creed",
            r'dark souls|elden ring': "Souls", r'elder scrolls|skyrim': "The Elder Scrolls",
            r'gta|grand theft auto': "GTA", r'call of duty': "CoD",
            r'final fantasy': "Final Fantasy", r'resident evil': "Resident Evil",
            r'god of war': "God of War", r'persona': "Persona", r'yakuza': "Yakuza",
            r'mass effect': "Mass Effect", r'fallout': "Fallout", r'civilization': "Civilization",
            r'borderlands': "Borderlands", r'bioshock': "BioShock", r'far cry': "Far Cry",
            r'tomb raider': "Tomb Raider", r'hitman': "Hitman", r'doom': "Doom",
            r'terraria': "Terraria", r'stardew valley': "Stardew Valley"
        }

    def _init_enhanced_keywords(self):
        self.gameplay_keywords = [
            "open world", "turn-based", "fps", "rpg", "co-op", "multiplayer", "survival",
            "roguelike", "battle royale", "sandbox", "stealth", "crafting", "physics",
            "hack and slash", "point and click", "real-time strategy", "tower defense",
            "puzzle", "visual novel", "card game", "deckbuilding", "rhythm", "management",
            "base building", "exploration", "parkour", "permadeath", "looter shooter"
        ]
        self.theme_keywords = [
            "fantasy", "sci-fi", "horror", "cyberpunk", "medieval", "post-apocalyptic",
            "anime", "mystery", "war", "space", "zombies", "detective", "funny",
            "dystopian", "lovecraftian", "western", "pirates", "vampire", "noir",
            "mythology", "superhero", "historical", "military", "futuristic"
        ]
    
    def _init_visual_keywords(self):
        self.visual_keywords = [
            "pixel art", "voxel", "low poly", "realistic", "anime", "cartoon", 
            "hand-drawn", "isometric", "top-down", "first-person", "third-person", 
            "2d", "3d", "vr", "retro", "minimalist", "noir", "colorful", "dark", 
            "atmospheric", "stylized", "cinematic", "text-based"
        ]

GameRecommender = OptimizedGameRecommender
