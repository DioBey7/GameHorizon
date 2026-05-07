import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.getenv('ENV', 'production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, os.getenv('DB_PATH', 'games.db'))
    MODEL_PATH = os.path.join(BASE_DIR, os.getenv('MODEL_PATH', 'models'))
    ARTIFACTS_PATH = os.path.join(MODEL_PATH, 'artifacts.joblib')
    
    DB_JOURNAL_MODE = 'WAL'
    DB_CACHE_SIZE = 100000
    DB_MMAP_SIZE = 134217728
    
    MIN_SIMILARITY = 0.15
    MIN_POPULARITY = 5.0
    RECOMMENDATION_COUNT = 15
    
    SVD_COMPONENTS = 120
    FAISS_NLIST = 100
    FAISS_NPROBE = 10
    FAISS_M_CONTENT = 12
    
    VECTOR_WEIGHT = 0.15
    TAG_WEIGHT = 0.25
    GENRE_WEIGHT = 0.10
    VISUAL_WEIGHT = 0.25
    QUALITY_WEIGHT = 0.10
    PLAYTIME_WEIGHT = 0.05
    ERA_WEIGHT = 0.10
    
    SERIES_BONUS = 0.15
    DEVELOPER_BONUS = 0.10
    SAME_VISUAL_STYLE_BONUS = 0.20
    
    BAYESIAN_PRIOR_WEIGHT = 10.0
    BAYESIAN_PRIOR_MEAN = 0.5
    
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    RATE_LIMIT_PER_HOUR = 1000