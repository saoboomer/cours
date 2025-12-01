// PRONOTE Grade Analyzer - Frontend Application
const API_BASE_URL = 'http://localhost:5000/api';

// Add connection check on load
window.addEventListener('load', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, { 
            method: 'GET',
            signal: AbortSignal.timeout(5000) // 5 second timeout
        });
        if (response.ok) {
            console.log('✅ Backend connected successfully');
        } else {
            console.error('⚠️ Backend responded with error:', response.status);
            showConnectionError();
        }
    } catch (error) {
        console.error('❌ Cannot connect to backend:', error);
        showConnectionError();
    }
});

function showConnectionError() {
    const loginError = document.getElementById('login-error');
    if (loginError) {
        loginError.innerHTML = `
            <strong>⚠️ Serveur backend non disponible</strong><br>
            Assurez-vous que le serveur est démarré sur http://localhost:5000<br>
            <small>Exécutez: <code>cd backend && python app.py</code></small>
        `;
        loginError.style.display = 'block';
    }
}

// State management
const state = {
    token: null,
    student: null,
    grades: [],
    periods: [],
    subjects: new Set(),
    currentPeriod: null,
    selectedSchool: null,
    offlineMode: false,
    averages: null
};

// DOM Elements
const loginScreen = document.getElementById('login-screen');
const dashboardScreen = document.getElementById('dashboard-screen');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');
const studentNameEl = document.getElementById('student-name');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupSchoolSelector();
    checkExistingSession();
});

function setupEventListeners() {
    // Login form
    loginForm.addEventListener('submit', handleLogin);
    
    // Logout button
    logoutBtn.addEventListener('click', handleLogout);
    
    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });
    
    // Prediction forms
    document.getElementById('needed-grade-form').addEventListener('submit', handleNeededGrade);
    document.getElementById('simulate-grades-form').addEventListener('submit', handleSimulateGrades);
    
    // Filters
    document.getElementById('period-filter').addEventListener('change', filterGrades);
    document.getElementById('subject-filter').addEventListener('change', filterGrades);

    // Offline JSON controls
    const offlineFile = document.getElementById('offline-file');
    const offlineLoadFileBtn = document.getElementById('offline-load-file');
    const offlineLoadTextBtn = document.getElementById('offline-load-text');
    if (offlineFile && offlineLoadFileBtn && offlineLoadTextBtn) {
        offlineLoadFileBtn.addEventListener('click', async () => {
            const file = offlineFile.files && offlineFile.files[0];
            if (!file) return showOfflineError('Aucun fichier sélectionné.');
            try {
                const text = await file.text();
                handleOfflineJson(text);
            } catch (e) {
                showOfflineError('Lecture du fichier impossible.');
            }
        });
        offlineLoadTextBtn.addEventListener('click', () => {
            const ta = document.getElementById('offline-textarea');
            if (!ta || !ta.value.trim()) return showOfflineError('Collez le JSON dans la zone.');
            handleOfflineJson(ta.value);
        });
    }

    // New what-if tool
    const whatIfForm = document.getElementById('whatif-form');
    if (whatIfForm) whatIfForm.addEventListener('submit', handleWhatIf);
}

function showOfflineError(msg) {
    const el = document.getElementById('offline-error');
    if (!el) return;
    el.textContent = msg;
    el.style.display = 'block';
}

function clearOfflineError() {
    const el = document.getElementById('offline-error');
    if (!el) return;
    el.style.display = 'none';
    el.textContent = '';
}

function handleOfflineJson(text) {
    clearOfflineError();
    let json;
    try {
        json = JSON.parse(sanitizeJsonText(text));
    } catch (e) {
        return showOfflineError('JSON invalide.');
    }
    try {
        loadOfflineDataIntoState(json);
        state.offlineMode = true;
        state.token = 'offline';
        state.student = { name: 'Mode Offline' };
        showScreen('dashboard');
        // Directly render without backend
        populateSubjectsAndFilters();
        renderOverview();
        renderGradesList();
    } catch (e) {
        console.error(e);
        showOfflineError('Erreur lors du chargement des données.');
    }
}

function sanitizeJsonText(text) {
    if (!text) return text;
    // Strip BOM
    if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);
    // Fix common typo from dumps: "falsea" -> "false"
    text = text.replace(/\bfalsea\b/g, 'false');
    return text;
}

// Offline parsing and computations
function parseNum(v) {
    if (v == null) return null;
    if (typeof v === 'number') return Number.isFinite(v) ? v : null;
    const s = typeof v === 'string' ? v : v.V;
    if (s == null) return null;
    if (typeof s !== 'string') return null;
    if (s.startsWith('|')) return null;
    const n = Number(s.replace(',', '.'));
    return Number.isFinite(n) ? n : null;
}

function normalizeCoef(c) {
    if (c == null) return 1;
    if (typeof c === 'number') return c;
    if (typeof c === 'object') {
        if (typeof c.parsedValue === 'number') return c.parsedValue;
        if (typeof c.source === 'string') {
            const n = Number(c.source);
            return Number.isFinite(n) ? n : 1;
        }
        return 1;
    }
    const n = Number(c);
    return Number.isFinite(n) ? n : 1;
}

