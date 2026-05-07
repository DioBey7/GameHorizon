const SynthEngine = {
    ctx: null,
    init() { if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)(); },
    play(type) {
        if (!this.ctx) return;
        if (this.ctx.state === 'suspended') this.ctx.resume();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain); gain.connect(this.ctx.destination);
        const now = this.ctx.currentTime;
        if (type === 'hover') { osc.frequency.setValueAtTime(600, now); gain.gain.setValueAtTime(0.01, now); osc.start(now); osc.stop(now + 0.05); }
        else if (type === 'click') { osc.type = 'square'; osc.frequency.setValueAtTime(150, now); gain.gain.setValueAtTime(0.03, now); osc.start(now); osc.stop(now + 0.1); }
        else if (type === 'success') { osc.frequency.setValueAtTime(440, now); gain.gain.setValueAtTime(0.02, now); osc.start(now); osc.stop(now + 0.3); }
        else if (type === 'error') { osc.type = 'sawtooth'; osc.frequency.setValueAtTime(100, now); gain.gain.setValueAtTime(0.05, now); osc.start(now); osc.stop(now + 0.2); }
    }
};

const UI = {
    search: document.getElementById('search-input'),
    autoList: document.getElementById('autocomplete-list'),
    results: document.getElementById('results-container'),
    loading: document.getElementById('loading'),
    btnSurprise: document.getElementById('btn-surprise'),
    btnInfo: document.getElementById('btn-info'),
    modalChart: document.getElementById('chart-modal'),
    modalInfo: document.getElementById('info-modal'),
    modalCloses: document.querySelectorAll('.close-modal'),
    chartTitle: document.getElementById('chart-title'),
    ctx: document.getElementById('radarChart').getContext('2d')
};

const Inputs = {
    sliders: ['w_visual', 'w_tag', 'w_genre', 'w_quality', 'w_popularity'],
    filters: ['f_genres', 'f_exclude', 'f_price']
};

let radarChart = null;
let currentResultsData = new Map();
let currentFocus = -1;

function debounce(func, delay) {
    let timeout;
    return (...args) => { clearTimeout(timeout); timeout = setTimeout(() => func(...args), delay); };
}

function initChart() {
    Chart.defaults.color = '#6b6b80';
    radarChart = new Chart(UI.ctx, {
        type: 'radar',
        data: {
            labels: ['SEMANTİK', 'MEKANİK', 'TÜR', 'GÖRSEL', 'KALİTE', 'POPÜLERLİK'],
            datasets: [{ data: [0, 0, 0, 0, 0, 0], backgroundColor: 'rgba(138, 43, 226, 0.15)', borderColor: '#8a2be2', pointBackgroundColor: '#00f3ff', borderWidth: 1.5 }]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { r: { angleLines: { color: 'rgba(26, 26, 36, 0.8)' }, grid: { color: 'rgba(26, 26, 36, 0.8)' }, ticks: { display: false, min: 0, max: 100 } } }, plugins: { legend: { display: false } } }
    });
}

function updateChartData(name, breakdown) {
    UI.chartTitle.textContent = `${name} // SİNİRSEL ANALİZ`;
    radarChart.data.datasets[0].data = [breakdown.vector, breakdown.tag, breakdown.genre, breakdown.visual, breakdown.quality, breakdown.popularity];
    radarChart.update();
    UI.modalChart.classList.remove('hidden');
}

function buildQueryString(q) {
    const p = new URLSearchParams(); if (q) p.append('q', q);
    Inputs.sliders.forEach(id => {
        const el = document.getElementById(id);
        if(el) p.append(id.replace('w_', ''), el.value);
    });
    const g = document.getElementById('f_genres').value.trim(); if (g) p.append('genres', g);
    const e = document.getElementById('f_exclude').value.trim(); if (e) p.append('exclude', e);
    const pr = document.getElementById('f_price').value; if (pr) p.append('max_price', pr);
    if (document.getElementById('f_indie').checked) p.append('is_indie', 'true');
    return p.toString();
}

async function performSearch(query) {
    if (!query) return;
    UI.results.innerHTML = ''; UI.loading.classList.remove('hidden'); UI.autoList.innerHTML = ''; currentResultsData.clear();
    SynthEngine.play('click');
    try {
        const res = await fetch(`/api/search?${buildQueryString(query)}`);
        const data = await res.json();
        if (data.results && data.results.length > 0) { renderResults(data.results); SynthEngine.play('success'); }
        else { handleEmptySearch(query); }
    } catch (err) { handleServerError(); } finally { UI.loading.classList.add('hidden'); }
}

