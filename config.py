# Dinamik ağırlıkların; API, model eğitimi gibi ayarların ve parametrelerin belirlendiği config.py dosyası.
import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

class Config:
    
    ENV = os.getenv('ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, os.getenv('DB_PATH', 'games.db'))
    MODEL_PATH = os.path.join(BASE_DIR, os.getenv('MODEL_PATH', 'models'))
    CACHE_DIR = os.path.join(BASE_DIR, os.getenv('CACHE_DIR', 'image_cache'))
    LOG_DIR = os.path.join(BASE_DIR, os.getenv('LOG_DIR', 'logs'))
    
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
    
    
    MIN_SIMILARITY = float(os.getenv('MIN_SIMILARITY', 0.12))
    MIN_POPULARITY = float(os.getenv('MIN_POPULARITY', 8))
    RECOMMENDATION_COUNT = int(os.getenv('RECOMMENDATION_COUNT', 15))
    SVD_COMPONENTS = int(os.getenv('SVD_COMPONENTS', 120))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 5000))
    MAX_RECOMMENDATIONS = int(os.getenv('MAX_RECOMMENDATIONS', 250))
    
    
    GENRE_WEIGHT = float(os.getenv('GENRE_WEIGHT', 0.20))
    GAMEPLAY_WEIGHT = float(os.getenv('GAMEPLAY_WEIGHT', 0.18))
    THEME_WEIGHT = float(os.getenv('THEME_WEIGHT', 0.16))
    PRICE_WEIGHT = float(os.getenv('PRICE_WEIGHT', 0.08))
    VISUAL_WEIGHT = float(os.getenv('VISUAL_WEIGHT', 0.14))
    DESCRIPTION_WEIGHT = float(os.getenv('DESCRIPTION_WEIGHT', 0.15))
    TAG_WEIGHT = float(os.getenv('TAG_WEIGHT', 0.16))
    CATEGORY_WEIGHT = float(os.getenv('CATEGORY_WEIGHT', 0.08))
    
    
    RARE_GENRE_BONUS = float(os.getenv('RARE_GENRE_BONUS', 0.06))
    VISUAL_STYLE_BONUS = float(os.getenv('VISUAL_STYLE_BONUS', 0.05))
    SERIES_BONUS = float(os.getenv('SERIES_BONUS', 0.08))
    DEVELOPER_BONUS = float(os.getenv('DEVELOPER_BONUS', 0.07))
    
    
    EXCLUSION_PENALTY = float(os.getenv('EXCLUSION_PENALTY', -0.15))
    MIN_EXCLUSION_MATCH = float(os.getenv('MIN_EXCLUSION_MATCH', 0.40)) 
    
    
    PROCESS_IMAGES = os.getenv('PROCESS_IMAGES', 'False').lower() == 'true'
    PROCESS_SCREENSHOTS = os.getenv('PROCESS_SCREENSHOTS', 'False').lower() == 'true'
    MAX_IMAGE_WORKERS = int(os.getenv('MAX_IMAGE_WORKERS', 4))
    IMAGE_DOWNLOAD_TIMEOUT = int(os.getenv('IMAGE_DOWNLOAD_TIMEOUT', 15))
    MAX_SCREENSHOTS = int(os.getenv('MAX_SCREENSHOTS', 3))
    
    
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    API_THREADS = int(os.getenv('API_THREADS', 8))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', 300))
    
    
    DB_CACHE_SIZE = int(os.getenv('DB_CACHE_SIZE', 2000000))
    DB_JOURNAL_MODE = os.getenv('DB_JOURNAL_MODE', 'WAL')
    DB_SYNCHRONOUS = os.getenv('DB_SYNCHRONOUS', 'NORMAL')
    DB_MMAP_SIZE = int(os.getenv('DB_MMAP_SIZE', 268435456))
    CLEAN_CACHE_ON_START = os.getenv('CLEAN_CACHE_ON_START', 'False').lower() == 'true'
    
    
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))
    CACHE_THRESHOLD = int(os.getenv('CACHE_THRESHOLD', 50000))
    
    
    BAYESIAN_PRIOR_WEIGHT = int(os.getenv('BAYESIAN_PRIOR_WEIGHT', 15))
    BAYESIAN_PRIOR_MEAN = float(os.getenv('BAYESIAN_PRIOR_MEAN', 0.6))

<<<<<<< HEAD

=======
    
>>>>>>> cdbd22f7fbdc20f081bee3139c5a9d5fa1f59fee
    FAISS_NLIST = int(os.getenv('FAISS_NLIST', 100))
    FAISS_NPROBE = int(os.getenv('FAISS_NPROBE', 10))
    MIN_FAISS_SAMPLES = int(os.getenv('MIN_FAISS_SAMPLES', 1000))
    
    
    CONTENT_BLACKLIST = [
        "hitler", "nazi", "racist", "sexist", "hate speech",
        "adolf", "supremacist", "hentai", "explicit", "nsfw", "porn"
    ]
    
    
    LOW_QUALITY_INDICATORS = [
        "asset flip", "low effort", "cash grab", "clicker", "idle game",
        "quick money", "reskin", "poor quality", "bad reviews"
    ]
    