function to20(value, scale) {
    const v = parseNum(value);
    const s = parseNum(scale) ?? 20;
    if (v == null || s == null || s === 0) return null;
    return (v / s) * 20;
}

function loadOfflineDataIntoState(json) {
    const root = json?.dataSec?.data ?? {};
    const services = (root.listeServices?.V ?? []).map(s => ({
        id: s.N,
        label: s.L,
        givenAvg20: to20(s.moyEleve, s.baremeMoyEleve ?? 20)
    }));
    const assignments = (root.listeDevoirs?.V ?? []).map(d => ({
        id: d.N,
        subject: d.service?.V?.L ?? 'Inconnu',
        serviceId: d.service?.V?.N ?? null,
        date: d.date?.V ?? null,
        note20: to20(d.note, d.bareme ?? 20),
        gradeRaw: parseNum(d.note),
        outOfRaw: parseNum(d.bareme) ?? 20,
        coefficient: normalizeCoef(d.coefficient),
        class_average: parseNum(d.moyenne),
        min: parseNum(d.noteMin),
        max: parseNum(d.noteMax),
        optional: d.estFacultatif === true,
        bonus: d.estBonus === true,
        comment: d.commentaire || ''
    }));

    // Build frontend state's grades shape
    state.grades = assignments.map(a => ({
        subject: a.subject,
        date: a.date,
        grade: a.gradeRaw ?? (a.note20 != null ? Math.round((a.note20 / 20) * (a.outOfRaw ?? 20) * 100) / 100 : null),
        out_of: a.outOfRaw ?? 20,
        coefficient: a.coefficient,
        comment: a.comment,
        class_average: a.class_average != null ? a.class_average : null,
        min: a.min != null ? a.min : null,
        max: a.max != null ? a.max : null,
        optional: a.optional,
        bonus: a.bonus
    })).filter(g => g.grade != null);

    state.subjects = new Set(state.grades.map(g => g.subject));

    // Averages
    const overall = parseNum(root.moyGenerale);
    const classOverall = parseNum(root.moyGeneraleClasse);
    state.averages = {
        overall_average: overall != null ? format20(overall) : '--',
        class_overall_average: classOverall != null ? format20(classOverall) : '--'
    };
}

function populateSubjectsAndFilters() {
    const subjectFilter = document.getElementById('subject-filter');
    const ngSubject = document.getElementById('ng-subject');
    const sgSubject = document.getElementById('sg-subject');
    if (subjectFilter) subjectFilter.innerHTML = '<option value="">Toutes les matières</option>';
    if (ngSubject) ngSubject.innerHTML = '<option value="">Sélectionner...</option>';
    if (sgSubject) sgSubject.innerHTML = '<option value="">Sélectionner...</option>';
    Array.from(state.subjects).sort().forEach(subject => {
        if (subjectFilter) {
            const opt = document.createElement('option');
            opt.value = subject; opt.textContent = subject; subjectFilter.appendChild(opt);
        }
        if (ngSubject) {
            const opt2 = document.createElement('option');
            opt2.value = subject; opt2.textContent = subject; ngSubject.appendChild(opt2);
        }
        if (sgSubject) {
            const opt3 = document.createElement('option');
            opt3.value = subject; opt3.textContent = subject; sgSubject.appendChild(opt3);
        }
    });
}

function format20(x) {
    if (x == null || !Number.isFinite(x)) return '--';
    return (Math.round(x * 100) / 100).toFixed(2);
}

// School Selector Setup
function setupSchoolSelector() {
    // Selector tabs
    document.querySelectorAll('.selector-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            const mode = e.target.dataset.mode;
            switchSelectorMode(mode);
        });
    });
    
    // Search mode
    const searchInput = document.getElementById('school-search');
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => searchSchools(e.target.value), 300);
    });
    
    // Browse mode - load regions
    loadRegions();
    
    document.getElementById('region-select').addEventListener('change', (e) => {
        loadCities(e.target.value);
    });
    
    document.getElementById('city-select').addEventListener('change', (e) => {
        const region = document.getElementById('region-select').value;
        loadSchools(region, e.target.value);
    });
    
    document.getElementById('school-select').addEventListener('change', (e) => {
        const selectedOption = e.target.options[e.target.selectedIndex];
        if (selectedOption.value) {
            selectSchool({
                url: selectedOption.dataset.url,
                ent: selectedOption.dataset.ent
            });
        }
    });
}

function switchSelectorMode(mode) {
    document.querySelectorAll('.selector-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.selector-content').forEach(content => content.classList.remove('active'));
    
    document.querySelector(`[data-mode="${mode}"]`).classList.add('active');
    document.getElementById(`${mode}-mode`).classList.add('active');
}

