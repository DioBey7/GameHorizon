# 🎮 GameHorizon — Yapay Zeka Destekli Oyun Keşif Platformu

![Status](https://img.shields.io/badge/Status-Geliştirme_Aşamasında-yellow)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Backend](https://img.shields.io/badge/Backend-Flask-green)
![AI](https://img.shields.io/badge/AI-PyTorch_%26_FAISS-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

GameHorizon, oyun açıklamaları, etiketler ve meta veriler üzerinden hem semantik (embedding / vektör) hem de kural tabanlı (tür, fiyat, geliştirici vb.) analizler yaparak oyunculara "neden" bir oyunun önerildiğini açıklayan hibrit bir oyun öneri motorudur. Amacımız klasik anahtar kelime/tür eşleşmesinin ötesine geçerek oyun deneyiminin ruhuna yakın öneriler sunmaktır.

## Öne çıkan özellikler
- Vektör tabanlı anlamsal arama (SentenceTransformers)
- FAISS ile yüksek hızlı vektör arama
- Hibrit skorlama: vektör benzerliği + tür, oynanış, fiyat, popülerlik vb.
- Çoklu oyun araması (örn. "Skyrim + Stardew Valley")
- Gelişmiş filtreleme ve negatif filtreleme (exclusion)
- Radar grafiklerle öneri kırılımı (ön yüz tarafında Chart.js)
- PWA desteği, favoriler ve arama geçmişi (frontend tarafında localStorage)

## İçindekiler
- Teknolojiler
- Hızlı başlama
- Veri hazırlama (games.json → SQLite)
- Uygulamayı çalıştırma (dev)
- API referansı (örnek istek/cevap)
- Yapı & bileşenler
- Yaygın problemler ve çözüm önerileri
- Katkı ve lisans

---

## Teknolojik altyapı (kısa)
- Backend: Flask, Flask-Caching, Flask-Limiter
- NLP / Embedding: sentence-transformers (all-MiniLM-L6-v2)
- Vektör arama: FAISS (faiss-cpu)
- Veri işleme: pandas, scikit-learn (TF-IDF, SVD)
- Depolama: SQLite (+ FTS5)
- Frontend: Vanilla JS, Chart.js, modern responsive CSS (glassmorphism)
- Diğer: PyTorch (CPU / opsiyonel GPU)

Not: Model eğitimi / vektör oluşturma CPU üzerinde çalışacak şekilde ayarlandı ama büyük veri setlerinde (90k oyun civarı) CPU belleği sınırları ve süre göz önünde bulundurulmalıdır. Eğer GPU kullanacaksanız PyTorch GPU sürümünü ve uygun sentence-transformers ayarlarını tercih edin.

---

### Hızlı Başlangıç (local)
1) Depoyu klonlayın
git clone https://github.com/DioBey7/GameHorizon.git
cd GameHorizon

2) Python sanal ortamı oluşturun ve aktifleştirin
#### Windows
python -m venv venv
venv\Scripts\activate

#### macOS / Linux
python3 -m venv venv
source venv/bin/activate

3) Bağımlılıkları yükleyin
pip install -r requirements.txt

Notlar:
- PyTorch için CPU/GPU uyumlu tekerlekleri kullanın. requirements.txt içinde PyTorch satırı platforma göre (CPU/GPU) el ile ayarlanmış olabilir. Eğer yükleme sorunları yaşarsanız PyTorch'un resmi talimatlarını (https://pytorch.org/) takip edin.
- FAISS kurulumunda bazı platformlarda ilave paketler gerekebilir (ör. libopenblas). Hata alırsanız sistem paket yöneticinizle gerekli kütüphaneleri kurun.

4) Veri setini hazırlayın (games.json)
- GitHub deposuna büyük veri setleri eklenmediği için orijinal Steam dataset'ini (ör. Kaggle) manuel indirin.
- İndirilen JSON dosyasını proje köküne koyun ve `games.json` olarak adlandırın.
- Eğer dataset tek büyük bir JSON nesnesiyse, database.py içerisinde otomatik dönüştürme/stream işlevleri kullanılıyor. Aksi durumlarda README altındaki "Veri hazırlama detayları"na bakın.

5) Veritabanını oluşturma (ETL)
- Olası adımlar:
    python database.py
  Bu script games.json → satır bazlı stream formatına çevirir ve SQLite veritabanını (games.db) doldurur.
- Alternatif: Eğer sadece test etmek istiyorsanız küçük bir örnek JSON ile başlayın.

6) Uygulamayı başlatma (geliştirme)
python app.py

- Ana sayfa: http://localhost:5000
- İlk çalıştırmada backend arkaplanda modeli yükleyip (SVD, FAISS, isim-embedding) hazırlayacaktır. Bu işlem dataset boyutuna göre 1–5 dakika alabilir.

---

## Veri hazırlama - Detaylar
- database.py:
  - games.json → (gerekirse) satır-bazlı "stream" formatına dönüştürülür.
  - Kayıtlar işlenip SQLite `games` tablosuna yazılır (FTS5 ile arama tablosu da doldurulur).
  - Büyük dosyalar için paralel işleme ve batch yazma kullanır; sistem belleğine dikkat edin.