function renderResults(results) {
    const fragment = document.createDocumentFragment();
    const uniqueIds = new Set();
    results.forEach((game, index) => {
        if (uniqueIds.has(game.AppID)) return;
        uniqueIds.add(game.AppID);
        currentResultsData.set(String(game.AppID), game);
        const card = document.createElement('div');
        card.className = 'game-card';
        card.style.animation = `fadeUp 0.5s ease forwards ${index * 0.05}s`;
        card.style.opacity = '0';
        card.addEventListener('mouseenter', () => SynthEngine.play('hover'));
        const reasons = (game.match_reasons || []).map(r => `<span class="reason-tag">${r.description}</span>`).join('') || '<span class="reason-tag">Semantik Eşleşme</span>';
        const price = (game.price === 0) ? '<span style="color:var(--accent-cyan); font-weight: 800;">ÜCRETSİZ</span>' : `$${game.price.toFixed(2)}`;
        const developer = (game.developer && game.developer !== "None") ? game.developer : "BELİRTİLMEMİŞ";

        card.innerHTML = `
            <img class="card-img" src="${game.ImageURL}" alt="${game.Name}" loading="lazy">
            <div class="card-content">
                <h4 class="card-title">${game.Name}</h4>
                <div class="reason-container">${reasons}</div>
                <div class="card-meta">
                    <div class="meta-row"><span class="meta-label">GELİŞTİRİCİ</span><span class="meta-value">${developer}</span></div>
                    <div class="meta-row"><span class="meta-label">LİSANS BEDELİ</span><span class="meta-value">${price}</span></div>
                    <div class="meta-row"><span class="meta-label">OYUNCU SKORU</span><span class="meta-value" style="color:var(--accent-cyan)">%${game.approval_ratio.toFixed(0)}</span></div>
                </div>
                <div class="card-score">
                    <span class="score-badge">%${(game.similarity * 100).toFixed(1)}</span>
                    <button class="btn-chart" data-id="${game.AppID}">ANALİZ</button>
                </div>
            </div>`;
        fragment.appendChild(card);
    });
    UI.results.appendChild(fragment);
}

function handleEmptySearch(query) {
    UI.results.innerHTML = `<div class="error-container"><div class="error-code">VERİ YOK</div><div class="error-msg">${query} matriste bulunamadı veya filtreler çok kısıtlı.</div></div>`;
}

function handleServerError() {
    UI.results.innerHTML = `<div class="error-container"><div class="error-code">[SYS_ERR]</div><div class="error-msg">Bağlantı kesildi.</div></div>`;
}

const handleAutocomplete = debounce(async (val) => {
    if (val.length < 2) { UI.autoList.innerHTML = ''; return; }
    try {
        const res = await fetch(`/api/autocomplete?q=${encodeURIComponent(val)}`);
        const names = await res.json();
        UI.autoList.innerHTML = names.map(n => `<li>${n}</li>`).join('');
        UI.autoList.classList.remove('hidden');
    } catch (err) { UI.autoList.innerHTML = ''; }
}, 250);

UI.search.addEventListener('input', (e) => handleAutocomplete(e.target.value));
UI.search.addEventListener('keydown', (e) => {
    let items = UI.autoList.getElementsByTagName('li');
    if (e.key === 'ArrowDown') { e.preventDefault(); currentFocus++; addActive(items); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); currentFocus--; addActive(items); }
    else if (e.key === 'Enter') {
        e.preventDefault();
        if (currentFocus > -1 && items.length > 0) items[currentFocus].click();
        else { UI.autoList.innerHTML = ''; performSearch(UI.search.value); }
    }
});

function addActive(items) {
    if (!items) return; removeActive(items);
    if (currentFocus >= items.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (items.length - 1);
    items[currentFocus].classList.add('autocomplete-active'); SynthEngine.play('hover');
}
function removeActive(items) { for (let i = 0; i < items.length; i++) items[i].classList.remove('autocomplete-active'); }

UI.autoList.addEventListener('click', (e) => {
    if (e.target.tagName === 'LI') { UI.search.value = e.target.textContent; UI.autoList.innerHTML = ''; performSearch(UI.search.value); }
});

UI.btnSurprise.addEventListener('click', async () => {
    UI.results.innerHTML = ''; UI.loading.classList.remove('hidden'); SynthEngine.play('click');
    try {
        const res = await fetch('/api/surprise');
        const data = await res.json(); UI.search.value = data.source.Name; renderResults(data.results); SynthEngine.play('success');
    } catch (err) { handleServerError(); } finally { UI.loading.classList.add('hidden'); }
});

UI.btnInfo.addEventListener('click', () => { SynthEngine.play('click'); UI.modalInfo.classList.remove('hidden'); });
UI.modalCloses.forEach(btn => btn.addEventListener('click', () => { UI.modalChart.classList.add('hidden'); UI.modalInfo.classList.add('hidden'); }));

UI.results.addEventListener('click', (e) => {
    if (e.target.classList.contains('btn-chart')) {
        const game = currentResultsData.get(e.target.getAttribute('data-id'));
        if (game) updateChartData(game.Name, game.breakdown);
    }
});

Inputs.sliders.forEach(id => {
    const el = document.getElementById(id);
    if(el) {
        const valEl = document.getElementById(id.replace('w_', 'val-'));
        el.addEventListener('input', (e) => { if(valEl) valEl.textContent = parseFloat(e.target.value).toFixed(2); });
        el.addEventListener('change', () => { if (UI.search.value) performSearch(UI.search.value); });
    }
});

document.addEventListener('click', (e) => { 
    SynthEngine.init(); 
    if(e.target !== UI.search) UI.autoList.innerHTML = '';
}, { once: false });
document.addEventListener('DOMContentLoaded', () => initChart());