async function searchSchools(query) {
    if (query.length < 2) {
        document.getElementById('search-results').style.display = 'none';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/schools/search?q=${encodeURIComponent(query)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const schools = await response.json();
        console.log('Search results:', schools); // Debug log
        displaySearchResults(schools);
    } catch (error) {
        console.error('Search error:', error);
        // Show error in UI
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = `<div class="search-result-item" style="color: var(--danger);">Erreur de connexion au serveur. Assurez-vous que le backend est démarré.</div>`;
        resultsContainer.style.display = 'block';
    }
}

function displaySearchResults(schools) {
    const resultsContainer = document.getElementById('search-results');
    
    if (!schools || schools.length === 0) {
        resultsContainer.innerHTML = `<div class="search-result-item" style="color: var(--text-secondary);">Aucun résultat trouvé</div>`;
        resultsContainer.style.display = 'block';
        return;
    }
    
    resultsContainer.innerHTML = schools.map(school => {
        const schoolData = JSON.stringify(school).replace(/"/g, '&quot;');
        return `
            <div class="search-result-item" onclick='selectSchoolFromSearch(${schoolData})'>
                <div class="search-result-name">${school.name}</div>
                <div class="search-result-location">${school.city}, ${school.region}</div>
            </div>
        `;
    }).join('');
    
    resultsContainer.style.display = 'block';
}

window.selectSchoolFromSearch = function(school) {
    selectSchool(school);
    document.getElementById('search-results').style.display = 'none';
    document.getElementById('school-search').value = school.name;
}

function selectSchool(school) {
    state.selectedSchool = school;
    document.getElementById('pronote-url').value = school.url;
    if (school.ent) {
        document.getElementById('ent').value = school.ent;
    }
}

async function loadRegions() {
    try {
        const response = await fetch(`${API_BASE_URL}/schools/regions`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const regions = await response.json();
        console.log('Loaded regions:', regions); // Debug
        
        const select = document.getElementById('region-select');
        select.innerHTML = '<option value="">Sélectionner une région...</option>';
        
        regions.forEach(region => {
            const option = document.createElement('option');
            option.value = region;
            option.textContent = region;
            select.appendChild(option);
        });
        
        console.log('Regions loaded successfully:', regions.length);
    } catch (error) {
        console.error('Error loading regions:', error);
        const select = document.getElementById('region-select');
        select.innerHTML = '<option value="">Erreur de chargement - Vérifiez le serveur</option>';
    }
}

async function loadCities(region) {
    const citySelect = document.getElementById('city-select');
    const schoolSelect = document.getElementById('school-select');
    
    if (!region) {
        citySelect.disabled = true;
        citySelect.innerHTML = '<option value="">Sélectionner d\'abord une région...</option>';
        schoolSelect.disabled = true;
        schoolSelect.innerHTML = '<option value="">Sélectionner d\'abord une ville...</option>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/schools/cities?region=${encodeURIComponent(region)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const cities = await response.json();
        console.log('Loaded cities for', region, ':', cities);
        
        citySelect.innerHTML = '<option value="">Sélectionner une ville...</option>';
        cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
        
        citySelect.disabled = false;
        schoolSelect.disabled = true;
        schoolSelect.innerHTML = '<option value="">Sélectionner d\'abord une ville...</option>';
    } catch (error) {
        console.error('Error loading cities:', error);
        citySelect.innerHTML = '<option value="">Erreur de chargement</option>';
    }
}

async function loadSchools(region, city) {
    const schoolSelect = document.getElementById('school-select');
    
    if (!region || !city) {
        schoolSelect.disabled = true;
        schoolSelect.innerHTML = '<option value="">Sélectionner d\'abord une ville...</option>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/schools/list?region=${encodeURIComponent(region)}&city=${encodeURIComponent(city)}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const schools = await response.json();
        console.log('Loaded schools for', city, ':', schools);
        
        schoolSelect.innerHTML = '<option value="">Sélectionner un établissement...</option>';
        schools.forEach(school => {
            const option = document.createElement('option');
            option.value = school.name;
            option.dataset.url = school.url;
            option.dataset.ent = school.ent || '';
            option.textContent = school.name;
            schoolSelect.appendChild(option);
        });
        
        schoolSelect.disabled = false;
    } catch (error) {
        console.error('Error loading schools:', error);
        schoolSelect.innerHTML = '<option value="">Erreur de chargement</option>';
    }
}

function checkExistingSession() {
    const token = localStorage.getItem('pronote_token');
    if (token) {
        state.token = token;
        loadDashboard();
    }
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    
    const submitBtn = loginForm.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoader = submitBtn.querySelector('.btn-loader');
    
    btnText.style.display = 'none';
    btnLoader.style.display = 'block';
    submitBtn.disabled = true;
    loginError.style.display = 'none';
    
    const credentials = {
        url: document.getElementById('pronote-url').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        ent: document.getElementById('ent').value || undefined
    };
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        const data = await response.json();
        
        if (!response.ok) {
            // Provide more helpful error messages
            let errorMessage = data.error || 'Login failed';
            
            if (errorMessage.includes('Authentication failed')) {
                errorMessage = `
                    🔐 Authentication Failed<br>
                    Please check:<br>
                    • URL format (should end with /pronote/eleve.html)<br>
                    • Username and password<br>
                    • ENT identifier (if your school uses regional auth)
                `;
            } else if (errorMessage.includes('ENT')) {
                errorMessage = `
                    🏫 ENT Error<br>
                    Check your ENT identifier. Common ones:<br>
                    • ac_rennes, ac_paris, ac_lyon<br>
                    • ac_bordeaux, ac_toulouse<br>
                    Leave empty if you don't use ENT
                `;
            } else if (errorMessage.includes('connection') || errorMessage.includes('timeout')) {
                errorMessage = `
                    🌐 Connection Error<br>
                    • Check your internet connection<br>
                    • Verify PRONOTE server is accessible<br>
                    • Try again in a few minutes
                `;
            }
            
            throw new Error(errorMessage);
        }
        
        state.token = data.token;
        state.student = data.student;
        localStorage.setItem('pronote_token', data.token);
        
        showScreen('dashboard');
        loadDashboard();
        
    } catch (error) {
        if (error.name === 'AbortError') {
            loginError.innerHTML = '⏱️ Délai d\'attente dépassé. Vérifiez votre connexion PRONOTE.';
        } else {
            // Check if error message contains HTML
            if (error.message.includes('<br>')) {
                loginError.innerHTML = error.message;
            } else {
                loginError.textContent = error.message;
            }
        }
        loginError.style.display = 'block';
    } finally {
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
        submitBtn.disabled = false;
    }
}

async function handleLogout() {
    try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: { 'Authorization': state.token }
        });
    } catch (error) {
        console.error('Logout error:', error);
    }
    
    localStorage.removeItem('pronote_token');
    state.token = null;
    state.student = null;
    state.grades = [];
    showScreen('login');
}

