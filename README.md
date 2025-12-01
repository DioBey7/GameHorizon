# 🎮 GameHorizon - Yapay Zeka Destekli Oyun Keşif Platformu

![Status](https://img.shields.io/badge/Status-Geliştirme_Aşamasında-yellow)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Framework](https://img.shields.io/badge/Backend-Flask-green)
![AI](https://img.shields.io/badge/AI-PyTorch_%26_FAISS-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**GameHorizon**, klasik etiket eşleşmesinin ötesine geçerek, oyunların içeriklerini, atmosferlerini ve oyuncu deneyimlerini vektörel uzayda analiz eden **hibrit bir oyun öneri motorudur**.

90.000+ oyunluk Steam veri seti üzerinde çalışan sistem, **Doğal Dil İşleme (NLP)** ve **Vektör Benzerliği (Vector Similarity)** teknolojilerini kullanarak oyunculara "neden" o oyunu sevebileceklerini matematiksel verilerle ve grafiklerle sunar.

---

## 🚀 Öne Çıkan Özellikler

### 🧠 Akıllı Arama & Öneri Motoru
* **Vektör Tabanlı Anlamsal Arama:** Oyun açıklamaları `SentenceTransformers` (BERT tabanlı modeller) ile 384 boyutlu vektörlere dönüştürülür. Sadece isim benzerliği değil, oyunun "ruhunu" ve temasını anlar.
* **Hibrit Skorlama Algoritması:** Öneri puanı tek bir faktöre bağlı değildir; Vektör mesafesi (FAISS), Jaccard Benzerliği (Türler), Fiyat politikası ve Popülarite skorlarının ağırlıklı ortalamasıyla hesaplanır.
* **Çoklu Oyun Analizi (Multi-Game Search):** Kullanıcı birden fazla oyun (Örn: *Skyrim + Stardew Valley*) girdiğinde, sistem bu oyunların vektörlerinin ortalamasını (Mean Pooling) alarak ortak zevke hitap eden kesişim kümesini bulur.

### 📊 Veri Görselleştirme & Analiz
* **Radar Grafikleri (Spider Charts):** Her öneri için Görsel, Tür, Oynanış, Fiyat ve Popülarite eksenlerinde oyunun referans oyuna ne kadar benzediğini görselleştirir.
* **Detaylı Kırılım:** Önerinin neden yapıldığını (örn: "%85 Görsel Benzerlik, %90 Tür Eşleşmesi") şeffaf bir şekilde gösterir.

### 🎨 Modern Kullanıcı Deneyimi
* **Glassmorphism UI:** Modern, şeffaf, estetik ve Responsive (Mobil Uyumlu) arayüz.
* **Gelişmiş Filtreleme:** Yıl aralığı, oynanış süresi (saat), tür dahil etme ve dışlama (Negative Filtering) seçenekleri.
* **Sürpriz Modu:** Yüksek puanlı gizli cevherleri (Hidden Gems) keşfetmenizi sağlayan rastgele öneri motoru.
* **PWA Desteği:** Uygulama mobil cihazlara yüklenebilir.

---

## 🛠️ Teknolojik Altyapı

Bu proje, yüksek performans ve ölçeklenebilirlik için modern teknolojiler kullanılarak geliştirilmiştir:

### Backend (Python)
* **Flask:** Rest API sunucusu ve uygulama iskeleti.
* **PyTorch & SentenceTransformers:** Metin tabanlı verilerin embedding işleminden geçirilmesi (`all-MiniLM-L6-v2` modeli).
* **FAISS (Facebook AI Similarity Search):** Milyonlarca vektör arasında milisaniyeler içinde benzerlik araması yapmak için Product Quantization (PQ) optimizasyonu ile kullanılır.
* **Scikit-learn:** TF-IDF ve SVD (Latent Semantic Analysis) işlemleri için.
* **SQLite (FTS5):** Metadataların saklanması ve Full-Text Search optimizasyonu.
* **Pandas & NumPy:** Büyük veri setinin manipülasyonu ve matris işlemleri (Float16 optimizasyonu ile).

### Frontend
* **HTML5 & CSS3:** Responsive Grid yapısı ve Glassmorphism tasarım dili.
* **Vanilla JavaScript (ES6+):** SPA (Single Page Application) mantığında asenkron veri yönetimi (Fetch API).
* **Chart.js:** Dinamik radar grafikleri.

---

### ⚙️ Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

## 1. Projeyi Klonlayın (CMD/Bash)

git clone [https://github.com/DioBey7/GameHorizon.git](https://github.com/DioBey7/GameHorizon.git)
cd GameHorizon

## 2. Sanal Ortamı (Virtual Environment) Kurun (CMD/Bash)

### Windows için
python -m venv venv
venv\Scripts\activate

### macOS/Linux için
python3 -m venv venv
source venv/bin/activate

## 3. Bağımlılıkları Yükleyin (CMD/Bash)

pip install -r requirements.txt

## 4. Veri Setini Hazırlayın

⚠️ Önemli: GitHub dosya boyutu sınırları nedeniyle veritabanı kaynak dosyası depoya dahil edilmemiştir.
Kaggle üzerinden güncel Steam Games Dataset (JSON formatında) indirin.
İndirdiğiniz dosyayı games.json olarak adlandırın ve proje ana dizinine atın.

## 5. Uygulamayı Başlatın (CMD/Bash)
   
İlk çalıştırmada sistem games.json dosyasını işleyip, vektör modellerini eğiteceği için açılış (donanımınıza bağlı olarak) 1-5 dakika sürebilir. Sonraki açılışlar çok daha hızlıdır.

python app.py

Tarayıcınızda http://localhost:5000 adresine gidin.

---

## 📂 Proje Yapısı
GameHorizon/
├── app.py              # Flask sunucusu, Threading ve API endpointleri
├── model.py            # AI mantığı, FAISS indeksi ve Hibrit Skorlama motoru
├── database.py         # ETL işlemleri, SQLite optimizasyonu ve Veri temizleme
├── config.py           # Sistem ayarları, Ağırlık katsayıları ve Sabitler
├── static/             # Frontend varlıkları
│   ├── style.css       # Glassmorphism stilleri
│   ├── script.js       # Frontend mantığı ve Chart.js entegrasyonu
│   └── manifest.json   # PWA konfigürasyonu
├── templates/          # HTML şablonları
│   └── index.html
├── requirements.txt    # Python bağımlılıkları
└── games.json          # (Manuel Eklenmeli) Kaynak veri seti

## 🔮 Gelecek Planları (Roadmap)

[ ] Kullanıcı Hesapları: Favorilerin bulutta saklanması.

[ ] İşbirlikçi Filtreleme: Kullanıcıların benzerliklerine göre öneri (User-based filtering).

[ ] Steam Entegrasyonu: Kullanıcının Steam kütüphanesini API ile otomatik içe aktarma.

[ ] Canlı Fiyat Takibi: İndirimleri anlık gösterme.

## 📄 Lisans
Bu proje eğitim ve portfolyo amaçlı geliştirilmiştir. MIT Lisansı altında açık kaynaklıdır.

pip install -r requirements.txt

