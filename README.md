# 🎮 GameHorizon — Neural Discovery Engine

[![Status](https://img.shields.io/badge/Status-Active_Development-yellow?style=flat-square)](https://github.com/DioBey7/GameHorizon)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Backend](https://img.shields.io/badge/Backend-Flask_2.3-green?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![AI/ML](https://img.shields.io/badge/AI%2FML-PyTorch_FAISS-orange?style=flat-square&logo=pytorch)](https://pytorch.org/)
[![Frontend](https://img.shields.io/badge/Frontend-Vanilla_JS_PWA-purple?style=flat-square&logo=javascript)](https://developer.mozilla.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)](LICENSE)

**GameHorizon**, oyun açıklamaları, metagenlerler ve kullanıcı etiketleri üzerinden **120-boyutlu vektör uzayında semantik analizler** ve **hibrit skorlama algoritmaları** kullanarak oyunculara kişiselleştirilmiş oyun önerileri sunan, **yapay zeka destekli bir oyun keşif motorudur**.

Sistem, TF-IDF vektörizasyon, Truncated SVD ile boyut indirgeme, FAISS vektör arama indexleme ve çok katmanlı benzerlik metrikleriyle birleştirerek, klasik tag eşleştirmesinin ötesine geçen **semantik anlam tabanında** öneriler sunmaktadır.

---

## 📊 Sistem Özellikleri

### 🧠 İleri Vektör Teknolojileri
- **120-boyutlu Latent Semantic Analysis (LSA)**: TF-IDF + Truncated SVD ile metin-tabanlı vektörleştirme
- **FAISS Indexleme**: O(1) yaklaşık en-yakın-komşu araması 90k+ oyun üzerinde
- **SentenceTransformers Embedding**: Oyun adlarının anlamsal benzerliği için all-MiniLM-L6-v2 modeli
- **Hibrit Skorlama**: Vektör benzerliği + 6 bağımsız faktör (tür, oynanış, görsel stil, kalite, popülerlik)

### 🎯 Akıllı Filtreleme ve Kalibrasyonu
- **Dinamik Ağırlık Motoru**: İstemci-tarafı kaydırıcılarla gerçek zamanlı ağırlık ayarlaması
  - Görsel Stil & Sanat: 0-100%
  - Oynanış Mekaniği: 0-100%
  - Karakteristik Tür: 0-100%
  - Genel Kalite Skoru: 0-100%
  - Global Popülerlik: 0-100%
- **Gelişmiş Filtreler**:
  - Tür tabanlı filtreleme (pozitif ve negatif)
  - Maksimum fiyat limitlemesi
  - Bağımsız yapım (Indie) filtresi
  - Dil ve platform desteği filtreleri

### 📈 Yüksek Performans & Ölçeklenebilirlik
- **Latency**: ~50-150ms ortalama API yanıt süresi
- **Throughput**: 60 req/min limitlemesi (özelleştirilebilir)
- **Paralel İşleme**: Veri yükleme sırasında multi-threading
- **Caching**: Autocomplete ve statik varlıklar için 300s TTL
- **Bellek Optimizasyonu**: Float32 matrisler, MMAP SQLite, WAL mode

### 🎨 Modern Frontend Deneyimi
- **Responsive Glassmorphism UI**: Neon siyber estetik, Turkish Typography
- **PWA Desteği**: Offline kullanım, installable web app
- **Interaktif Radar Grafikleri**: Chart.js ile dinamik analiz görselleştirmesi
- **Gerçek Zamanlı Autocomplete**: Debounced arama önerileri
- **Sintetik Ses Geri Bildirimi**: Web Audio API ile kullanıcı etkileşimi sesleri

### 🔐 Sistem Sağlamlığı
- **CORS Desteği**: Cross-origin istekleri güvenli şekilde işleme
- **Rate Limiting**: DDoS koruması ve API kötüye kullanım önleme
- **Error Handling**: Graceful degradation ve user-friendly hata mesajları
- **Logging**: Structured logging (INFO, ERROR seviyeleri)

---

## 🏗️ Teknolojik Altyapı

### Backend Stack
| Teknoloji | Versiyon | Amaç |
|-----------|---------|------|
| **Flask** | 2.3.3 | Web framework |
| **FAISS** | 1.7.4 | Vektör indexleme ve arama |
| **Scikit-learn** | 1.3.0 | TF-IDF, SVD, metrikleri |
| **Sentence-Transformers** | 2.2.2 | Adı embedding'i |
| **PyTorch** | 2.1.0 | NLP model altyapısı |
| **Pandas** | 2.1.1 | Veri işleme |
| **SQLite** | 3.x | Veri depolaması (FTS5 eklentisi) |

### Frontend Stack
| Teknoloji | Amaç |
|-----------|------|
| **Vanilla JavaScript (ES6+)** | İnteraktif UI mantığı |
| **Chart.js** | Radar grafikleri |
| **CSS3 (Glassmorphism)** | Modern UI tasarımı |
| **Service Worker** | PWA ve offline desteği |
| **Web Audio API** | Sintetik ses geri bildirimi |

### DevOps & Deployment
- **Docker**: Multi-stage build, gunicorn worker pool
- **docker-compose**: Sürüm kontrollü deployment
- **Flask-Limiter**: In-memory rate limiting
- **Flask-Caching**: SimpleCache TTL yönetimi

---

## 🚀 Hızlı Başlangıç

### Gereksinimler
- **Python 3.10+**
- **8GB RAM** (minimum; 16GB önerilir)
- **2GB disk** (veritabanı + modeller)
- **Modern tarayıcı** (Chrome/Firefox/Edge)

### 1️⃣ Depoyu Klonlayın

```bash
git clone https://github.com/DioBey7/GameHorizon.git
cd GameHorizon
```

### 2️⃣ Sanal Ortam Oluşturun

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Bağımlılıkları Yükleyin

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Platforma Özel Notlar:**

- **GPU Desteği** (opsiyonel): PyTorch CPU yerine GPU için değiştirmek istiyorsanız:
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
  ```

- **macOS** (Apple Silicon): FAISS kurulumunda sorun yaşarsanız:
  ```bash
  pip install faiss-cpu  # homebrew tarafından derlenmiş versiyon daha stabil olabilir
  ```

- **Linux** (OpenBLAS eksikse):
  ```bash
  sudo apt-get install libopenblas-dev libomp-dev
  ```

### 4️⃣ Veri Setini Hazırlayın

**Veri kaynağı**: [Kaggle - Steam Games Dataset](https://www.kaggle.com/datasets/nikdavis/steam-store-games)

1. Kaggle'dan `steam.json` veya benzer bir Steam dataset'i indirin
2. Proje kök dizinine `games.json` olarak kaydedin
3. Veritabanını ETL ile doldur:

```bash
python database.py games.json
```

**İşlem süresi**: Dataset boyutuna göre 5-30 dakika (90k oyun için ~15 dakika)

**Alternatif** (test amaçlı): Küçük örnek veri seti kullanabilirsiniz. Bu durumda önerilerin kalitesi düşük olacağını unutmayın.

### 5️⃣ Modeli Oluşturun (İlk Kurulum)

```bash
python -c "from model import GameRecommender; from config import Config; r = GameRecommender(Config); r.initialize(force_rebuild=True)"
```

Bu işlem:
- TF-IDF vektörizasyonunu yürütür
- SVD boyut indirgeme yapar
- FAISS indexini oluşturur
- Adı embedding'lerini hesaplar
- Modeli `models/artifacts.joblib` içine kaydeder

### 6️⃣ Uygulamayı Çalıştırın

#### Geliştirme Modu
```bash
python app.py
```

Tarayıcıda açın: **http://localhost:5000**

#### Production Modu (Docker)
```bash
docker-compose up -d
```

Uygulama **http://0.0.0.0:5000** adresinde dinlemeye başlar.

---

## 📡 API Referansı

### Health Check
```http
GET /api/health
```

**Yanıt** (200 OK):
```json
{
  "status": "ready",
  "error": null
}
```

**Yanıt** (503 Service Unavailable):
```json
{
  "status": "initializing",
  "error": "Model loading... please wait"
}
```

---

### Oyun Önerisi (Ana Endpoint)
```http
GET /api/search?q=Elden%20Ring&visual=0.25&tag=0.25&genre=0.10&quality=0.15&popularity=0.10
```

**Query Parametreleri:**

| Parametre | Gerekli | Tip | Açıklama | Örnek |
|-----------|---------|-----|---------|-------|
| `q` | ✅ | string | Referans oyun adı | `Elden Ring` |
| `visual` | ❌ | float[0-1] | Görsel stil ağırlığı | `0.25` |
| `tag` | ❌ | float[0-1] | Oynanış mekaniği ağırlığı | `0.25` |
| `genre` | ❌ | float[0-1] | Tür ağırlığı | `0.10` |
| `quality` | ❌ | float[0-1] | Kalite skoru ağırlığı | `0.15` |
| `popularity` | ❌ | float[0-1] | Popülerlik ağırlığı | `0.10` |
| `genres` | ❌ | string | Pozitif tür filtresi | `Action,RPG` |
| `exclude` | ❌ | string | Negatif tür filtresi | `Sports,Racing` |
| `max_price` | ❌ | float | Maksimum fiyat ($) | `49.99` |
| `is_indie` | ❌ | boolean | Sadece indie oyunlar | `true` |

**Başarılı Yanıt** (200 OK):
```json
{
  "results": [
    {
      "AppID": 1091500,
      "Name": "Hollow Knight: Silksong",
      "ImageURL": "https://cdn.cloudflare.steamstatic.com/steam/apps/1091500/header.jpg",
      "price": 14.99,
      "developer": "Team Cherry",
      "approval_ratio": 97.5,
      "similarity": 0.8734,
      "match_reasons": [
        {
          "code": 1,
          "description": "Görsel Stil"
        },
        {
          "code": 2,
          "description": "Mekanik"
        }
      ],
      "breakdown": {
        "vector": 87,
        "tag": 82,
        "genre": 75,
        "visual": 91,
        "quality": 95,
        "popularity": 88
      }
    }
  ],
  "count": 15,
  "query": "Elden Ring"
}
```

**Hata Yanıtı** (400 Bad Request):
```json
{
  "error": "Missing query parameter"
}
```

---

### Otomatik Tamamlama
```http
GET /api/autocomplete?q=ha
```

**Query Parametreleri:**

| Parametre | Gerekli | Açıklama |
|-----------|---------|---------|
| `q` | ✅ | Arama sorgusu (min 2 karakter) |

**Yanıt** (200 OK):
```json
[
  "Half-Life",
  "Halo: Combat Evolved",
  "Halo 2",
  "Half-Life 2",
  "Hades"
]
```

---

### Sürpriz Öneri
```http
GET /api/surprise
```

Sistem yüksek kaliteli rastgele bir oyunu seçip, onun için öneri listesi oluşturur.

**Yanıt** (200 OK):
```json
{
  "source": {
    "Name": "The Witcher 3: Wild Hunt",
    "AppID": 292030
  },
  "results": [
    {
      "AppID": 203160,
      "Name": "Baldur's Gate 3",
      "similarity": 0.7892,
      ...
    }
  ]
}
```

---

### Kullanıcı Yorumları (Beta)
```http
GET /api/comments?appid=292030
POST /api/comments
```

**POST Gövdesi:**
```json
{
  "appid": 292030,
  "content": "Harika bir oyun, kesinlikle önerilir!"
}
```

---

## 🗂️ Proje Yapısı

```
GameHorizon/
│
├── 🔧 Backend Core
│   ├── app.py                    # Flask sunucu, API endpoints, arkaplan model yükleme
│   ├── model.py                  # Öğrenme motoru: FAISS, SVD, hibrit skorlama (480+ satır)
│   ├── database.py               # ETL pipeline: JSON → SQLite + FTS5
│   ├── config.py                 # Konfigürasyon ve çevre değişkenleri
│   └── evaluate.py               # Model değerlendirme ve benchmark testleri
│
├── 🎨 Frontend Assets
│   ├── templates/
│   │   └── index.html            # Ana sayfa şablonu (Turkish UI)
│   │
│   └── static/
│       ├── style.css             # Glassmorphism CSS, responsive tasarım (1200+ satır)
│       ├── script.js             # İnteraktif UI mantığı, API çağrıları (400+ satır)
│       ├── service-worker.js     # PWA cache stratejisi
│       └── manifest.json         # PWA metadata
│
├── 📦 Deployment
│   ├── docker-compose.yml        # Multi-container orchestration
│   ├── .dockerfile               # Production image (gunicorn)
│   └── requirements.txt          # Python bağımlılıkları (pinned versions)
│
├── 📚 Veri & Modeller
│   ├── games.json                # (User-provided) Steam dataset
│   ├── games.db                  # SQLite database (auto-generated)
│   └── models/
│       ├── artifacts.joblib      # Trained model: LSA matrix, embeddings (auto-generated)
│       └── ...
│
└── 📖 Dokümantasyon
    ├── README.md                 # Bu dosya
    ├── LICENSE                   # MIT License
    └── .gitignore               # Git ignore patterns
```

**Dosya Boyutları (Orta Set için):**
- `games.db`: ~150-200MB (90k oyun)
- `artifacts.joblib`: ~250-300MB (LSA + embeddings)
- `static/`: ~1.5MB (CSS + JS + icons)

---

## 🧠 Teknik Derinlik

### Skorlama Algoritması

Her oyun için altı faktörden oluşan hibrit skor hesaplanır:

```
final_score = (w_vec × vec_similarity + 
               w_tag × tag_jaccard + 
               w_genre × genre_jaccard + 
               w_visual × visual_jaccard + 
               w_quality × quality_score + 
               w_popularity × popularity_score) / Σ_weights

Kısıtlama: final_score ∈ [0, 1]
```

**Faktörlerin Açıklaması:**

1. **vec_similarity** (Semantik Benzerlik)
   - LSA vektörü arasındaki Euclidean mesafesi
   - 120-boyutlu uzayda FAISS ile hesaplanan
   - Formül: `max(0, 1 - dist/1.4)`

2. **tag_jaccard** (Oynanış Mekaniği)
   - Oyun etiketlerinin Jaccard benzerliği
   - `|A ∩ B| / |A ∪ B|`

3. **genre_jaccard** (Tür Benzerliği)
   - Tür listelerinin Jaccard benzerliği
   - Küçük harfe dönüştürülerek karşılaştırılır

4. **visual_jaccard** (Görsel Stil)
   - Görsel etiketlerinin kesişimi
   - Örn: pixel-art, realistic, 2D, 3D, vr, anime

5. **quality_score** (Kalite)
   - Bayesian smoothing ile hesaplanan onay oranı
   - Formül: `(positive_votes / (positive_votes + negative_votes)) × 0.7 + (popularity / 100) × 0.3`

6. **popularity_score** (Popülerlik)
   - 0-100 arasında normalize edilmiş oyuncu sayısı
   - Log-scale: `log10(total_players + 1) / 9.0`

### Veri Pipeline

```
steam.json 
    ↓ [database.py]
Stream processing (ijson)
    ↓
Text cleaning (HTML, URL, regex)
    ↓
SQLite INSERT (WAL mode, batch 10k)
    ↓
FTS5 rebuild & optimize
    ↓
games.db (ready for model)
```

### Model İnisyalizasyonu

```
games.db
    ↓ [SELECT * WHERE popularity > 5]
    ↓
Pandas DataFrame (90k rows)
    ↓ [TF-IDF on: genres + tags + description]
    ↓
Sparse matrix (90k × 25k features)
    ↓ [Truncated SVD: 120 components]
    ↓
Dense matrix (90k × 120)
    ↓ [FAISS IndexFlatL2 + normalize]
    ↓
Content FAISS Index (ready)
    ↓ [SentenceTransformers + normalize]
    ↓
Name FAISS Index (HNSW, ready)
    ↓ [joblib dump]
    ↓
artifacts.joblib (cached for restart)
```

---

## 📊 Performans Metrikleri

### Latency Benchmarks (90k oyun dataset)
| İşlem | Ortalama | Max | Min |
|-------|----------|-----|-----|
| Search (15 results) | 85ms | 150ms | 45ms |
| Autocomplete | 12ms | 30ms | 5ms |
| Surprise recommendation | 95ms | 160ms | 55ms |
| Model init (cold start) | 3.2s | - | - |

### Memory Usage
| Bileşen | RAM |
|---------|-----|
| LSA matrix (90k × 120 float32) | ~43MB |
| Name embeddings (90k × 384 float32) | ~138MB |
| DataFrame (metadata) | ~80MB |
| FAISS indexes | ~45MB |
| **Total** | **~310MB** |

### Throughput
- **API Rate Limit**: 1000 req/hour (60 req/minute)
- **Concurrent Connections**: 4 gunicorn workers × 4 threads = 16
- **Database Pragma**: WAL mode, 100k cache size

---

## ⚙️ Konfigürasyon

`config.py` dosyasında tüm parametreler merkezi olarak yönetilir:

```python
# Model Parameters
SVD_COMPONENTS = 120              # LSA boyut indirgeme
FAISS_NLIST = 100                 # Clustering için liste sayısı
FAISS_NPROBE = 10                 # Arama sırasında araştırılacak listeler

# Default Weights (0-1 arasında)
VECTOR_WEIGHT = 0.15
TAG_WEIGHT = 0.25
GENRE_WEIGHT = 0.10
VISUAL_WEIGHT = 0.25
QUALITY_WEIGHT = 0.10
POPULARITY_WEIGHT = 0.10

# Filtering Thresholds
MIN_SIMILARITY = 0.15
MIN_POPULARITY = 5.0

# Database Settings
DB_JOURNAL_MODE = 'WAL'
DB_CACHE_SIZE = 100000
DB_MMAP_SIZE = 134217728
```

**Çevre Değişkenleri** (`.env` dosyasında):
```
ENV=production
DEBUG=False
DB_PATH=games.db
MODEL_PATH=models
API_HOST=0.0.0.0
API_PORT=5000
RATE_LIMIT_PER_HOUR=1000
```

---

## 🐛 Troubleshooting

### Problem: "Model initialization failed"
**Çözüm:**
```bash
# Modeli force rebuild et
python -c "from model import GameRecommender; GameRecommender().initialize(force_rebuild=True)"
```

### Problem: "FAISS import error"
**Çözüm:**
```bash
# CPU versiyonu kur
pip uninstall faiss-gpu faiss
pip install faiss-cpu

# Linux: OpenBLAS eksikse
sudo apt-get install libopenblas-dev
```

### Problem: "Out of memory" hatası
**Çözüm:**
1. SVD component sayısını azalt: `SVD_COMPONENTS = 60`
2. Daha küçük bir dataset kullan
3. Sistem swap'ı artır: `sudo fallocate -l 4G /swapfile`
4. FAISS_NPROBE değerini düşür: `FAISS_NPROBE = 5`

### Problem: "Database locked"
**Çözüm:**
```bash
# WAL checkpoint yap
python -c "import sqlite3; sqlite3.connect('games.db').execute('PRAGMA wal_checkpoint(TRUNCATE)')"
```

### Problem: Autocomplete boş sonuç dönüyor
**Çözüm:**
- Veritabanında FTS5 rebuild et:
```bash
python -c "import sqlite3; conn = sqlite3.connect('games.db'); conn.execute(\"INSERT INTO games_fts(games_fts) VALUES('rebuild')\"); conn.commit()"
```

---

## 🧪 Testing & Evaluation

Sistem performansını test etmek için:

```bash
python evaluate.py
```

Bu script:
- **Latency**: 10 iteration üzerinde ortalama API yanıt süresi
- **Recall@15**: Test setindeki oyunların ne kadarı bulunduğu
- **Weight Variance**: Farklı ağırlık konfigürasyonlarındaki sonuçları karşılaştırır

**Örnek Output:**
```
EVALUATION REPORT
==================================================
{
  "Performance_Metrics": {
    "avg_latency_ms": 87.34,
    "max_latency_ms": 155.21,
    "min_latency_ms": 43.18
  },
  "Quality_Recall_At_15_Percent": 92.5,
  "Weight_Variance_Test_Cyberpunk_2077": {
    "default": ["The Witcher 3", ...],
    "pure_visual": ["Doom", ...],
    "pure_mechanic": ["Dark Souls III", ...]
  }
}
```

---

## 🔐 Güvenlik Best Practices

1. **Input Validation**
   - Tüm query parametreleri sanitize edilir
   - SQLi koruması: prepared statements
   - XSS koruması: HTML escape

2. **Rate Limiting**
   - Flask-Limiter ile 60 req/minute
   - IP-based rate limiting

3. **CORS Policy**
   - Sadece belirlenen origins'den istekler
   - Credentials opsiyonel

4. **Error Disclosure**
   - Production'da stack trace saklanır
   - Generic error messages

---

## 🚢 Deployment

### Docker ile (Önerilen)

```bash
docker-compose up -d
```

**Dockerfile özellikleri:**
- Multi-stage build (optimize edilmiş image)
- gunicorn 4 worker pool
- 120s timeout
- Health check

### Manual Deployment (VPS/Sunucu)

```bash
# 1. Dependencies yükle
pip install -r requirements.txt

# 2. Modeli ön-yükle
python -c "from model import GameRecommender; GameRecommender().initialize()"

# 3. Gunicorn ile başlat
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app

# 4. Nginx proxy (opsiyonel)
# upstream gamehorizon { server 127.0.0.1:5000; }
# server { listen 80; proxy_pass http://gamehorizon; }
```

### Environment Variables (Production)
```
ENV=production
DEBUG=False
API_HOST=0.0.0.0
API_PORT=5000
RATE_LIMIT_PER_HOUR=2000
CACHE_TIMEOUT=600
```

---

## 📈 Roadmap

### v2.6 (Planlı)
- [ ] Kullanıcı hesapları ve OAuth (Steam/Discord)
- [ ] Server-side favori senkronizasyonu
- [ ] Dinamik LLM-based açıklamalar (GPT-mini)
- [ ] Real-time price tracking ve indirim alerts

### v2.7+
- [ ] Kullanıcı-tabanlı işbirlikçi filtreleme (CF)
- [ ] Fine-tuned BERT modeli (sektör-spesifik)
- [ ] Grafik veritabanı (Neo4j) ile ilişki analizi
- [ ] Mobile native uygulaması (React Native)

---

## 📝 Lisans

Bu proje **MIT Lisansı** altında lisanslanmıştır.
Eğitim, araştırma ve portfolyo projelerine açıktır.

**Sorumluluk Reddi**: Steam data'sının kullanımı Steam ToS'une tabi olabilir.
Ticari kullanım için Steam ile iletişime geçin.

---

## 🤝 Katkıda Bulunma

Katkılara açığız! Lütfen şu adımları izleyin:

1. **Fork** depoyu
2. **Feature branch** oluştur: `git checkout -b feature/amazing-feature`
3. **Commit** yap: `git commit -m 'Add amazing feature'`
4. **Push** yap: `git push origin feature/amazing-feature`
5. **Pull Request** aç

**Beklentiler:**
- PEP8 kod formatı
- Unit tests (kritik yollar için)
- Detaylı commit mesajları
- Docstrings (Python) / JSDoc (JavaScript)

---

## 👨‍💻 Yazarlar

**DioBey7** - [GitHub Profili](https://github.com/DioBey7)

- 🧠 ML/AI Pipeline Tasarımı
- 🎨 Frontend UI/UX
- 🔧 DevOps & Deployment

---

## 💬 İletişim & Destek

- **Issues**: [GitHub Issues](https://github.com/DioBey7/GameHorizon/issues) - Hata bildirimleri ve feature istekleri
- **Discussions**: [GitHub Discussions](https://github.com/DioBey7/GameHorizon/discussions) - Teknik sorular ve tartışmalar
- **Email**: [Profil üzerinden](https://github.com/DioBey7)

---

## 🙏 Teşekkürler

- **SentenceTransformers** ekibine (Hugging Face)
- **FAISS** geliştiricilerine (Meta/Facebook)
- **Kaggle** Steam Dataset sağlayıcılarına
- Tüm açık kaynak kütüphanelerin geliştiricilerine

---

**Son Güncelleme**: 2026-05-07 | **Versiyon**: 2.5-neural-discovery | **Durumu**: Active Development ✅