// Screen management
function showScreen(screen) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(`${screen}-screen`).classList.add('active');
}

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Load tab-specific data
    if (tabName === 'analysis') {
        loadAnalysis();
    } else if (tabName === 'predictions') {
        loadPredictions();
    } else if (tabName === 'advanced') {
        loadAdvancedAnalytics();
    }
}

// Advanced Analytics Loading
async function loadAdvancedAnalytics() {
    try {
        // Load GPA Projection
        const gpaResponse = await fetch(`${API_BASE_URL}/advanced/gpa-projection`, {
            headers: { 'Authorization': state.token }
        });
        const gpaData = await gpaResponse.json();
        
        document.getElementById('gpa-projection').textContent = gpaData.projected_gpa || '--';
        const changeEl = document.getElementById('gpa-change');
        if (gpaData.change) {
            const sign = gpaData.change > 0 ? '+' : '';
            changeEl.textContent = `${sign}${gpaData.change} points`;
            changeEl.style.color = gpaData.change > 0 ? 'var(--success)' : 'var(--danger)';
        }
        
        // Load Correlations
        const corrResponse = await fetch(`${API_BASE_URL}/advanced/correlations`, {
            headers: { 'Authorization': state.token }
        });
        const corrData = await corrResponse.json();
        
        if (corrData.strongest_correlation) {
            const corr = corrData.strongest_correlation;
            document.getElementById('strongest-corr').textContent = 
                `${corr.subject1} ↔ ${corr.subject2} (${corr.correlation > 0 ? '+' : ''}${corr.correlation})`;
        }
        
        // Load detailed analytics for each subject
        renderAdvancedAnalytics();
        
    } catch (error) {
        console.error('Advanced analytics loading error:', error);
    }
}

async function renderAdvancedAnalytics() {
    const container = document.getElementById('advanced-analytics-container');
    container.innerHTML = '<h3 style="margin: 2rem 0 1rem; font-size: 1.5rem;">Analyse par matière</h3>';
    
    for (const subject of state.subjects) {
        const card = document.createElement('div');
        card.className = 'stats-card glass';
        card.style.marginBottom = '1.5rem';
        
        try {
            // Fetch all metrics for this subject
            const [consistency, improvement, volatility, benchmark, forecast, efficiency] = await Promise.all([
                fetch(`${API_BASE_URL}/advanced/consistency?subject=${encodeURIComponent(subject)}`, {
                    headers: { 'Authorization': state.token }
                }).then(r => r.json()),
                fetch(`${API_BASE_URL}/advanced/improvement-rate?subject=${encodeURIComponent(subject)}`, {
                    headers: { 'Authorization': state.token }
                }).then(r => r.json()),
                fetch(`${API_BASE_URL}/advanced/volatility?subject=${encodeURIComponent(subject)}`, {
                    headers: { 'Authorization': state.token }
                }).then(r => r.json()),
                fetch(`${API_BASE_URL}/advanced/benchmark?subject=${encodeURIComponent(subject)}`, {
                    headers: { 'Authorization': state.token }
                }).then(r => r.json()),
                fetch(`${API_BASE_URL}/advanced/forecast?subject=${encodeURIComponent(subject)}`, {
                    headers: { 'Authorization': state.token }
                }).then(r => r.json()),
                fetch(`${API_BASE_URL}/advanced/learning-efficiency?subject=${encodeURIComponent(subject)}`, {
                    headers: { 'Authorization': state.token }
                }).then(r => r.json())
            ]);
            
            card.innerHTML = `
                <h3 style="margin-bottom: 1.5rem; font-size: 1.25rem;">${subject}</h3>
                <div class="stats-grid-detailed">
                    <div class="subject-stat">
                        <div class="subject-stat-label">Consistance</div>
                        <div class="subject-stat-value">${consistency.consistency_score || 0}/100</div>
                        <small style="color: var(--text-tertiary);">${consistency.stability || 'N/A'}</small>
                    </div>
                    <div class="subject-stat">
                        <div class="subject-stat-label">Amélioration/mois</div>
                        <div class="subject-stat-value" style="color: ${improvement.rate_per_month > 0 ? 'var(--success)' : 'var(--danger)'}">
                            ${improvement.rate_per_month > 0 ? '+' : ''}${improvement.rate_per_month || 0}
                        </div>
                    </div>
                    <div class="subject-stat">
                        <div class="subject-stat-label">Volatilité (High Stakes)</div>
                        <div class="subject-stat-value">${volatility.high_stakes?.std_dev || 0}</div>
                    </div>
                    <div class="subject-stat">
                        <div class="subject-stat-label">vs Classe</div>
                        <div class="subject-stat-value" style="color: ${benchmark.average_difference > 0 ? 'var(--success)' : 'var(--danger)'}">
                            ${benchmark.average_difference > 0 ? '+' : ''}${benchmark.average_difference || 0}
                        </div>
                    </div>
                    <div class="subject-stat">
                        <div class="subject-stat-label">Prédiction</div>
                        <div class="subject-stat-value">${forecast.prediction || '--'}/20</div>
                        <small style="color: var(--text-tertiary);">±${forecast.margin_of_error || 0}</small>
                    </div>
                    <div class="subject-stat">
                        <div class="subject-stat-label">Efficacité</div>
                        <div class="subject-stat-value">${efficiency.efficiency_index || 0}</div>
                        <small style="color: var(--text-tertiary);">${efficiency.rating || 'N/A'}</small>
                    </div>
                </div>
            `;
            
            container.appendChild(card);
            
        } catch (error) {
            console.error(`Error loading analytics for ${subject}:`, error);
        }
    }
}

