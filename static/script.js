(function() {
    'use strict';

    class GameHorizon {
        constructor() {
            this.currentLang = 'tr';
            this.isDarkMode = true;
            this.searchHistory = [];
            this.favorites = {};
            this.charts = {}; 
            this.lastSearchResults = null; 

            this.translations = {
                tr: {
                    title: "GameHorizon",
                    labelGameName: "Bir oyun adı girin:",
                    btnSubmitText: "ÖNERİLERİ GÖSTER",
                    historyTitle: "Geçmiş Aramalar",
                    clearHistoryText: "GEÇMİŞİ TEMİZLE",
                    infoTitle: "Oyun Keşif Yolculuğunuz",
                    infoText: "GameHorizon, sevdiğiniz oyunlara benzer yeni oyunları keşfetmenize yardımcı akıllı bir steam oyun öneri sistemidir.",
                    howToUseTitle: "Nasıl Kullanılır?",
                    step1: "Arama çubuğuna sevdiğin bir oyunun adını yaz. Çoklu arama için '+' kullanabilirsin (örn: Halo + Doom).",
                    step2: "Önerilen oyunlardan birini seç veya 'Enter' tuşuna basarak direkt arama yap.",
                    step3: "Radar grafikleri ve benzerlik yüzdeleri ile detaylı analizi incele.",
                    step4: "Gelişmiş filtreleri kullanarak yıl, oynanış süresi gibi kriterleri belirle.",
                    step5: "Steam sayfasına git veya paylaş.",
                    step6: "Favorilere ekle ve geçmiş aramalarını yönet.",
                    step7: "Tema ve dil ayarlarını değiştir.",
                    step8: "Önerilen oyun kartlarındaki yorum butonuna tıklayarak kullanıcı yorumlarını oku ve kendi yorumunu ekle.",
                    warningTitle: "Önemli Hatırlatmalar",
                    warning1: "Görüntülenen fiyatlar eklentiler ve ana oyunlar için yaklaşık fiyatlardır ve indirim dönemlerinde değişiklik gösterebilir.",
                    warning2: "Öneriler; görsel, tür, oynanış ve fiyat gibi birçok faktörün karmaşık analiziyle oluşturulur.",
                    warning3: "En doğru sonuçlar için oyun adlarını ve filtre terimlerini (Örn: Action, RPG) İngilizce ve tam yazmaya özen gösterin.",
                    warning4: "Yorumlar, kullanıcıların önerilen oyunlar hakkındaki deneyimlerini paylaşmaları için önemlidir. Lütfen etik kurallarına uyunuz.",
                    warning5: "GameHorizon, Steam veritabanına bağlıdır ve bazı oyunlar öneri sisteminde yer almayabilir.",
                    warning6: "Uygulama, internet bağlantısı gerektir ve bağlantı sorunları performansı etkileyebilir.",
                    warning7: "Kullanıcı verileri (geçmiş ve favoriler) yalnızca tarayıcıda saklanır ve üçüncü taraflarla paylaşılmaz.",
                    warning8: "GameHorizon, Steam'in resmi bir ürünü değildir ve bağımsız olarak geliştirilmiştir.",
                    warning9: "Öneri ve fiyat bilgileri zamanla değişebilir; en güncel bilgiler için Steam'i kontrol ediniz.",
                    warning10: "Daha fazla öneri ve iyileştirme için linkedin ve github linklerimden bana ulaşabilirsiniz.",
                    gotItText: "ANLADIM!",
                    loadingText: "Sistem yükleniyor... Lütfen bekleyiniz.",
                    noResults: "Hiç sonuç bulunamadı.",
                    errorMessage: "Aradığınız oyun veritabanımızda bulunamadı.",
                    placeholder: "Oyun adı... (Çoklu arama için: Oyun1 + Oyun2)",
                    darkThemeText: "KOYU TEMA",
                    lightThemeText: "AÇIK TEMA",
                    trLangText: "TÜRKÇE",
                    enLangText: "ENGLISH",
                    price: "Ortalama Fiyat",
                    free: "Ücretsiz",
                    viewOnSteam: "Steam'de Görüntüle",
                    similarity: "Benzerlik",
                    genreFilter: "Tür Filtreleme:",
                    excludeFilter: "Dışlama Filtresi:",
                    toggleFilters: "Gelişmiş Filtreler",
                    yearRange: "Yıl Aralığı:",
                    playtimeRange: "Oynanış (Saat):",
                    surpriseMe: "Sürpriz Yap",
                    confirmClearHistory: "Geçmişi silmek istiyor musunuz?",
                    favoritesTitle: "Favoriler",
                    noFavorites: "Favori yok.",
                    shareGame: "Paylaş",
                    shareText: "Bu oyuna benzer oyunlar:",
                    removeFromFavorites: "Çıkar",
                    addToFavorites: "Ekle",
                    similarGamesTitle: "Benzer Oyunlar",
                    otherGamesTitle: "Diğer Öneriler",
                    installApp: "Uygulamayı Yükle",
                    visual: "Görsel",
                    genre: "Tür",
                    gameplay: "Oynanış",
                    popularity: "Popülerlik",
                    noHistory: "Henüz arama geçmişi yok.",
                    invalidInput: "Lütfen geçerli bir oyun adı giriniz.",
                    networkError: "Bağlantı hatası. Lütfen internetinizi kontrol edin.",
                    unknownError: "Beklenmedik bir hata oluştu.",
                    genreFilterPlaceholder: "Örn: Action, RPG",
                    excludeFilterPlaceholder: "Örn: Sports, Racing",
                    commentsTitle: "Kullanıcı Yorumları",
                    noComments: "Henüz yorum yapılmamış. İlk yorumu sen yap!",
                    yourCommentPlaceholder: "Yorumunuzu buraya yazın...",
                    submitComment: "GÖNDER",
                    anonymousUser: "Anonim Oyuncu",
                    didYouMean: "Bunu mu demek istediniz?",
                    randomRecsTitle: "Veritabanımızda bulamadık ama bunları sevebilirsin:"
                },
                en: {
                    title: "GameHorizon",
                    labelGameName: "Enter a game name:",
                    btnSubmitText: "SHOW RECOMMENDATIONS",
                    historyTitle: "Search History",
                    clearHistoryText: "CLEAR HISTORY",
                    infoTitle: "Your Game Discovery Journey",
                    infoText: "GameHorizon is an intelligent recommendation system to help you discover new games.",
                    howToUseTitle: "How to Use?",
                    step1: "Type a game name. Use '+' for multi-game search (e.g., Halo + Doom).",
                    step2: "Select a suggestion or press 'Enter'.",
                    step3: "Analyze with radar charts and similarity scores.",
                    step4: "Use advanced filters for year, playtime, etc.",
                    step5: "View on Steam or share.",
                    step6: "Add to favorites and manage history.",
                    step7: "Change theme and language.",
                    step8: "Read and add user comments by clicking the comment button on game cards.",
                    warningTitle: "Important Reminders",
                    warning1: "Displayed average prices are for the base game and add-ons and may vary during sales.",
                    warning2: "Recommendations are generated through complex analysis of factors like visuals, genre, gameplay, and price.",
                    warning3: "For best results, ensure game names and filter terms (e.g., Action, RPG) are spelled correctly in English.",
                    warning4: "Comments are important for sharing users' experiences with recommended games. Please follow ethical guidelines.",
                    warning5: "GameHorizon relies on the Steam database, and some games may not be included in the recommendation system.",
                    warning6: "The application requires an internet connection, and connectivity issues may affect performance.",
                    warning7: "User data (history and favorites) is stored only in the browser and is not shared with third parties.",
                    warning8: "GameHorizon is not an official Steam product and is independently developed.",
                    warning9: "Recommendations and price information may change over time; please check Steam for the most up-to-date information.",
                    warning10: "For more recommendations and improvements, you can reach me via my LinkedIn and GitHub links.",
                    gotItText: "GOT IT",
                    loadingText: "System loading...",
                    noResults: "No results found.",
                    errorMessage: "The game you searched for was not found in our database.",
                    placeholder: "Game name... (Multi-search: Game1 + Game2)",
                    darkThemeText: "DARK THEME",
                    lightThemeText: "LIGHT THEME",
                    trLangText: "TURKISH",
                    enLangText: "ENGLISH",
                    price: "Average Price",
                    free: "Free",
                    viewOnSteam: "View on Steam",
                    similarity: "Similarity",
                    genreFilter: "Genre Filter:",
                    excludeFilter: "Exclusion Filter:",
                    toggleFilters: "Advanced Filters",
                    yearRange: "Year Range:",
                    playtimeRange: "Playtime (Hours):",
                    surpriseMe: "Surprise Me",
                    confirmClearHistory: "Clear history?",
                    favoritesTitle: "Favorites",
                    noFavorites: "No favorites.",
                    shareGame: "Share",
                    shareText: "Similar games:",
                    removeFromFavorites: "Remove",
                    addToFavorites: "Add",
                    similarGamesTitle: "Similar Games",
                    otherGamesTitle: "Other Suggestions",
                    installApp: "Install App",
                    visual: "Visual",
                    genre: "Genre",
                    gameplay: "Gameplay",
                    popularity: "Popularity",
                    noHistory: "No search history yet.",
                    invalidInput: "Please enter a valid game name.",
                    networkError: "Network error. Please check your connection.",
                    unknownError: "An unexpected error occurred.",
                    genreFilterPlaceholder: "E.g., Action, RPG",
                    excludeFilterPlaceholder: "E.g., Sports, Racing",
                    commentsTitle: "User Reviews",
                    noComments: "No comments yet. Be the first!",
                    yourCommentPlaceholder: "Write your comment here...",
                    submitComment: "SUBMIT",
                    anonymousUser: "Anonymous Player",
                    didYouMean: "Did you mean?",
                    randomRecsTitle: "We couldn't find it, but you might like these:"
                }
            };

            this.initializeApp();
        }

        initializeApp() {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupEventListeners();
                this.loadUserPreferences();
                this.updateUI();
                this.hideLoadingScreen();
                this.setupPWA();
                this.createBackgroundElements();
            });
        }
        
        createBackgroundElements() {
            if (!document.getElementById('stars1')) {
                const stars1 = document.createElement('div'); stars1.id = 'stars1';
                const stars2 = document.createElement('div'); stars2.id = 'stars2';
                const stars3 = document.createElement('div'); stars3.id = 'stars3';
                document.body.prepend(stars3, stars2, stars1);
            }
        }

        setupPWA() {
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/service-worker.js')
                    .then(() => console.log('Service Worker Registered'))
                    .catch(e => console.error('Service Worker registration failed:', e));
            }
        }

        showToast(message, type = 'info') {
            const existingToasts = document.querySelectorAll('.toast');
            existingToasts.forEach(t => t.remove());

            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            void toast.offsetWidth;
            
            setTimeout(() => toast.classList.add('show'), 100);
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    if(document.body.contains(toast)) document.body.removeChild(toast);
                }, 300);
            }, 3000);
        }

        setupEventListeners() {
            document.getElementById('recommendForm').addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit();
            });

            const gameInput = document.getElementById('game_name');
            gameInput.addEventListener('input', this.debounce((e) => {
                const val = e.target.value;
                const lastQuery = val.split('+').pop().trim();
                this.fetchAutocompleteSuggestions(lastQuery);
            }, 300));
            
            gameInput.addEventListener('keydown', (e) => this.handleAutocompleteNavigation(e));

            document.getElementById('btn-surprise').addEventListener('click', () => this.handleSurprise());

            document.getElementById('toggle-filters').addEventListener('click', () => {
                const panel = document.getElementById('filter-panel');
                panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
            });

            document.body.addEventListener('click', (e) => {
                const langBtn = e.target.closest('.lang-btn');
                if (langBtn) return this.changeLanguage(langBtn.dataset.lang);

                const themeToggle = e.target.closest('#themeToggle');
                if (themeToggle) return this.toggleTheme();
                
                const showFavorites = e.target.closest('#showFavorites');
                if (showFavorites) return this.toggleFavorites();
                
                const closeFavorites = e.target.closest('#closeFavorites');
                if (closeFavorites) return this.toggleFavorites(false);

                const infoControl = e.target.closest('#closeInfo, #gotItBtn');
                if (infoControl) return this.hideInfoCard();

                const clearHistory = e.target.closest('#clearHistory');
                if (clearHistory) return this.clearSearchHistory();
                
                const historyItem = e.target.closest('.history-item');
                if (historyItem) {
                    const gameName = historyItem.querySelector('span').textContent;
                    if (e.target.closest('.search-history-btn')) {
                        this.searchFromHistory(gameName);
                    } else if (e.target.closest('.remove-history-btn')) {
                        this.removeFromHistory(gameName);
                    } else {
                        this.searchFromHistory(gameName);
                    }
                }
                
                const autocompleteItem = e.target.closest('.autocomplete-item');
                if (autocompleteItem) return this.selectAutocompleteItem(autocompleteItem.dataset.value);
                
                const suggestionChip = e.target.closest('.suggestion-chip');
                if(suggestionChip) {
                    document.getElementById('game_name').value = suggestionChip.dataset.value;
                    this.handleFormSubmit();
                }

                if (!e.target.closest('.autocomplete')) this.hideAutocomplete();
                
                const card = e.target.closest('.game-card');
                if(card) {
                    const gameId = card.dataset.gameId;
                    const gameDataElement = card.querySelector('[data-game-data]');
                    if(gameDataElement){
                        const gameData = JSON.parse(gameDataElement.dataset.gameData);

                        if (e.target.closest('.favorite-btn')) {
                            e.stopPropagation();
                            this.toggleFavorite(gameId, gameData);
                        } else if (e.target.closest('.share-btn')) {
                            e.stopPropagation();
                            this.shareGame(gameData);
                        } else if (e.target.closest('.comment-btn')) {
                            e.stopPropagation();
                            this.openCommentsModal(gameId, gameData.name);
                        } else if (!e.target.closest('.btn-view')) {
                             window.open(gameData.steamUrl, '_blank');
                        }
                    }
                }
                
                const favRemoveBtn = e.target.closest('.remove-favorite');
                if(favRemoveBtn) {
                    e.stopPropagation();
                    this.toggleFavorite(favRemoveBtn.dataset.gameId);
                }

                if (e.target.classList.contains('modal-overlay') || e.target.closest('.close-modal')) {
                    this.closeModal();
                }
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.hideAutocomplete();
                    this.toggleFavorites(false);
                    this.closeModal();
                }
            });
        }

        loadUserPreferences() {
            const savedLang = localStorage.getItem('preferredLanguage') || 'tr';
            const savedTheme = localStorage.getItem('preferredTheme');
            const infoCardHidden = localStorage.getItem('infoCardHidden');
            this.searchHistory = JSON.parse(localStorage.getItem('gameSearchHistory')) || [];
            this.favorites = JSON.parse(localStorage.getItem('gameFavorites')) || {};

            this.changeLanguage(savedLang, false);

            if (savedTheme) {
                this.isDarkMode = savedTheme === 'dark';
            } else {
                this.isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
            }

            if (infoCardHidden) {
                document.getElementById('infoCard').style.display = 'none';
            }

            this.renderSearchHistory();
            this.renderFavorites();
        }

        updateUI() {
            this.translatePage();
            this.updateThemeUI();
        }

        translatePage() {
            document.querySelectorAll('[data-translate]').forEach(el => {
                const key = el.dataset.translate;
                const translation = this.translations[this.currentLang][key];
                if (translation) {
                    if (el.placeholder) el.placeholder = translation;
                    else el.textContent = translation;
                }
            });
            this.updateDynamicTexts();
            this.updatePlaceholders();
            this.renderSearchHistory();
        }

        updateDynamicTexts() {
            const themeText = document.querySelector('.theme-text');
            if (themeText) {
                themeText.textContent = this.isDarkMode ?
                    this.translations[this.currentLang].darkThemeText :
                    this.translations[this.currentLang].lightThemeText;
            }
        }

        updatePlaceholders() {
            document.getElementById('genre_filter').placeholder = this.translations[this.currentLang].genreFilterPlaceholder;
            document.getElementById('exclude_filter').placeholder = this.translations[this.currentLang].excludeFilterPlaceholder;
        }

        changeLanguage(lang, save = true) {
            if (this.currentLang === lang && save) return; 
            this.currentLang = lang;
            document.querySelectorAll('.lang-btn').forEach(btn => {
                btn.classList.toggle('active', btn.dataset.lang === lang);
            });
            this.translatePage();
            if (save) localStorage.setItem('preferredLanguage', lang);

            if (this.lastSearchResults) {
                if(this.lastSearchResults.error) {
                    this.showErrorWithSuggestions(this.lastSearchResults.query);
                } else {
                    this.displayResults(this.lastSearchResults);
                }
            }
            this.renderFavorites();
        }

        toggleTheme(save = true) {
            this.isDarkMode = !this.isDarkMode;
            this.updateThemeUI();
            if (save) localStorage.setItem('preferredTheme', this.isDarkMode ? 'dark' : 'light');
            this.refreshCharts();
        }

        updateThemeUI() {
            document.body.classList.toggle('light', !this.isDarkMode);
            const themeIcon = document.querySelector('.theme-icon');
            if (themeIcon) {
                themeIcon.className = this.isDarkMode ? 'fas fa-moon theme-icon' : 'fas fa-sun theme-icon';
            }
            this.updateDynamicTexts();
        }

        async handleSurprise() {
            this.showLoadingState();
            try {
                const response = await fetch('/api/surprise');
                if(!response.ok) throw new Error('API Error');
                const data = await response.json();
                document.getElementById('game_name').value = data.source.Name;
                this.lastSearchResults = data;
                this.displayResults(data);
            } catch (e) {
                this.showError(this.translations[this.currentLang].errorMessage);
            } finally {
                this.hideLoadingState();
            }
        }

        async handleFormSubmit() {
            const gameInput = document.getElementById('game_name');
            const genreInput = document.getElementById('genre_filter');
            const excludeInput = document.getElementById('exclude_filter');
            let yearMin = document.getElementById('year_min').value;
            let yearMax = document.getElementById('year_max').value;
            let playMin = document.getElementById('playtime_min').value;
            let playMax = document.getElementById('playtime_max').value;

            if (yearMin && yearMin < 0) yearMin = 0;
            if (yearMax && yearMax < 0) yearMax = 0;
            if (playMin && playMin < 0) playMin = 0;
            if (playMax && playMax < 0) playMax = 0;

            const gameName = gameInput.value.trim();

            if (!gameName) return this.showError(this.translations[this.currentLang].invalidInput);

            this.showLoadingState();
            this.hideAutocomplete();
            this.destroyCharts();

            try {
                const params = new URLSearchParams({ q: gameName });
                if (genreInput.value.trim()) params.append('genres', genreInput.value.trim());
                if (excludeInput.value.trim()) params.append('exclude', excludeInput.value.trim());
                if (yearMin) params.append('year_min', yearMin);
                if (yearMax) params.append('year_max', yearMax);
                if (playMin) params.append('playtime_min', playMin);
                if (playMax) params.append('playtime_max', playMax);

                const response = await fetch(`/api/search?${params.toString()}`);
                
                if (!response.ok) {
                    this.showErrorWithSuggestions(gameName);
                    this.lastSearchResults = { error: true, query: gameName };
                    return;
                }
                
                const data = await response.json();
                
                if (data.error) {
                     this.showErrorWithSuggestions(gameName);
                     this.lastSearchResults = { error: true, query: gameName };
                     return;
                }

                this.lastSearchResults = data;
                this.displayResults(data);
                this.addToSearchHistory(gameName);
            } catch (error) {
                this.showErrorWithSuggestions(gameName);
            } finally {
                this.hideLoadingState();
            }
        }
        
        async showErrorWithSuggestions(query) {
            const resultSection = document.getElementById('result');
            const trans = this.translations[this.currentLang];
            
            let suggestions = [];
            try {
                 const res = await fetch(`/api/autocomplete?q=${encodeURIComponent(query)}`);
                 suggestions = await res.json();
            } catch(e) {}

            let html = `
                <div class="error-box glass-effect">
                    <h3><i class="fas fa-exclamation-circle"></i> ${trans.errorMessage}</h3>
                    <p>${trans.noResults}</p>
            `;

            if (suggestions.length > 0) {
                html += `
                    <div class="suggestion-box">
                        <h4>${trans.didYouMean}</h4>
                        <div class="suggestion-list">
                            ${suggestions.map(s => `<span class="suggestion-chip" data-value="${this.escapeHtml(s)}">${this.escapeHtml(s)}</span>`).join('')}
                        </div>
                    </div>
                `;
            }
            
            html += `</div>`; 
            
            try {
                const randomRes = await fetch('/api/surprise');
                const randomData = await randomRes.json();
                
                if(randomData.results && randomData.results.length > 0) {
                    const randomGames = randomData.results.slice(0, 4); 
                    
                    html += `
                        <div class="random-recs-box">
                            <h3 class="random-recs-title">${trans.randomRecsTitle}</h3>
                            <div class="result-grid">
                                ${randomGames.map((game, i) => this.createGameCardHtml(game, i)).join('')}
                            </div>
                        </div>
                    `;
                    
                    setTimeout(() => {
                         randomGames.forEach(game => this.createRadarChart(game));
                    }, 100);
                }
            } catch(e) {}

            resultSection.innerHTML = html;
        }

        getErrorMessage(error) {
            if (error.message.includes('Failed to fetch')) return this.translations[this.currentLang].networkError;
            return error.message || this.translations[this.currentLang].unknownError;
        }

        displayResults(data) {
            const resultSection = document.getElementById('result');
            if (!data || !data.results || data.results.length === 0) {
                this.showErrorWithSuggestions(data?.query || "");
                return;
            }
            
            const validResults = data.results.filter(game => game.Name && game.similarity > 0.1);
            if(validResults.length === 0) {
                 this.showErrorWithSuggestions(data.query);
                 return;
            }

            const similarGames = validResults.filter(g => (g.similarity || 0) * 100 >= 50);
            const otherGames = validResults.filter(g => (g.similarity || 0) * 100 < 50);

            let html = '';

            if (similarGames.length > 0) {
                html += `<h2 class="section-title">${this.translations[this.currentLang].similarGamesTitle}</h2>`;
                html += `<div class="result-grid">${similarGames.map((game, i) => this.createGameCardHtml(game, i)).join('')}</div>`;
            }

            if (otherGames.length > 0) {
                html += `<h2 class="section-title">${this.translations[this.currentLang].otherGamesTitle}</h2>`;
                html += `<div class="result-grid">${otherGames.map((game, i) => this.createGameCardHtml(game, i + similarGames.length)).join('')}</div>`;
            }
            
            resultSection.innerHTML = html;

            setTimeout(() => {
                validResults.forEach(game => this.createRadarChart(game));
            }, 50);
        }
        
        createGameCardHtml(game, index) {
            const priceText = game.price === 0 ? this.translations[this.currentLang].free : `$${parseFloat(game.price).toFixed(2)}`;
            const similarityPercentage = Math.round((game.similarity || 0) * 100);
            const similarityColor = this.getSimilarityColor(similarityPercentage);
            const imageUrl = game.ImageURL;
            const playTime = game.playtime ? Math.round(game.playtime / 60) + 'h' : 'N/A';
            const year = game.year || 'N/A';
            
            const isFavorite = !!this.favorites[game.AppID];
            const favoriteIcon = isFavorite ? 'fas' : 'far';
            
            const gameDataForAttr = JSON.stringify({
                appid: game.AppID,
                name: game.Name,
                price: game.price,
                steamUrl: game.SteamURL,
                header_image: game.ImageURL
            }).replace(/"/g, '&quot;');

            return `
                <div class="game-card" data-game-id="${game.AppID}" style="animation-delay: ${index * 50}ms">
                    <div class="game-card-header">
                        <img src="${imageUrl}" alt="${this.escapeHtml(game.Name)}" class="game-image" loading="lazy" onerror="this.style.display='none'">
                        <div class="game-actions" data-game-data="${gameDataForAttr}">
                            <button class="favorite-btn" aria-label="${isFavorite ? this.translations[this.currentLang].removeFromFavorites : this.translations[this.currentLang].addToFavorites}">
                                <i class="${favoriteIcon} fa-heart"></i>
                            </button>
                            <button class="comment-btn" aria-label="Yorumlar">
                                <i class="fas fa-comment-alt"></i>
                            </button>
                            <button class="share-btn" aria-label="${this.translations[this.currentLang].shareGame}">
                                <i class="fas fa-share-alt"></i>
                            </button>
                        </div>
                        <div class="game-similarity" style="background: ${similarityColor};">
                            ${similarityPercentage}%
                        </div>
                    </div>
                    <div class="game-card-body">
                        <h3 class="game-title" title="${this.escapeHtml(game.Name)}">${this.escapeHtml(game.Name)}</h3>
                        <div class="meta-info">
                            <span><i class="fas fa-calendar"></i> ${year}</span>
                            <span><i class="fas fa-clock"></i> ${playTime}</span>
                        </div>
                        <p class="game-price">${this.translations[this.currentLang].price}: <strong>${priceText}</strong></p>
                        
                        <div class="chart-wrapper">
                            <canvas id="chart-${game.AppID}"></canvas>
                        </div>

                        <div class="game-tags">
                            ${(game.genres || []).slice(0, 3).map(genre => `<span class="game-tag">${this.escapeHtml(genre)}</span>`).join('')}
                        </div>
                    </div>
                    <div class="game-card-footer">
                        <a href="${game.SteamURL}" target="_blank" rel="noopener noreferrer" class="btn-view"><i class="fab fa-steam"></i> ${this.translations[this.currentLang].viewOnSteam}</a>
                    </div>
                </div>
            `;
        }

        createRadarChart(game) {
            const ctx = document.getElementById(`chart-${game.AppID}`);
            if (!ctx) return;
            
            if (this.charts[game.AppID]) {
                this.charts[game.AppID].destroy();
            }

            const b = game.breakdown;
            const labels = [
                this.translations[this.currentLang].visual,
                this.translations[this.currentLang].genre,
                this.translations[this.currentLang].gameplay,
                this.translations[this.currentLang].price,
                this.translations[this.currentLang].popularity
            ];
            
            const textColor = this.isDarkMode ? '#dfe6e9' : '#2d3436';
            const gridColor = this.isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

            this.charts[game.AppID] = new Chart(ctx, {
                type: 'radar',
                data: {
                    labels: labels,
                    datasets: [{
                        data: [b.visual, b.genre, b.gameplay, b.price, b.popularity],
                        backgroundColor: 'rgba(108, 92, 231, 0.2)',
                        borderColor: 'rgba(108, 92, 231, 0.8)',
                        pointBackgroundColor: 'rgba(108, 92, 231, 1)',
                        borderWidth: 1.5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: { display: false },
                            pointLabels: {
                                font: { size: 10, family: 'Poppins' },
                                color: textColor
                            },
                            grid: { color: gridColor },
                            angleLines: { color: gridColor }
                        }
                    },
                    plugins: { legend: { display: false } }
                }
            });
        }

        destroyCharts() {
            Object.values(this.charts).forEach(chart => chart.destroy());
            this.charts = {};
        }

        refreshCharts() {
            if (this.lastSearchResults) {
                if(this.lastSearchResults.error) {
                    this.showErrorWithSuggestions(this.lastSearchResults.query);
                } else {
                    this.displayResults(this.lastSearchResults);
                }
            }
        }

        escapeHtml(text) {
            if (typeof text !== 'string') return text;
            return text.replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[m]);
        }

        toggleFavorite(gameId, gameData) {
            if (this.favorites[gameId]) {
                delete this.favorites[gameId];
                this.showToast(this.translations[this.currentLang].removeFromFavorites, 'info');
            } else {
                this.favorites[gameId] = gameData;
                this.showToast(this.translations[this.currentLang].addToFavorites, 'success');
            }
            localStorage.setItem('gameFavorites', JSON.stringify(this.favorites));
            
            document.querySelectorAll(`.game-card[data-game-id="${gameId}"] .favorite-btn i`).forEach(icon => {
                icon.className = this.favorites[gameId] ? 'fas fa-heart' : 'far fa-heart';
            });
            
            this.renderFavorites();
        }

        renderFavorites() {
            const list = document.getElementById('favoritesList');
            const favIds = Object.keys(this.favorites);
            if(favIds.length === 0) {
                list.innerHTML = `<div class="no-favorites" style="padding:1rem; text-align:center; color:var(--text-secondary)">${this.translations[this.currentLang].noFavorites}</div>`;
                return;
            }
            list.innerHTML = favIds.map(id => this.createFavoriteGameHtml(this.favorites[id])).join('');
        }
        
        createFavoriteGameHtml(game) {
            const priceText = game.price === 0 ? this.translations[this.currentLang].free : `$${parseFloat(game.price).toFixed(2)}`;
            const imageUrl = game.header_image;
            return `
                <div class="favorite-game" data-game-id="${game.appid}">
                    <img src="${imageUrl}" class="favorite-game-image" alt="${this.escapeHtml(game.name)}">
                    <div class="favorite-game-info">
                        <h4>${this.escapeHtml(game.name)}</h4>
                        <div class="favorite-game-price">${this.translations[this.currentLang].price}: ${priceText}</div>
                    </div>
                    <div class="favorite-game-actions">
                         <a href="${game.steamUrl}" target="_blank" rel="noopener noreferrer" class="btn-view small"><i class="fab fa-steam"></i></a>
                         <button class="remove-favorite" data-game-id="${game.appid}"><i class="fas fa-times"></i></button>
                    </div>
                </div>
            `;
        }
        
        toggleFavorites(show = null) {
            const favoritesSection = document.getElementById('favoritesSection');
            if (show === null) show = !favoritesSection.classList.contains('show');
            favoritesSection.classList.toggle('show', show);
            if(show) this.renderFavorites();
        }
        
        shareGame(gameData) {
            const text = `${this.translations[this.currentLang].shareText} ${gameData.name}`;
            if (navigator.share) {
                navigator.share({ title: gameData.name, text, url: gameData.steamUrl });
            } else {
                navigator.clipboard.writeText(gameData.steamUrl).then(() => this.showToast('Link kopyalandı!', 'success'));
            }
        }

        getSimilarityColor(percentage) {
            if (percentage >= 80) return 'linear-gradient(135deg, #00b894, #00cec9)';
            if (percentage >= 60) return 'linear-gradient(135deg, #0984e3, #6c5ce7)';
            if (percentage >= 40) return 'linear-gradient(135deg, #fdcb6e, #fab1a0)';
            return 'linear-gradient(135deg, #d63031, #ff7675)';
        }

        async fetchAutocompleteSuggestions(query) {
            const spinner = document.getElementById('autocomplete-spinner');
            if (!query || query.length < 2) return this.hideAutocomplete();
            
            spinner.hidden = false;
            try {
                const response = await fetch(`/api/autocomplete?q=${encodeURIComponent(query)}`);
                if (!response.ok) throw new Error('Autocomplete fetch failed');
                const suggestions = await response.json();
                this.showAutocompleteSuggestions(suggestions);
            } catch (error) {
                console.error('Autocomplete error:', error);
                this.hideAutocomplete();
            } finally {
                spinner.hidden = true;
            }
        }
        
        showAutocompleteSuggestions(suggestions) {
            const list = document.getElementById('autocomplete-list');
            if (!suggestions || suggestions.length === 0) return this.hideAutocomplete();
            list.innerHTML = suggestions.map(s => `<div class="autocomplete-item" data-value="${this.escapeHtml(s)}">${this.escapeHtml(s)}</div>`).join('');
            list.hidden = false;
        }
        
        hideAutocomplete() {
            document.getElementById('autocomplete-list').hidden = true;
        }

        selectAutocompleteItem(value) {
            const input = document.getElementById('game_name');
            const currentVal = input.value;
            const parts = currentVal.split('+');
            parts.pop();
            parts.push(value);
            input.value = parts.join(' + ').trim(); 
            this.hideAutocomplete();
        }

        handleAutocompleteNavigation(e) {
            const list = document.getElementById('autocomplete-list');
            if (list.hidden) return;
            const items = list.querySelectorAll('.autocomplete-item');
            if (items.length === 0) return;

            let activeIndex = Array.from(items).findIndex(item => item.classList.contains('active'));

            if (e.key === 'ArrowDown') {
                activeIndex = activeIndex < items.length - 1 ? activeIndex + 1 : 0;
            } else if (e.key === 'ArrowUp') {
                activeIndex = activeIndex > 0 ? activeIndex - 1 : items.length - 1;
            } else if (e.key === 'Enter' && activeIndex > -1) {
                e.preventDefault();
                this.selectAutocompleteItem(items[activeIndex].dataset.value);
                return;
            } else {
                return;
            }

            items.forEach(item => item.classList.remove('active'));
            items[activeIndex].classList.add('active');
        }

        addToSearchHistory(gameName) {
            this.searchHistory = [gameName, ...this.searchHistory.filter(name => name.toLowerCase() !== gameName.toLowerCase())].slice(0, 10);
            localStorage.setItem('gameSearchHistory', JSON.stringify(this.searchHistory));
            this.renderSearchHistory();
        }

        renderSearchHistory() {
            const list = document.getElementById('historyList');
            if (this.searchHistory.length === 0) {
                list.innerHTML = `<li class="history-item" style="justify-content:center; color:var(--text-secondary)">${this.translations[this.currentLang].noHistory}</li>`;
                return;
            }
            list.innerHTML = this.searchHistory.map(game => `
                <li class="history-item">
                    <span>${this.escapeHtml(game)}</span>
                    <div>
                        <button class="search-history-btn" title="${this.translations[this.currentLang].search || 'Search'}"><i class="fas fa-search"></i></button>
                        <button class="remove-history-btn" title="${this.translations[this.currentLang].remove || 'Remove'}"><i class="fas fa-times"></i></button>
                    </div>
                </li>`).join('');
        }

        searchFromHistory(gameName) {
            document.getElementById('game_name').value = gameName;
            this.handleFormSubmit();
        }

        removeFromHistory(gameName) {
            this.searchHistory = this.searchHistory.filter(name => name !== gameName);
            localStorage.setItem('gameSearchHistory', JSON.stringify(this.searchHistory));
            this.renderSearchHistory();
        }

        clearSearchHistory() {
            if (confirm(this.translations[this.currentLang].confirmClearHistory)) {
                this.searchHistory = [];
                localStorage.removeItem('gameSearchHistory');
                this.renderSearchHistory();
            }
        }

        hideInfoCard() {
            document.getElementById('infoCard').style.display = 'none';
            localStorage.setItem('infoCardHidden', 'true');
        }

        showLoadingState() {
            const btn = document.getElementById('btn-submit');
            btn.disabled = true;
            btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${this.translations[this.currentLang].btnSubmitText}`;
            document.getElementById('result').innerHTML = `<div class="loading-recommendations"><div class="spinner-large"></div></div>`;
        }

        hideLoadingState() {
            const btn = document.getElementById('btn-submit');
            btn.disabled = false;
            btn.innerHTML = this.translations[this.currentLang].btnSubmitText;
        }

        showError(message) {
            document.getElementById('result').innerHTML = `<div class="error-message glass-effect"><h3>${message}</h3></div>`;
        }

        hideLoadingScreen() {
            const screen = document.getElementById('loading-screen');
            screen.style.opacity = '0';
            setTimeout(() => screen.style.display = 'none', 500);
        }
        
        openCommentsModal(appId, gameName) {
            let modalOverlay = document.querySelector('.modal-overlay');
            if(!modalOverlay) {
                modalOverlay = document.createElement('div');
                modalOverlay.className = 'modal-overlay';
                document.body.appendChild(modalOverlay);
            }
            
            const trans = this.translations[this.currentLang];
            modalOverlay.innerHTML = `
                <div class="modal glass-effect">
                    <div class="modal-header">
                        <h3>${trans.commentsTitle} - ${this.escapeHtml(gameName)}</h3>
                        <button class="close-modal"><i class="fas fa-times"></i></button>
                    </div>
                    <div class="modal-body">
                        <div id="commentsList" class="comments-list">
                            <div style="text-align:center; padding:1rem;"><div class="spinner-large" style="width:30px; height:30px;"></div></div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <form id="commentForm" class="comment-form" data-appid="${appId}">
                            <textarea class="comment-input" placeholder="${trans.yourCommentPlaceholder}" required></textarea>
                            <button type="submit" class="submit-comment-btn">${trans.submitComment}</button>
                        </form>
                    </div>
                </div>
            `;
            
            this.fetchComments(appId);
            
            modalOverlay.querySelector('#commentForm').addEventListener('submit', (e) => {
                e.preventDefault();
                this.postComment(appId);
            });
        }

        closeModal() {
            const modal = document.querySelector('.modal-overlay');
            if (modal) modal.remove();
        }

        async fetchComments(appId) {
            try {
                const res = await fetch(`/api/comments?appid=${appId}`);
                if (!res.ok) throw new Error('Fetch failed');
                const comments = await res.json();
                this.renderComments(comments);
            } catch (e) {
                document.getElementById('commentsList').innerHTML = `<div class="error-message">${this.translations[this.currentLang].errorMessage}</div>`;
            }
        }

        async postComment(appId) {
            const input = document.querySelector('.comment-input');
            const content = input.value.trim();
            if (!content) return;

            try {
                const res = await fetch('/api/comments', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({appid: appId, content: content})
                });
                
                if (!res.ok) throw new Error('Post failed');
                
                input.value = '';
                this.fetchComments(appId);
            } catch (e) {
                alert(this.translations[this.currentLang].errorMessage);
            }
        }

        renderComments(comments) {
            const list = document.getElementById('commentsList');
            const trans = this.translations[this.currentLang];
            
            if (!comments || comments.length === 0) {
                list.innerHTML = `<div class="no-comments">${trans.noComments}</div>`;
                return;
            }

            list.innerHTML = comments.map(c => `
                <div class="comment-item">
                    <div class="comment-header">
                        <span class="comment-author">${trans.anonymousUser}</span>
                        <span class="comment-date">${new Date(c.created_at).toLocaleDateString()}</span>
                    </div>
                    <div class="comment-text">${this.escapeHtml(c.content)}</div>
                </div>
            `).join('');
        }

        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func.apply(this, args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    }

    window.gameHorizon = new GameHorizon();

})();