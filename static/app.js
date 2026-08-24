// ============================================
// DevGraph — Premium Frontend Logic
// ============================================

async function searchDeveloper() {
    const username = document.getElementById('username').value.trim();
    if (!username) {
        showError('Please enter a username');
        return;
    }

    showLoading(true);
    hideError();

    try {
        const [devRes, statsRes, followersRes, secondRes, langRes] = await Promise.all([
            fetch(`/api/developer/${encodeURIComponent(username)}`),
            fetch(`/api/network-stats/${encodeURIComponent(username)}`),
            fetch(`/api/followers/${encodeURIComponent(username)}`),
            fetch(`/api/second-degree/${encodeURIComponent(username)}`),
            fetch(`/api/language-network/${encodeURIComponent(username)}`)
        ]);

        if (devRes.status === 404) throw new Error('Developer not found');
        if (devRes.status === 400) {
            const errData = await devRes.json();
            throw new Error(errData.error || 'Invalid username');
        }
        if (!devRes.ok) throw new Error('Failed to fetch developer data');

        const dev = await devRes.json();
        const stats = statsRes.ok ? await statsRes.json() : {};
        const followers = followersRes.ok ? await followersRes.json() : [];
        const secondDegree = secondRes.ok ? await secondRes.json() : [];
        const langNetwork = langRes.ok ? await langRes.json() : [];

        renderProfile(dev, stats);
        renderFollowers(followers);
        renderSecondDegree(secondDegree);
        renderLanguageNetwork(langNetwork);
        showResults(true);

    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
}

// ---- Render Profile ----
function renderProfile(dev, stats) {
    const name = dev.name || dev.username;
    document.getElementById('profile-name').textContent = name;

    // Avatar initial
    const avatar = document.getElementById('profile-avatar');
    avatar.textContent = (name.charAt(0) || '?').toUpperCase();

    // Handle
    const handleEl = document.getElementById('profile-url');
    handleEl.textContent = `@${dev.username || ''}`;
    if (dev.profile_url) handleEl.href = dev.profile_url;

    // Stats
    document.getElementById('stat-followers').textContent = formatNumber(dev.followers || 0);
    document.getElementById('stat-direct').textContent = formatNumber(stats.direct_followers || 0);
    document.getElementById('stat-2nd').textContent = formatNumber(stats.second_degree || 0);
    document.getElementById('stat-langs').textContent = stats.languages || 0;
}

// ---- Render Followers ----
function renderFollowers(followers) {
    const grid = document.getElementById('followers-grid');
    const countEl = document.getElementById('followers-count');

    if (!followers || followers.length === 0) {
        grid.innerHTML = '<div class="empty-state">No followers loaded yet. Try searching a developer!</div>';
        countEl.textContent = '';
        return;
    }

    countEl.textContent = `${followers.length} loaded`;
    grid.innerHTML = followers.map((f, i) => `
        <div class="dev-card" style="animation-delay: ${i * 0.05}s">
            <div class="dev-card-name">@${escapeHtml(f.username || '')}</div>
            <div class="dev-card-meta">${formatNumber(f.followers || 0)} followers</div>
            ${f.profile_url ? `<a href="${escapeHtml(f.profile_url)}" target="_blank" rel="noopener noreferrer" class="dev-card-link">View Profile <span>→</span></a>` : ''}
        </div>
    `).join('');
}

// ---- Render Second Degree ----
function renderSecondDegree(results) {
    const grid = document.getElementById('second-degree-grid');
    const countEl = document.getElementById('second-count');

    if (!results || results.length === 0) {
        grid.innerHTML = '<div class="empty-state">No second-degree connections found yet.</div>';
        countEl.textContent = '';
        return;
    }

    countEl.textContent = `${results.length} found`;
    grid.innerHTML = results.map((r, i) => `
        <div class="dev-card" style="animation-delay: ${i * 0.05}s">
            <div class="dev-card-name">@${escapeHtml(r.username || '')}</div>
            <div class="dev-card-meta">
                <span class="tag tag-mutual">✨ ${r.mutual_connections} mutual</span>
            </div>
        </div>
    `).join('');
}

// ---- Render Language Network ----
function renderLanguageNetwork(results) {
    const grid = document.getElementById('language-grid');
    const countEl = document.getElementById('lang-count');

    if (!results || results.length === 0) {
        grid.innerHTML = '<div class="empty-state">No language network data found yet.</div>';
        countEl.textContent = '';
        return;
    }

    countEl.textContent = `${results.length} developers`;
    grid.innerHTML = results.map((r, i) => `
        <div class="dev-card" style="animation-delay: ${i * 0.05}s">
            <div class="dev-card-name">@${escapeHtml(r.username || '')}</div>
            <div class="dev-card-meta">${r.shared_languages} shared language${r.shared_languages !== 1 ? 's' : ''}</div>
            <div>
                ${(r.languages || []).map(l => `<span class="tag tag-lang">${escapeHtml(l)}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

// ---- UI State ----
function showLoading(show) {
    document.getElementById('loading').classList.toggle('hidden', !show);
}

function showResults(show) {
    document.getElementById('results').classList.toggle('hidden', !show);
}

function showError(message) {
    const el = document.getElementById('error-display');
    el.querySelector('.toast-msg').textContent = message;
    el.classList.remove('hidden');
    setTimeout(hideError, 5000);
}

function hideError() {
    document.getElementById('error-display').classList.add('hidden');
}

// ---- Utilities ----
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// ---- Event Listeners ----
document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('username');
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') searchDeveloper();
    });
    document.getElementById('search-btn').addEventListener('click', searchDeveloper);
    // Focus search on load
    input.focus();
});