// Dashboard loading
async function loadDashboard() {
    try {
        studentNameEl.textContent = state.student?.name || 'Chargement...';
        if (state.offlineMode) {
            // Offline: data already in state
            populateSubjectsAndFilters();
            renderOverview();
            renderGradesList();
            return;
        }
        await Promise.all([
            loadPeriods(),
            loadGrades(),
            loadAverages()
        ]);
        renderOverview();
        renderGradesList();
    } catch (error) {
        console.error('Dashboard loading error:', error);
        if (error.message.includes('Unauthorized')) {
            handleLogout();
        }
    }
}

async function loadPeriods() {
    const response = await fetch(`${API_BASE_URL}/periods`, {
        headers: { 'Authorization': state.token }
    });
    
    if (!response.ok) throw new Error('Failed to load periods');
    
    state.periods = await response.json();
    
    // Populate period filter
    const periodFilter = document.getElementById('period-filter');
    periodFilter.innerHTML = '<option value="">Toutes les périodes</option>';
    state.periods.forEach(period => {
        const option = document.createElement('option');
        option.value = period.name;
        option.textContent = period.name;
        periodFilter.appendChild(option);
    });
}

async function loadGrades() {
    const response = await fetch(`${API_BASE_URL}/grades`, {
        headers: { 'Authorization': state.token }
    });
    
    if (!response.ok) throw new Error('Failed to load grades');
    
    state.grades = await response.json();
    
    // Extract unique subjects
    state.subjects = new Set(state.grades.map(g => g.subject));
    
    // Populate subject filter and prediction forms
    const subjectFilter = document.getElementById('subject-filter');
    const ngSubject = document.getElementById('ng-subject');
    const sgSubject = document.getElementById('sg-subject');
    
    subjectFilter.innerHTML = '<option value="">Toutes les matières</option>';
    ngSubject.innerHTML = '<option value="">Sélectionner...</option>';
    sgSubject.innerHTML = '<option value="">Sélectionner...</option>';
    
    Array.from(state.subjects).sort().forEach(subject => {
        const option1 = document.createElement('option');
        option1.value = subject;
        option1.textContent = subject;
        subjectFilter.appendChild(option1);
        
        const option2 = option1.cloneNode(true);
        const option3 = option1.cloneNode(true);
        ngSubject.appendChild(option2);
        sgSubject.appendChild(option3);
    });
}

async function loadAverages() {
    const response = await fetch(`${API_BASE_URL}/averages`, {
        headers: { 'Authorization': state.token }
    });
    
    if (!response.ok) throw new Error('Failed to load averages');
    
    state.averages = await response.json();
}

// Overview rendering
function renderOverview() {
    document.getElementById('overall-average').textContent = 
        state.averages?.overall_average || '--';
    document.getElementById('class-average').textContent = 
        state.averages?.class_overall_average || '--';
    document.getElementById('subject-count').textContent = state.subjects.size;
    document.getElementById('total-grades').textContent = state.grades.length;

    if (state.offlineMode) {
        const comparison = computeOfflineComparison();
        renderSubjectsChart(comparison);
        renderSubjectsList(comparison);
    } else {
        loadSubjectComparison();
    }
}

function computeOfflineComparison() {
    const by = {};
    for (const g of state.grades) {
        if (g.optional) continue;
        const key = g.subject;
        const coef = Math.max(0, g.coefficient || 1);
        if (!by[key]) by[key] = { subject: key, num: 0, den: 0, count: 0, values: [] };
        const v20 = (g.grade / (g.out_of || 20)) * 20;
        by[key].num += v20 * coef;
        by[key].den += coef;
        by[key].count += 1;
        by[key].values.push(v20);
    }
    const res = Object.values(by).map(x => {
        const avg = x.den > 0 ? x.num / x.den : null;
        const mean = avg || 0;
        const sd = x.values.length > 1 ? Math.sqrt(x.values.reduce((s, v) => s + Math.pow(v - mean, 2), 0) / (x.values.length - 1)) : 0;
        return {
            subject: x.subject,
            average: avg || 0,
            grade_count: x.count,
            std_dev: sd,
            trend: 'stable'
        };
    });
    return res.sort((a, b) => a.subject.localeCompare(b.subject));
}