<<<<<<< HEAD

    MODEL_INIT_TIMEOUT = int(os.getenv('MODEL_INIT_TIMEOUT', 300))
    MODEL_RETRY_ATTEMPTS = int(os.getenv('MODEL_RETRY_ATTEMPTS', 3))
    
    
    PRICE_QUOTA = {'low': 5, 'mid': 4, 'high': 3}
    PRICE_BRACKETS = {'low': (0, 9.99), 'mid': (10, 29.99), 'high': (30, float('inf'))}
    
    
=======
    
    MODEL_INIT_TIMEOUT = int(os.getenv('MODEL_INIT_TIMEOUT', 300))
    MODEL_RETRY_ATTEMPTS = int(os.getenv('MODEL_RETRY_ATTEMPTS', 3))
    

    PRICE_QUOTA = {'low': 5, 'mid': 4, 'high': 3}
    PRICE_BRACKETS = {'low': (0, 9.99), 'mid': (10, 29.99), 'high': (30, float('inf'))}
    
 
>>>>>>> cdbd22f7fbdc20f081bee3139c5a9d5fa1f59fee
    MAX_DEVELOPER_RECOMMENDATIONS = 3
    

    RARE_GENRES = {
        "Visual Novel", "Psychological Horror", "Walking Simulator", 
        "Interactive Fiction", "Metroidvania", "Roguelike", "Bullet Hell",
        "Text-Based", "Rhythm", "Music", "Educational", "VR" , "Soulslike",
        "Immersive Sim", "Grand Strategy", "4X", "Analog Horror", "Steampunk",
        "Rich Story"
    }

    
    AVAILABLE_GENRES = [
        "Action", "Adventure", "RPG", "Strategy", "Simulation", "Sports", "Racing",
        "Indie", "Casual", "Puzzle", "Horror", "Platformer", "Shooter", "Fighting",
        "Visual Novel", "Roguelike", "Metroidvania", "Open World", "Sandbox",
        "Survival", "Battle Royale", "MOBA", "MMO", "Card Game", "Board Game",
        "Educational", "VR", "Anime", "Fantasy", "Sci-Fi", "Cyberpunk", "Steampunk",
        "Post-apocalyptic", "Medieval", "Historical", "Space", "Zombies", "Mystery",
        "Detective", "Thriller", "Comedy", "Drama", "Romance", "War", "Western",
        "Superhero", "Mythology", "Pixel Art", "Low Poly", "Realistic" , "2D", "3D",
        "Retro", "Memes" , "Rich Story" , "Funny", "Important Choices"
    ]

    @classmethod
    def validate(cls) -> bool:
        """Config değerlerini doğrula"""
        errors = []
        
        
        db_dir = os.path.dirname(os.path.abspath(cls.DB_PATH)) or '.'
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception as e:
                errors.append(f"Veritabanı dizini oluşturulamadı: {db_dir}, hata: {e}")
        
        
        if not os.path.exists(cls.MODEL_PATH):
            try:
                os.makedirs(cls.MODEL_PATH, exist_ok=True)
            except Exception as e:
                errors.append(f"Model dizini oluşturulamadı: {cls.MODEL_PATH}, hata: {e}")
        
        
        if cls.LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            errors.append(f"Geçersiz LOG_LEVEL: {cls.LOG_LEVEL}")

        
<<<<<<< HEAD
        
=======
>>>>>>> cdbd22f7fbdc20f081bee3139c5a9d5fa1f59fee
        weights = [
            cls.GENRE_WEIGHT, cls.GAMEPLAY_WEIGHT, cls.THEME_WEIGHT,
            cls.PRICE_WEIGHT, cls.VISUAL_WEIGHT, cls.DESCRIPTION_WEIGHT,
            cls.TAG_WEIGHT, cls.CATEGORY_WEIGHT
        ]
        total_weight = sum(weights)
        if abs(total_weight - 1.0) > 0.01:
            logging.warning(f"Temel ağırlık toplamı 1.0'dan farklı (şu an: {total_weight:.2f}). Bu durum, bonus ağırlıkların üzerine eklendiği için kabul edilebilir.")
        
        if errors:
            for error in errors:
                logging.error(error)
            return False
        return True
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Config değerlerini dictionary olarak döndür"""
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith('_') and not callable(getattr(cls, attr))
        }
    
    @classmethod
    def log_config(cls):
        """Config değerlerini logla"""
        config_dict = cls.to_dict()
        logging.info("Uygulama konfigürasyonu:")
        for key, value in config_dict.items():
            if 'PASSWORD' not in key and 'SECRET' not in key and 'KEY' not in key:
                logging.info(f"  {key}: {value}")


if not Config.validate():
    logging.warning("Config doğrulama hatası - bazı ayarlar default değerlerle çalışacak")

Config.log_config()