- Eğer bellek sınırı yaşıyorsanız:
  - BATCH_SIZE ve MAX_WORKERS değerlerini env/config ile azaltın.
  - Sistem swap/ram ayarlarını kontrol edin.

---

## API - Örnekler
Tüm endpointler JSON döner. Örnek adres: http://localhost:5000

1) Sağlık kontrolü
GET /api/health
Response:
{
  "status": "initializing" | "ready",
  "error": null | "message",
  "message": "Sistem yükleniyor..." | "Sistem aktif"
}

2) Arama (öneriler)
GET /api/search?q=Halo
İsteğe bağlı query parametreleri:
- genres: "Action,RPG" (virgülle ayrılmış)
- exclude: "Sports,Racing"
- year_min, year_max, playtime_min, playtime_max

Response:
```text
{
  "results": [
    {
      "AppID": 12345,
      "Name": "Örnek Oyun",
      "ImageURL": "https://...",
      "genres": ["Action", "Adventure"],
      "price": 9.99,
      "SteamURL": "https://store.steampowered.com/app/12345",
      "similarity": 0.8534,
      "match_reasons": [{"code": 1, "description": "Benzer tür"}, ...],
      "primary_match": 1,
      "explanation": "Similarity Match",
      "breakdown": {"genre": 85, "gameplay": 60, "theme": 40, "price": 90, "visual": 77, "popularity": 82},
      "year": "2017",
      "playtime": 720,
      "popularity_score": 82.5
    }
  ],
  "count": 1,
  "query": "Halo"
}
```
3) Otomatik Tamamlama
GET /api/autocomplete?q=hal
Response: ["Halo: Combat Evolved", "Halo 2", "Half-Life"]

4) Sürpriz öneri (random seçilmiş yüksek puanlı oyuna göre)
GET /api/surprise

Response:
```text
{
  "source": {"Name": "Kaynak Oyun", "AppID": 12345},
  "results": [ ... aynı formatta öneriler ... ]
}
```
---

## Önemli notlar / Tavsiyeler
- İlk model inisyalizasyonu: app.py, arka planda bir thread ile modeli yükler. Eğer `init_done` false ise API 503 dönebilir; bekleyin.
- Bellek: tamsayı (float32) matrisler ve FAISS indeksi bellek tüketir. Büyük dataset'lerde swap/OutOfMemory riskine karşı DB filtrelerini veya SVD bileşen sayısını düşürün.
- PyTorch & FAISS: platforma göre uyumlu tekerlekleri kullanın. faiss-cpu genellikle Linux'ta daha sorunsuzdur; Windows için ek adım gerekebilir.
- requirements.txt içinde tekrarlamalar/sürüm karışıklıkları olabilir — paketleri kurarken hata alırsanız requirements'ı el ile düzenleyin (özellikle torch/torchvision satırı).

## Yaygın hatalar ve çözümler
- "Veritabanı bulunamadı": games.db yok — önce database.py ile veriyi yükleyin.
- "FAISS import hata": doğru faiss paketini kurduğunuzdan emin olun (faiss-cpu vs faiss-gpu).
- "SentenceTransformer model indirilemiyor": internet bağlantısı veya firewall; manuel indirme seçeneklerini değerlendirin.
- "Bellek uyarıları/çökme": BATCH_SIZE, MAX_WORKERS, SVD_COMPONENTS azaltın; fiziksel RAM artırın veya swap kullanın.

## Proje yapısı (kısa)
```text
GameHorizon/
├── app.py              # Flask sunucusu, arka plan model yüklemesi ve API
├── model.py            # Öneri mantığı, embedding, FAISS ve skor hesaplama
├── database.py         # ETL: games.json -> games.db (SQLite + FTS5)
├── config.py           # Konfigürasyon, çevre değişkenleri, varsayılanlar
├── requirements.txt    # Python bağımlılıkları
├── games.json          # (Manuel Eklenmeli) Kaynak veri seti
├── static/             # Frontend varlıkları (CSS, JS, manifest)
│   ├── style.css
│   ├── script.js
│   └── manifest.json
└── templates/          # HTML şablonları
    └── index.html
```

## Geliştirilecekler (Roadmap)
- Kullanıcı hesapları ve sunucu tarafı favori senkronizasyonu
- Kullanıcı-temelli işbirlikçi filtreleme
- Steam OAuth / kütüphane içe aktarma
- Canlı fiyat takibi & indirim bildirimleri
- Daha ayrıntılı model monitoringi ve A/B testleri

## Katkıda bulunma
1. Fork -> feature branch -> PR
2. Kod formatı (PEP8), anlamlı commit mesajları
3. Büyük değişiklikler için önce issue açın ve tasarım tartışması yapın

## Lisans
MIT — eğitim ve portfolyo amaçlı.

## İletişim
Projeyle ilgili sorular, hata bildirimleri veya katkı istekleri için GitHub Issues kısmını kullanabilirsiniz.

---

