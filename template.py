"""HTML template builder for the interactive review page.

Generates a fully self-contained HTML file (inline CSS/JS, no external
dependencies) that works offline.
"""

import html
import json
from datetime import datetime


def build_html(corrections: list[dict], title: str = "Dictation Review") -> str:
    """Build the complete self-contained HTML review page."""
    corrections_json = json.dumps(corrections, ensure_ascii=False)
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — {date_str}</title>
<style>
{CSS}
</style>
</head>
<body>
<div id="app">
  <header>
    <div class="header-top">
      <h1>{html.escape(title)}</h1>
      <div class="header-controls">
        <button id="darkToggle" onclick="toggleDark()" title="Toggle dark mode">🌙</button>
      </div>
    </div>
    <div class="progress-bar-container">
      <div class="progress-bar" id="progressBar"></div>
    </div>
    <div class="progress-text" id="progressText">0 / 0 reviewed</div>
    <div class="batch-buttons">
      <span>Set all to:</span>
      <button onclick="batchSelect('original')">Original</button>
      <button onclick="batchSelect('minimal')">Minimal</button>
      <button onclick="batchSelect('light')">Light</button>
      <button onclick="batchSelect('polish')">Polish</button>
    </div>
    <div class="keyboard-hint">
      Keyboard: <kbd>1</kbd>-<kbd>5</kbd> select · <kbd>E</kbd> edit · <kbd>Enter</kbd> confirm · <kbd>↑↓</kbd> navigate
    </div>
  </header>

  <main id="cardsContainer"></main>

  <section id="outputSection" class="output-section hidden">
    <h2>Final Output</h2>
    <div class="output-tabs">
      <button class="tab active" onclick="showTab('preview')">Preview</button>
      <button class="tab" onclick="showTab('raw')">Raw Markdown</button>
    </div>
    <div id="previewTab" class="tab-content">
      <div id="markdownPreview"></div>
    </div>
    <div id="rawTab" class="tab-content hidden">
      <textarea id="markdownRaw" readonly></textarea>
    </div>
    <div class="output-actions">
      <button onclick="copyMarkdown()">📋 Copy Markdown to Clipboard</button>
      <button onclick="downloadMarkdown()">💾 Download as .md</button>
    </div>
  </section>
</div>

<script>
const CORRECTIONS = {corrections_json};
const DATE_STR = "{date_str}";
const TIMESTAMP = "{timestamp}";

{JS}
</script>
</body>
</html>"""


CSS = """
:root {
  --bg: #f5f5f7;
  --card-bg: #ffffff;
  --text: #1d1d1f;
  --text-secondary: #6e6e73;
  --border: #d2d2d7;
  --accent: #0071e3;
  --accent-hover: #0077ed;
  --green: #34c759;
  --red: #ff3b30;
  --green-bg: #e8f8ed;
  --red-bg: #fdecea;
  --confirmed-bg: #f0faf3;
  --header-bg: #ffffff;
  --progress-bg: #e5e5ea;
  --kbd-bg: #e5e5ea;
  --output-bg: #f9f9f9;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --mono: "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
}

.dark {
  --bg: #1c1c1e;
  --card-bg: #2c2c2e;
  --text: #f5f5f7;
  --text-secondary: #98989d;
  --border: #48484a;
  --accent: #0a84ff;
  --accent-hover: #409cff;
  --green-bg: #1a3a2a;
  --red-bg: #3a1a1a;
  --confirmed-bg: #1a2e1f;
  --header-bg: #2c2c2e;
  --progress-bg: #3a3a3c;
  --kbd-bg: #3a3a3c;
  --output-bg: #2c2c2e;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  padding-bottom: 4rem;
}

