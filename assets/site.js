'use strict';

// Font stack variants: studio (default) | editorial | terminal
(function applyFontVariant() {
  const allowed = new Set(['studio', 'editorial', 'terminal']);
  const params = new URL(location.href).searchParams;
  const fromQuery = params.get('fonts');
  const stored = localStorage.getItem('intart-fonts');
  const choice = allowed.has(fromQuery) ? fromQuery : (allowed.has(stored) ? stored : 'studio');
  if (choice === 'studio') document.documentElement.removeAttribute('data-fonts');
  else document.documentElement.setAttribute('data-fonts', choice);
  if (fromQuery && allowed.has(fromQuery)) localStorage.setItem('intart-fonts', fromQuery);

  if (document.body && !document.querySelector('.font-switcher')) {
    const nav = document.createElement('nav');
    nav.className = 'font-switcher';
    nav.setAttribute('aria-label', 'Font variations');
    nav.innerHTML = [
      ['studio', 'Studio'],
      ['editorial', 'Editorial'],
      ['terminal', 'Terminal'],
    ].map(([id, label]) => {
      const url = new URL(location.href);
      url.searchParams.set('fonts', id);
      url.searchParams.set('language-selected', document.documentElement.lang);
      const current = choice === id ? ' aria-current="true"' : '';
      return `<a href="${url.pathname + url.search}"${current}>${label}</a>`;
    }).join('');
    document.body.append(nav);
  }
})();

// Decorative trading/AI atmosphere — no claims, no fake metrics.
(function injectAtmosphere() {
  if (document.querySelector('.atmosphere')) return;
  const atm = document.createElement('div');
  atm.className = 'atmosphere';
  atm.setAttribute('aria-hidden', 'true');
  atm.innerHTML = `
    <div class="atmosphere-grid"></div>
    <div class="atmosphere-orb a"></div>
    <div class="atmosphere-orb b"></div>
    <div class="atmosphere-nodes">
      <span></span><span></span><span></span><span></span><span></span>
    </div>
    <svg class="atmosphere-chart" viewBox="0 0 520 220" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="chartStroke" x1="0" y1="0" x2="520" y2="0" gradientUnits="userSpaceOnUse">
          <stop stop-color="#4f8cff"/>
          <stop offset="0.55" stop-color="#2ee6d6"/>
          <stop offset="1" stop-color="#3dd68c"/>
        </linearGradient>
        <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="220" gradientUnits="userSpaceOnUse">
          <stop stop-color="#2ee6d6" stop-opacity="0.28"/>
          <stop offset="1" stop-color="#2ee6d6" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path class="area" d="M0 160 C40 150 70 120 110 128 C150 136 170 90 210 96 C250 102 270 70 310 78 C350 86 370 50 410 58 C450 66 480 40 520 46 L520 220 L0 220 Z"/>
      <path class="line" d="M0 160 C40 150 70 120 110 128 C150 136 170 90 210 96 C250 102 270 70 310 78 C350 86 370 50 410 58 C450 66 480 40 520 46"/>
    </svg>`;
  document.body.prepend(atm);
})();