async function loadSubjectComparison() {
    try {
        const response = await fetch(`${API_BASE_URL}/analysis/comparison`, {
            headers: { 'Authorization': state.token }
        });
        
        if (!response.ok) throw new Error('Failed to load comparison');
        
        const comparison = await response.json();
        
        renderSubjectsChart(comparison);
        renderSubjectsList(comparison);
        
    } catch (error) {
        console.error('Comparison loading error:', error);
    }
}

function renderSubjectsChart(comparison) {
    const ctx = document.getElementById('subjects-chart');
    
    if (window.subjectsChart) {
        window.subjectsChart.destroy();
    }
    
    window.subjectsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: comparison.map(c => c.subject),
            datasets: [{
                label: 'Moyenne',
                data: comparison.map(c => c.average),
                backgroundColor: 'rgba(79, 70, 229, 0.8)',
                borderColor: 'rgba(79, 70, 229, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 20,
                    ticks: {
                        stepSize: 5
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function renderSubjectsList(comparison) {
    const container = document.getElementById('subjects-comparison');
    container.innerHTML = '';
    
    comparison.forEach(subject => {
        const item = document.createElement('div');
        item.className = 'subject-item';
        
        const trendClass = `trend-${subject.trend}`;
        const trendIcon = subject.trend === 'improving' ? '↗' : 
                         subject.trend === 'declining' ? '↘' : '→';
        
        item.innerHTML = `
            <div class="subject-name">${subject.subject}</div>
            <div class="subject-stat">
                <div class="subject-stat-label">Moyenne</div>
                <div class="subject-stat-value">${subject.average.toFixed(2)}/20</div>
            </div>
            <div class="subject-stat">
                <div class="subject-stat-label">Notes</div>
                <div class="subject-stat-value">${subject.grade_count}</div>
            </div>
            <div class="subject-stat">
                <div class="subject-stat-label">Écart-type</div>
                <div class="subject-stat-value">${subject.std_dev.toFixed(2)}</div>
            </div>
            <div class="subject-stat">
                <div class="subject-stat-label">Tendance</div>
                <span class="trend-badge ${trendClass}">${trendIcon} ${subject.trend}</span>
            </div>
        `;
        
        container.appendChild(item);
    });
}

// Grades list rendering
function filterGrades() {
    renderGradesList();
}

function renderGradesList() {
    const container = document.getElementById('grades-list');
    const periodFilter = document.getElementById('period-filter').value;
    const subjectFilter = document.getElementById('subject-filter').value;
    
    let filteredGrades = state.grades;
    
    if (subjectFilter) {
        filteredGrades = filteredGrades.filter(g => g.subject === subjectFilter);
    }
    
    container.innerHTML = '';
    
    if (filteredGrades.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Aucune note trouvée</p>';
        return;
    }
    
    filteredGrades.forEach(grade => {
        const card = document.createElement('div');
        card.className = 'grade-card';
        
        card.innerHTML = `
            <div class="grade-header">
                <div>
                    <div class="grade-subject">${grade.subject}</div>
                    <div class="grade-date">${formatDate(grade.date)}</div>
                </div>
                <div class="grade-value">${grade.grade}/${grade.out_of}</div>
            </div>
            ${grade.comment ? `<p style="color: var(--text-secondary); margin-bottom: 1rem;">${grade.comment}</p>` : ''}
            <div class="grade-details">
                <div class="grade-detail">
                    <span class="grade-detail-label">Coefficient</span>
                    <span class="grade-detail-value">${grade.coefficient || 1}</span>
                </div>
                <div class="grade-detail">
                    <span class="grade-detail-label">Moyenne classe</span>
                    <span class="grade-detail-value">${grade.class_average || 'N/A'}</span>
                </div>
                <div class="grade-detail">
                    <span class="grade-detail-label">Note min</span>
                    <span class="grade-detail-value">${grade.min || 'N/A'}</span>
                </div>
                <div class="grade-detail">
                    <span class="grade-detail-label">Note max</span>
                    <span class="grade-detail-value">${grade.max || 'N/A'}</span>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

// Analysis tab
async function loadAnalysis() {
    await loadStatistics();
    await loadTrends();
}

async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/analysis/statistics`, {
            headers: { 'Authorization': state.token }
        });
        
        if (!response.ok) throw new Error('Failed to load statistics');
        
        const stats = await response.json();
        renderStatistics(stats);
        
    } catch (error) {
        console.error('Statistics loading error:', error);
    }
}

function renderStatistics(stats) {
    const container = document.getElementById('statistics-container');
    container.innerHTML = '';
    
    Object.entries(stats).forEach(([subject, data]) => {
        const card = document.createElement('div');
        card.className = 'stats-card';
        
        card.innerHTML = `
            <h3>${subject}</h3>
            <div class="stats-grid-detailed">
                <div class="subject-stat">
                    <div class="subject-stat-label">Moyenne</div>
                    <div class="subject-stat-value">${data.average.toFixed(2)}</div>
                </div>
                <div class="subject-stat">
                    <div class="subject-stat-label">Médiane</div>
                    <div class="subject-stat-value">${data.median.toFixed(2)}</div>
                </div>
                <div class="subject-stat">
                    <div class="subject-stat-label">Écart-type</div>
                    <div class="subject-stat-value">${data.std_dev.toFixed(2)}</div>
                </div>
                <div class="subject-stat">
                    <div class="subject-stat-label">Min</div>
                    <div class="subject-stat-value">${data.min.toFixed(2)}</div>
                </div>
                <div class="subject-stat">
                    <div class="subject-stat-label">Max</div>
                    <div class="subject-stat-value">${data.max.toFixed(2)}</div>
                </div>
                <div class="subject-stat">
                    <div class="subject-stat-label">Nombre</div>
                    <div class="subject-stat-value">${data.count}</div>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
}

async function loadTrends() {
    const container = document.getElementById('trends-container');
    container.innerHTML = '';
    
    for (const subject of state.subjects) {
        try {
            const response = await fetch(
                `${API_BASE_URL}/analysis/trends?subject=${encodeURIComponent(subject)}`,
                { headers: { 'Authorization': state.token } }
            );
            
            if (!response.ok) continue;
            
            const trend = await response.json();
            
            const card = document.createElement('div');
            card.className = 'stats-card';
            
            const trendClass = `trend-${trend.trend}`;
            const trendIcon = trend.trend === 'improving' ? '↗' : 
                             trend.trend === 'declining' ? '↘' : '→';
            
            card.innerHTML = `
                <h3>${subject}</h3>
                <div class="stats-grid-detailed">
                    <div class="subject-stat">
                        <div class="subject-stat-label">Tendance</div>
                        <span class="trend-badge ${trendClass}">${trendIcon} ${trend.trend}</span>
                    </div>
                    <div class="subject-stat">
                        <div class="subject-stat-label">Confiance</div>
                        <div class="subject-stat-value">${trend.confidence}%</div>
                    </div>
                    ${trend.prediction ? `
                    <div class="subject-stat">
                        <div class="subject-stat-label">Prédiction</div>
                        <div class="subject-stat-value">${trend.prediction}/20</div>
                    </div>
                    ` : ''}
                </div>
            `;
            
            container.appendChild(card);
            
        } catch (error) {
            console.error(`Trend loading error for ${subject}:`, error);
        }
    }
}

// Predictions tab
function loadPredictions() {
    // Already loaded via subject selects
}

async function handleNeededGrade(e) {
    e.preventDefault();
    
    const subject = document.getElementById('ng-subject').value;
    const target = parseFloat(document.getElementById('ng-target').value);
    const coef = parseFloat(document.getElementById('ng-coef').value);
    const outOf = parseFloat(document.getElementById('ng-outof').value);
    
    try {
        if (state.offlineMode) {
            const result = computeNeededGradeLocal({ subject, target, coef, outOf });
            return displayNeededGradeResult(result);
        }
        const response = await fetch(`${API_BASE_URL}/analysis/needed-grade`, {
            method: 'POST',
            headers: {
                'Authorization': state.token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subject,
                target_average: target,
                coefficient: coef,
                out_of: outOf
            })
        });
        
        if (!response.ok) throw new Error('Calculation failed');
        
        const result = await response.json();
        displayNeededGradeResult(result);
        
    } catch (error) {
        console.error('Needed grade calculation error:', error);
    }
}

function displayNeededGradeResult(result) {
    const container = document.getElementById('needed-grade-result');
    container.style.display = 'block';
    
    const resultClass = result.is_possible ? 
        (result.difficulty === 'easy' ? 'success' : 'warning') : 'danger';
    
    container.className = `result-box ${resultClass}`;
    
    const difficultyText = {
        'easy': 'Facile',
        'moderate': 'Modéré',
        'difficult': 'Difficile',
        'impossible': 'Impossible'
    };
    
    container.innerHTML = `
        <div class="result-title">
            ${result.is_possible ? '✓ Objectif atteignable' : '✗ Objectif non atteignable'}
        </div>
        <div class="result-value">${result.needed_grade.toFixed(2)}/${result.out_of}</div>
        <div class="result-details">
            <div class="result-detail">
                <span>Note nécessaire (normalisée)</span>
                <strong>${result.normalized_needed.toFixed(2)}/20</strong>
            </div>
            <div class="result-detail">
                <span>Moyenne actuelle</span>
                <strong>${result.current_average.toFixed(2)}/20</strong>
            </div>
            <div class="result-detail">
                <span>Moyenne visée</span>
                <strong>${result.target_average.toFixed(2)}/20</strong>
            </div>
            <div class="result-detail">
                <span>Difficulté</span>
                <strong>${difficultyText[result.difficulty]}</strong>
            </div>
        </div>
    `;
}

async function handleSimulateGrades(e) {
    e.preventDefault();
    
    const subject = document.getElementById('sg-subject').value;
    const target = parseFloat(document.getElementById('sg-target').value);
    const num = parseInt(document.getElementById('sg-num').value);
    const coef = parseFloat(document.getElementById('sg-coef').value);
    
    try {
        if (state.offlineMode) {
            const result = computeSimulateGradesLocal({ subject, target, num, coef });
            return displaySimulateGradesResult(result);
        }
        const response = await fetch(`${API_BASE_URL}/analysis/simulate-grades`, {
            method: 'POST',
            headers: {
                'Authorization': state.token,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subject,
                target_average: target,
                num_grades: num,
                coefficient: coef,
                out_of: 20
            })
        });
        
        if (!response.ok) throw new Error('Simulation failed');
        
        const result = await response.json();
        displaySimulateGradesResult(result);
        
    } catch (error) {
        console.error('Simulate grades error:', error);
    }
}

// Local computations for analysis
function currentSubjectAverage20(subject) {
    const items = state.grades.filter(g => g.subject === subject && !g.optional);
    if (items.length === 0) return null;
    let num = 0, den = 0;
    for (const g of items) {
        const v20 = (g.grade / (g.out_of || 20)) * 20;
        const c = Math.max(0, g.coefficient || 1);
        if (g.bonus) {
            num += v20 * c; // bonus adds to numerator only
        } else {
            num += v20 * c;
            den += c;
        }
    }
    return den > 0 ? num / den : null;
}

function computeNeededGradeLocal({ subject, target, coef, outOf }) {
    const current = currentSubjectAverage20(subject) ?? 0;
    const c = Math.max(0.0001, coef || 1);
    const out = Math.max(1, outOf || 20);
    // Solve for x20: (current*W + x20*c) / (W + c) = target
    const pastItems = state.grades.filter(g => g.subject === subject && !g.optional && !g.bonus);
    let W = 0;
    for (const g of pastItems) W += Math.max(0, g.coefficient || 1);
    const x20 = (target * (W + c)) - (current * W);
    const needed20 = x20 / c;
    const neededRaw = (needed20 / 20) * out;
    const isPossible = needed20 <= 20 && needed20 >= 0;
    const difficulty = !isPossible ? 'impossible' : needed20 < current ? 'easy' : needed20 <= 15 ? 'moderate' : 'difficult';
    return {
        is_possible: isPossible,
        difficulty,
        needed_grade: neededRaw,
        out_of: out,
        normalized_needed: needed20,
        current_average: current,
        target_average: target
    };
}

function computeSimulateGradesLocal({ subject, target, num, coef }) {
    const current = currentSubjectAverage20(subject) ?? 0;
    const n = Math.max(1, num || 1);
    const c = Math.max(0.0001, coef || 1);
    const pastItems = state.grades.filter(g => g.subject === subject && !g.optional && !g.bonus);
    let W = 0;
    for (const g of pastItems) W += Math.max(0, g.coefficient || 1);
    // Let each of the n grades have the same normalized score y (out of 20)
    // (current*W + y*c*n) / (W + c*n) = target  => y = (target*(W + c*n) - current*W) / (c*n)
    const y = ((target * (W + c * n)) - (current * W)) / (c * n);
    const isPossible = y >= 0 && y <= 20;
    return {
        is_possible: isPossible,
        average_needed_per_grade: y,
        normalized_average: y,
        out_of: 20,
        num_grades: n,
        current_average: current
    };
}

// What-if tool (applies one hypothetical grade)
function handleWhatIf(e) {
    e.preventDefault();
    const subject = document.getElementById('wi-subject').value;
    const grade = parseFloat(document.getElementById('wi-grade').value);
    const outOf = parseFloat(document.getElementById('wi-outof').value);
    const coef = parseFloat(document.getElementById('wi-coef').value);
    const resultEl = document.getElementById('whatif-result');
    const items = state.grades.filter(g => g.subject === subject && !g.optional && !g.bonus);
    let num = 0, den = 0;
    for (const g of items) {
        const v20 = (g.grade / (g.out_of || 20)) * 20;
        const c = Math.max(0, g.coefficient || 1);
        num += v20 * c;
        den += c;
    }
    const v20 = (grade / (outOf || 20)) * 20;
    const c = Math.max(0, coef || 1);
    const newAvg = (num + v20 * c) / (den + c);
    resultEl.style.display = 'block';
    resultEl.className = 'result-box success';
    resultEl.innerHTML = `
        <div class="result-title">Nouvelle moyenne estimée</div>
        <div class="result-value">${newAvg.toFixed(2)}/20</div>
    `;
}

function displaySimulateGradesResult(result) {
    const container = document.getElementById('simulate-grades-result');
    container.style.display = 'block';
    
    const resultClass = result.is_possible ? 'success' : 'danger';
    
    container.className = `result-box ${resultClass}`;
    
    container.innerHTML = `
        <div class="result-title">
            ${result.is_possible ? '✓ Objectif atteignable' : '✗ Objectif non atteignable'}
        </div>
        <div class="result-value">${result.average_needed_per_grade.toFixed(2)}/${result.out_of}</div>
        <div class="result-details">
            <div class="result-detail">
                <span>Moyenne nécessaire par note</span>
                <strong>${result.normalized_average.toFixed(2)}/20</strong>
            </div>
            <div class="result-detail">
                <span>Nombre de notes</span>
                <strong>${result.num_grades}</strong>
            </div>
            <div class="result-detail">
                <span>Moyenne actuelle</span>
                <strong>${result.current_average.toFixed(2)}/20</strong>
            </div>
        </div>
    `;
}

// Utility functions
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}