header {
  position: sticky;
  top: 0;
  background: var(--header-bg);
  border-bottom: 1px solid var(--border);
  padding: 1rem 1.5rem;
  z-index: 100;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

h1 { font-size: 1.25rem; font-weight: 600; }

.header-controls button {
  background: none;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  font-size: 1rem;
}

.progress-bar-container {
  width: 100%;
  height: 6px;
  background: var(--progress-bg);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.25rem;
}

.progress-bar {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  width: 0%;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.batch-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.4rem;
}

.batch-buttons span {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.batch-buttons button {
  font-size: 0.75rem;
  padding: 0.25rem 0.6rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--card-bg);
  color: var(--text);
  cursor: pointer;
}

.batch-buttons button:hover { border-color: var(--accent); color: var(--accent); }

.keyboard-hint {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

kbd {
  background: var(--kbd-bg);
  border-radius: 4px;
  padding: 0.1rem 0.35rem;
  font-family: var(--mono);
  font-size: 0.7rem;
}

main { max-width: 800px; margin: 1.5rem auto; padding: 0 1rem; }

.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1rem;
  transition: border-color 0.2s;
}

.card.active { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }
.card.confirmed { background: var(--confirmed-bg); border-color: var(--green); }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.card-number {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.card-status {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  background: var(--progress-bg);
  color: var(--text-secondary);
}

.card.confirmed .card-status {
  background: var(--green);
  color: white;
}

blockquote {
  border-left: 3px solid var(--border);
  padding: 0.5rem 0.75rem;
  margin-bottom: 1rem;
  font-style: italic;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.options { margin-bottom: 0.75rem; }

.option {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.25rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.option:hover { background: var(--progress-bg); }
.option.selected { background: rgba(0, 113, 227, 0.08); }
.option.delete .option-text { color: var(--red); }
.option.delete.selected { background: var(--red-bg); }
.card.confirmed .card-status.deleted { color: var(--red); }

.option input[type="radio"] {
  margin-top: 0.3rem;
  accent-color: var(--accent);
}

.option-label {
  font-size: 0.8rem;
  font-weight: 600;
  min-width: 80px;
  color: var(--text-secondary);
}

.option-text { font-size: 0.9rem; flex: 1; }

.option.change { padding-left: 2rem; }
.section-title {
  display: block;
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-secondary);
  margin: 0.25rem 0 0.35rem;
}

.diff-add {
  background: var(--green-bg);
  color: var(--green);
  padding: 0.05rem 0.15rem;
  border-radius: 3px;
  text-decoration: none;
}

.diff-del {
  background: var(--red-bg);
  color: var(--red);
  padding: 0.05rem 0.15rem;
  border-radius: 3px;
  text-decoration: line-through;
}

.edit-toggle {
  font-size: 0.8rem;
  color: var(--accent);
  background: none;
  border: none;
  cursor: pointer;
  margin-bottom: 0.5rem;
}

.edit-area {
  width: 100%;
  min-height: 80px;
  padding: 0.6rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-family: var(--font);
  font-size: 0.9rem;
  background: var(--card-bg);
  color: var(--text);
  resize: vertical;
  margin-bottom: 0.75rem;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
}

.confirm-btn {
  padding: 0.4rem 1.2rem;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.confirm-btn:hover { background: var(--accent-hover); }
.confirm-btn:disabled { opacity: 0.5; cursor: default; }

.output-section {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.output-section.hidden { display: none; }

.output-section h2 { margin-bottom: 1rem; }

.output-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 1rem;
}

.tab {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  cursor: pointer;
  font-size: 0.85rem;
}

.tab:first-child { border-radius: 8px 0 0 8px; }
.tab:last-child { border-radius: 0 8px 8px 0; }
.tab.active { background: var(--accent); color: white; border-color: var(--accent); }

.tab-content.hidden { display: none; }

#markdownPreview {
  background: var(--output-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.25rem;
  white-space: pre-wrap;
  font-size: 0.9rem;
  line-height: 1.7;
}

#markdownRaw {
  width: 100%;
  min-height: 300px;
  padding: 1rem;
  font-family: var(--mono);
  font-size: 0.85rem;
  background: var(--output-bg);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  resize: vertical;
}

.output-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.output-actions button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card-bg);
  color: var(--text);
  cursor: pointer;
  font-size: 0.85rem;
}

.output-actions button:hover { border-color: var(--accent); color: var(--accent); }

@media (max-width: 600px) {
  header { padding: 0.75rem 1rem; }
  .card { padding: 1rem; }
  .option-label { min-width: 60px; font-size: 0.75rem; }
}
"""

JS = r"""
// --- State ---
let state = {
  activeIndex: 0,
  items: CORRECTIONS.map((c, i) => ({
    index: i,
    original: c.original,
    minimal: c.minimal,
    light: c.light,
    polish: c.polish,
    selected: null,    // 'original' | 'minimal' | 'light' | 'polish' | 'delete'
    editText: '',
    editing: false,
    confirmed: false,
  })),
};

const STORAGE_KEY = 'dictation-reviewer-' + TIMESTAMP;

// --- Diff ---
function diffWords(a, b) {
  const wa = a.split(/(\s+)/);
  const wb = b.split(/(\s+)/);
  // Simple LCS-based word diff
  const m = wa.length, n = wb.length;
  const dp = Array.from({length: m + 1}, () => Array(n + 1).fill(0));
  for (let i = 1; i <= m; i++)
    for (let j = 1; j <= n; j++)
      dp[i][j] = wa[i-1] === wb[j-1] ? dp[i-1][j-1] + 1 : Math.max(dp[i-1][j], dp[i][j-1]);

  const result = [];
  let i = m, j = n;
  const ops = [];
  while (i > 0 && j > 0) {
    if (wa[i-1] === wb[j-1]) {
      ops.push({type: 'eq', text: wa[i-1]});
      i--; j--;
    } else if (dp[i-1][j] >= dp[i][j-1]) {
      ops.push({type: 'del', text: wa[i-1]});
      i--;
    } else {
      ops.push({type: 'add', text: wb[j-1]});
      j--;
    }
  }
  while (i > 0) { ops.push({type: 'del', text: wa[i-1]}); i--; }
  while (j > 0) { ops.push({type: 'add', text: wb[j-1]}); j--; }
  ops.reverse();

  return ops.map(op => {
    const escaped = escapeHtml(op.text);
    if (op.type === 'del') return `<span class="diff-del">${escaped}</span>`;
    if (op.type === 'add') return `<span class="diff-add">${escaped}</span>`;
    return escaped;
  }).join('');
}

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// --- Render ---
function renderCards() {
  const container = document.getElementById('cardsContainer');
  container.innerHTML = state.items.map((item, i) => {
    const isActive = i === state.activeIndex;
    const classes = ['card'];
    if (isActive) classes.push('active');
    if (item.confirmed) classes.push('confirmed');

    const options = [
      {key: 'original', label: 'Original', text: item.original},
      {key: 'minimal', label: 'Minimal', text: item.minimal},
      {key: 'light', label: 'Light', text: item.light},
      {key: 'polish', label: 'Polish', text: item.polish},
    ];

    const completeHtml = options.map(opt => {
      const isSelected = item.selected === opt.key;
      return `
        <label class="option ${isSelected ? 'selected' : ''}" onclick="selectOption(${i}, '${opt.key}')">
          <input type="radio" name="opt${i}" ${isSelected ? 'checked' : ''} ${item.confirmed ? 'disabled' : ''}>
          <span class="option-label">${opt.label}</span>
          <span class="option-text">${escapeHtml(opt.text)}</span>
        </label>`;
    }).join('');

    const deleteSelected = item.selected === 'delete';
    const deleteHtml = `
        <label class="option delete ${deleteSelected ? 'selected' : ''}" onclick="selectOption(${i}, 'delete')">
          <input type="radio" name="opt${i}" ${deleteSelected ? 'checked' : ''} ${item.confirmed ? 'disabled' : ''}>
          <span class="option-label">Delete</span>
          <span class="option-text">Delete this entry (leave it out of the final notes)</span>
        </label>`;

    const changesHtml = options.filter(opt => opt.key !== 'original').map(opt => {
      const isSelected = item.selected === opt.key;
      return `
        <div class="option change ${isSelected ? 'selected' : ''}" onclick="selectOption(${i}, '${opt.key}')">
          <span class="option-label">${opt.label}</span>
          <span class="option-text">${diffWords(item.original, opt.text)}</span>
        </div>`;
    }).join('');

    const editHtml = item.editing ? `
      <textarea class="edit-area" id="editArea${i}" oninput="updateEdit(${i}, this.value)"
        ${item.confirmed ? 'disabled' : ''}>${escapeHtml(item.editText)}</textarea>` : '';

    return `
      <div class="${classes.join(' ')}" id="card${i}" data-index="${i}" onclick="setActive(${i})">
        <div class="card-header">
          <span class="card-number">#${i + 1}</span>
          <span class="card-status">${item.confirmed ? (item.selected === 'delete' ? '✓ Deleted' : '✓ Confirmed') : 'Pending'}</span>
        </div>
        <blockquote>${escapeHtml(item.original)}</blockquote>
        <div class="options">
          <div class="section-title">Complete versions</div>
          ${completeHtml}
          ${deleteHtml}
        </div>
        <div class="options">
          <div class="section-title">Changes vs. original</div>
          ${changesHtml}
        </div>
        <button class="edit-toggle" onclick="toggleEdit(${i})" ${item.confirmed ? 'disabled' : ''}>
          ${item.editing ? 'Close editor' : '✏️ Edit manually'}
        </button>
        ${editHtml}
        <div class="card-actions">
          <button class="confirm-btn" onclick="confirmCard(${i})"
            ${item.confirmed ? 'disabled' : ''}
            ${!item.selected ? 'disabled' : ''}>
            ${item.confirmed ? 'Confirmed' : 'Confirm'}
          </button>
        </div>
      </div>`;
  }).join('');

  updateProgress();
  checkAllDone();
}

function updateProgress() {
  const total = state.items.length;
  const done = state.items.filter(it => it.confirmed).length;
  const pct = total > 0 ? (done / total * 100) : 0;
  document.getElementById('progressBar').style.width = pct + '%';
  document.getElementById('progressText').textContent = `${done} / ${total} reviewed`;
}

// --- Actions ---
function setActive(i) {
  state.activeIndex = i;
  document.querySelectorAll('.card').forEach((c, idx) => {
    c.classList.toggle('active', idx === i);
  });
}

function selectOption(i, key) {
  if (state.items[i].confirmed) return;
  state.items[i].selected = key;
  state.items[i].editText = key === 'delete' ? '' : state.items[i][key];
  saveState();
  renderCards();
}

function toggleEdit(i) {
  if (state.items[i].confirmed) return;
  state.items[i].editing = !state.items[i].editing;
  if (state.items[i].editing && !state.items[i].editText && state.items[i].selected && state.items[i].selected !== 'delete') {
    state.items[i].editText = state.items[i][state.items[i].selected];
  }
  saveState();
  renderCards();
  if (state.items[i].editing) {
    const ta = document.getElementById('editArea' + i);
    if (ta) ta.focus();
  }
}

function updateEdit(i, value) {
  state.items[i].editText = value;
  saveState();
}

function confirmCard(i) {
  if (!state.items[i].selected) return;
  state.items[i].confirmed = true;
  saveState();
  renderCards();
  // Auto-scroll to next unconfirmed
  const next = state.items.findIndex((it, idx) => idx > i && !it.confirmed);
  if (next !== -1) {
    setActive(next);
    document.getElementById('card' + next)?.scrollIntoView({behavior: 'smooth', block: 'center'});
  }
}

function batchSelect(key) {
  state.items.forEach(item => {
    if (!item.confirmed && !isDeleted(item)) {
      item.selected = key;
      item.editText = item[key];
    }
  });
  saveState();
  renderCards();
}

// --- Dark mode ---
function toggleDark() {
  document.documentElement.classList.toggle('dark');
  const isDark = document.documentElement.classList.contains('dark');
  localStorage.setItem('dictation-dark', isDark ? '1' : '0');
  document.getElementById('darkToggle').textContent = isDark ? '☀️' : '🌙';
}

// --- Output ---
function checkAllDone() {
  const allDone = state.items.every(it => it.confirmed);
  const section = document.getElementById('outputSection');
  if (allDone && state.items.length > 0) {
    section.classList.remove('hidden');
    renderOutput();
  } else {
    section.classList.add('hidden');
  }
}

function isDeleted(item) {
  return item.selected === 'delete';
}

function getFinalText(item) {
  if (item.editing && item.editText) return item.editText;
  return item[item.selected] || item.original;
}

function generateMarkdown() {
  const kept = state.items.filter(it => !isDeleted(it));
  const revised = kept.map(it => getFinalText(it)).join('\n\n');
  const originals = kept.map(it => it.original).join('\n\n');
  return `# Daily Notes — ${DATE_STR}\n\n---\n\n## Revised\n\n${revised}\n\n---\n\n## Original\n\n${originals}\n`;
}

function renderOutput() {
  const md = generateMarkdown();
  document.getElementById('markdownRaw').value = md;
  // Simple markdown to HTML for preview
  const previewHtml = md
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^---$/gm, '<hr>')
    .replace(/\n\n/g, '<br><br>');
  document.getElementById('markdownPreview').innerHTML = previewHtml;
}