// Locale selection does not depend on the visitor's identity or traffic source.
const languageDialog = document.getElementById('language-dialog');
// This explicit navigation flag suppresses the dialog only during a language switch.
const languageURL = new URL(location.href);
const selectedLanguage = languageURL.searchParams.get('language-selected');
const skipDialog = selectedLanguage === document.documentElement.lang;
if (selectedLanguage !== null) {
  languageURL.searchParams.delete('language-selected');
  history.replaceState(null, '', languageURL);
}
document.querySelectorAll('[data-language]').forEach(link => {
  link.addEventListener('click', event => {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    if (link.dataset.language === document.documentElement.lang) {
      languageDialog.close();
      document.getElementById('load-video').focus();
      return;
    }
    const target = new URL(link.href);
    target.search = location.search;
    target.searchParams.set('language-selected', link.dataset.language);
    location.assign(target);
  });
});
if (document.body.dataset.step === '1' && !skipDialog) languageDialog.showModal();
const shell = document.getElementById('video-shell');
const loadButton = document.getElementById('load-video');
const status = document.getElementById('video-status');
const step = Number(document.body.dataset.step || '1');
const gateSeconds = step === 1 ? 600 : step === 2 ? 180 : 0;
const gate = document.getElementById('access-gate');
const gateTimer = document.getElementById('access-timer');
let watchedSeconds = 0;
let lastTick = 0;
let player;
let loading = false;
async function loadVideo() {
  if (loading) return;
  loading = true;
  loadButton.disabled = true;
  status.textContent = '';
  let script;
  try {
    if (!customElements.get('mux-player')) {
      await new Promise((resolve, reject) => {
        script = document.createElement('script');
        // Pinned player build; fetched only after an explicit user request.
        script.src = 'https://cdn.jsdelivr.net/npm/@mux/mux-player@3.2.4/dist/mux-player.js';
        const timer = setTimeout(() => reject(new Error('Player load timeout')), 15000);
        script.onload = () => { clearTimeout(timer); resolve(); };
        script.onerror = () => { clearTimeout(timer); reject(new Error('Player unavailable')); };
        document.head.append(script);
      });
    }
    if (!customElements.get('mux-player')) throw new Error('Player not registered');
    player = document.createElement('mux-player');
    player.id = 'video_main';
    player.setAttribute('playback-id', shell.dataset.playback);
    player.setAttribute('stream-type', 'on-demand');
    player.setAttribute('accent-color', '#2ee6d6');
    player.setAttribute('playsinline', '');
    player.setAttribute('preload', 'metadata');
    player.setAttribute('disable-tracking', '');
    player.setAttribute('aria-label', document.title);
    player.addEventListener('ended', () => {
      document.getElementById('completed').hidden = false;
      const next = document.getElementById('continue-link');
      if (next && watchedSeconds >= gateSeconds) {
        next.classList.add('video-finished');
        next.focus({preventScroll:true});
        next.scrollIntoView({behavior:'smooth', block:'center'});
      }
    });
    player.addEventListener('play', () => { lastTick = performance.now(); });
    player.addEventListener('pause', () => { lastTick = 0; });
    player.addEventListener('error', () => {
      status.textContent = shell.dataset.error;
    });
    shell.replaceChildren(player);
    if (gateSeconds > 0) requestAnimationFrame(trackWatchTime);
    // Native controls remain available. No autoplay, fake progress or seek blocking.
  } catch (error) {
    if (script) script.remove();
    status.textContent = shell.dataset.error;
    loadButton.textContent = shell.dataset.retry;
    loadButton.disabled = false;
  } finally {
    loading = false;
  }
}
function trackWatchTime(now) {
  if (player && !player.paused && !player.ended && watchedSeconds < gateSeconds) {
    if (lastTick) watchedSeconds += Math.min((now - lastTick) / 1000, 1);
    lastTick = now;
    updateGate();
  }
  if (watchedSeconds < gateSeconds) requestAnimationFrame(trackWatchTime);
}
function updateGate() {
  if (!gateTimer) return;
  const left = Math.max(0, Math.ceil(gateSeconds - watchedSeconds));
  gateTimer.textContent = `${String(Math.floor(left / 60)).padStart(2, '0')}:${String(left % 60).padStart(2, '0')}`;
  if (left === 0) {
    if (gate) gate.hidden = true;
    document.querySelectorAll('[data-gated]').forEach(el => { el.hidden = false; });
    const next = document.getElementById('continue-link');
    if (next) next.closest('.next-row').hidden = false;
  }
}
loadButton.addEventListener('click', loadVideo);
updateGate();
document.getElementById('replay').addEventListener('click', () => {
  if (!player) return;
  player.currentTime = 0;
  document.getElementById('completed').hidden = true;
  player.play().catch(() => { /* Browser may require use of the native play control. */ });
});