function showTab(tab) {
  document.getElementById('previewTab').classList.toggle('hidden', tab !== 'preview');
  document.getElementById('rawTab').classList.toggle('hidden', tab !== 'raw');
  document.querySelectorAll('.output-tabs .tab').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.toLowerCase().includes(tab));
  });
}

async function copyMarkdown() {
  const md = generateMarkdown();
  await navigator.clipboard.writeText(md);
  alert('Markdown copied to clipboard!');
}

function downloadMarkdown() {
  const md = generateMarkdown();
  const blob = new Blob([md], {type: 'text/markdown'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = TIMESTAMP + '.md';
  a.click();
  URL.revokeObjectURL(url);
}

// --- Persistence ---
function saveState() {
  const toSave = state.items.map(it => ({
    selected: it.selected,
    editText: it.editText,
    editing: it.editing,
    confirmed: it.confirmed,
  }));
  localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave));
}

function loadState() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) return;
  try {
    const parsed = JSON.parse(saved);
    parsed.forEach((s, i) => {
      if (state.items[i]) {
        state.items[i].selected = s.selected;
        state.items[i].editText = s.editText;
        state.items[i].editing = s.editing;
        state.items[i].confirmed = s.confirmed;
      }
    });
  } catch (e) {
    console.warn('Failed to restore state:', e);
  }
}

// --- Keyboard shortcuts ---
document.addEventListener('keydown', (e) => {
  // Don't capture when typing in textarea
  if (e.target.tagName === 'TEXTAREA') {
    if (e.key === 'Escape') {
      e.target.blur();
      toggleEdit(state.activeIndex);
    }
    return;
  }

  const i = state.activeIndex;
  switch (e.key) {
    case '1': selectOption(i, 'original'); e.preventDefault(); break;
    case '2': selectOption(i, 'minimal'); e.preventDefault(); break;
    case '3': selectOption(i, 'light'); e.preventDefault(); break;
    case '4': selectOption(i, 'polish'); e.preventDefault(); break;
    case '5': selectOption(i, 'delete'); e.preventDefault(); break;
    case 'e':
    case 'E': toggleEdit(i); e.preventDefault(); break;
    case 'Enter': confirmCard(i); e.preventDefault(); break;
    case 'ArrowDown':
      if (i < state.items.length - 1) {
        setActive(i + 1);
        document.getElementById('card' + (i + 1))?.scrollIntoView({behavior: 'smooth', block: 'center'});
      }
      e.preventDefault();
      break;
    case 'ArrowUp':
      if (i > 0) {
        setActive(i - 1);
        document.getElementById('card' + (i - 1))?.scrollIntoView({behavior: 'smooth', block: 'center'});
      }
      e.preventDefault();
      break;
  }
});

// --- Init ---
(function init() {
  if (localStorage.getItem('dictation-dark') === '1') {
    document.documentElement.classList.add('dark');
    document.getElementById('darkToggle').textContent = '☀️';
  }
  loadState();
  renderCards();
})();
"""
