#!/usr/bin/env python3
"""
generate_html.py
Creates PL400_Study.html — one self-contained file, no internet required.

Left sidebar  : 6 domains sorted by exam weight + per-domain progress rings.
Concept Guide : rendered markdown, "Beyond the Exam" collapsed by default.
Study Deck    : interactive flashcards — guess → reveal → Got it / Review.
                Score + progress persist across sessions via localStorage.
"""
import json, os, re
import markdown as mdlib
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.toc import TocExtension

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(ROOT, "PL400_Study.html")

DOMAINS = [
    ("extend_the_platform",               "Extend the Platform",              "30–35%"),
    ("create_a_technical_design",         "Create a Technical Design",        "10–15%"),
    ("extend_the_user_experience",        "Extend the User Experience",       "10–15%"),
    ("build_power_platform_solutions",    "Build Power Platform Solutions",   "10–15%"),
    ("develop_integrations",              "Develop Integrations",             "10–15%"),
    ("implement_power_apps_improvements", "Implement Power Apps Improvements","10–15%"),
]

# ── helpers ──────────────────────────────────────────────────────────────────

def read_utf8(path):
    with open(path, encoding="utf-8") as f:
        return f.read()

def render_guide(slug):
    path = os.path.join(ROOT, "concept_guides", f"{slug}.md")
    text = read_utf8(path)
    md = mdlib.Markdown(extensions=[
        TableExtension(),
        FencedCodeExtension(),
        TocExtension(permalink=False, toc_depth="2-3"),
    ])
    html = md.convert(text)
    toc  = md.toc

    # Wrap "Beyond the exam" h2 and everything after it in a <details>
    m = re.search(r'<h2[^>]*>[^<]*[Bb]eyond[^<]*</h2>', html)
    if m:
        inner = html[m.end():]
        html = (
            html[:m.start()] +
            '<details class="beyond-section">'
            '<summary>'
            '<span class="beyond-arrow">▶</span>'
            ' <strong>🔭 Beyond the Exam</strong>'
            ' <em class="beyond-hint"> — extra depth from Microsoft Learn (click to expand)</em>'
            '</summary>'
            f'<div class="beyond-body">{inner}</div>'
            '</details>'
        )
    return toc, html

def load_cards(slug):
    path = os.path.join(ROOT, "_parsed", f"{slug}.jsonl")
    cards = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cards.append(json.loads(line))
    return cards

def js_str(s):
    """Escape a Python string for safe embedding in a JS string literal."""
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

# ── CSS ──────────────────────────────────────────────────────────────────────

CSS = """
:root {
  --sb: #0f172a; --sb2: #1e293b; --sbt: #94a3b8; --sba: #3b82f6; --sbab: #172554;
  --bg: #f1f5f9; --surf: #ffffff; --txt: #1e293b; --muted: #64748b;
  --bdr: #e2e8f0; --acc: #3b82f6; --acc2: #2563eb;
  --ok: #16a34a; --okbg: #f0fdf4; --okbdr: #bbf7d0;
  --bad: #dc2626; --badbg: #fef2f2;
  --codebg: #1e293b; --codetxt: #e2e8f0;
  --beybg: #eff6ff; --beybdr: #bfdbfe;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:var(--bg);color:var(--txt);display:flex;height:100vh;overflow:hidden;font-size:15px}

/* ── Sidebar ── */
.sb{width:264px;min-width:264px;background:var(--sb);display:flex;flex-direction:column;overflow:hidden}
.sb-head{padding:18px 16px 14px;border-bottom:1px solid var(--sb2)}
.sb-head h1{font-size:1.05rem;color:#f1f5f9;font-weight:700;letter-spacing:.02em}
.sb-head p{font-size:.72rem;color:#475569;margin-top:3px}
.sb-nav{overflow-y:auto;flex:1;padding:8px 0}
.db{display:flex;width:100%;padding:10px 16px;background:none;border:none;cursor:pointer;
    color:var(--sbt);border-left:3px solid transparent;text-align:left;
    transition:all .15s;align-items:center;gap:10px}
.db:hover{background:var(--sb2);color:#cbd5e1}
.db.active{background:var(--sbab);color:#f1f5f9;border-left-color:var(--sba)}
.db-info{flex:1;min-width:0}
.db-name{font-size:.82rem;font-weight:500;display:block;white-space:nowrap;
         overflow:hidden;text-overflow:ellipsis}
.db-meta{display:flex;justify-content:space-between;font-size:.68rem;
         color:#475569;margin-top:2px}
.db.active .db-meta{color:#93c5fd}
/* progress ring */
.ring-wrap{position:relative;width:36px;height:36px;flex-shrink:0}
.ring-wrap svg{transform:rotate(-90deg)}
.ring-bg{fill:none;stroke:var(--sb2);stroke-width:3}
.ring-fg{fill:none;stroke:var(--sba);stroke-width:3;stroke-linecap:round;
         stroke-dasharray:88;stroke-dashoffset:88;transition:stroke-dashoffset .5s}
.ring-pct{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
          font-size:.55rem;color:#94a3b8;font-weight:600}
.sb-foot{padding:12px 16px;border-top:1px solid var(--sb2);font-size:.7rem;color:#334155}

/* ── Main ── */
.main{flex:1;display:flex;flex-direction:column;overflow:hidden;min-width:0}
.tabs{display:flex;background:var(--surf);border-bottom:1px solid var(--bdr);
      padding:0 24px;flex-shrink:0}
.tb{padding:11px 18px;background:none;border:none;border-bottom:2px solid transparent;
    cursor:pointer;font-size:.85rem;font-weight:500;color:var(--muted);
    margin-bottom:-1px;transition:all .15s}
.tb.active{color:var(--acc);border-bottom-color:var(--acc)}

/* ── Panels ── */
.panel{display:none;flex:1;overflow:hidden;min-height:0}
.panel.active{display:flex;flex-direction:column}
.guide-wrap,.deck-wrap{display:none;flex:1;overflow:hidden;min-height:0}
.guide-wrap.active,.deck-wrap.active{display:flex}

/* ── Guide ── */
.guide-scroll{flex:1;overflow-y:auto;padding:32px 40px;max-width:920px}
.toc-col{width:220px;min-width:220px;overflow-y:auto;padding:20px 14px;
         border-left:1px solid var(--bdr);font-size:.78rem}
.toc-col .toctitle,.toc-label{font-weight:700;text-transform:uppercase;
  font-size:.66rem;letter-spacing:.06em;color:var(--muted);margin-bottom:8px}
.toc-col ul{padding-left:14px;list-style:none}
.toc-col li{margin-bottom:5px;line-height:1.4}
.toc-col a{color:var(--muted);text-decoration:none}
.toc-col a:hover{color:var(--acc)}
/* Typography */
.guide-scroll h1{font-size:1.55rem;color:#0f172a;margin-bottom:10px;
                 padding-bottom:10px;border-bottom:2px solid var(--bdr)}
.guide-scroll h2{font-size:1.15rem;color:#1e293b;margin:28px 0 10px}
.guide-scroll h3{font-size:1rem;color:#334155;margin:18px 0 7px}
.guide-scroll h4{font-size:.9rem;font-weight:700;color:#475569;margin:14px 0 5px}
.guide-scroll p{line-height:1.72;margin-bottom:11px}
.guide-scroll ul,.guide-scroll ol{padding-left:22px;margin-bottom:11px}
.guide-scroll li{line-height:1.65;margin-bottom:3px}
.guide-scroll hr{border:none;border-top:1px solid var(--bdr);margin:22px 0}
.guide-scroll a{color:var(--acc);text-decoration:none}
.guide-scroll a:hover{text-decoration:underline}
.guide-scroll code{background:#f1f5f9;padding:2px 5px;border-radius:3px;
                   font-size:.83em;font-family:'Cascadia Code','Consolas',monospace}
.guide-scroll pre{background:var(--codebg);color:var(--codetxt);padding:16px;
                  border-radius:8px;overflow-x:auto;margin:12px 0;line-height:1.5}
.guide-scroll pre code{background:none;padding:0;font-size:.85em}
.guide-scroll blockquote{border-left:4px solid var(--ok);background:var(--okbg);
                          padding:11px 15px;border-radius:0 6px 6px 0;margin:12px 0}
.guide-scroll table{border-collapse:collapse;width:100%;margin:14px 0;font-size:.85rem}
.guide-scroll th{background:#1e293b;color:#f1f5f9;padding:8px 12px;text-align:left}
.guide-scroll td{padding:7px 12px;border-bottom:1px solid var(--bdr)}
.guide-scroll tr:nth-child(even) td{background:#f8fafc}
/* Beyond section */
.beyond-section{margin:28px 0;border:1px solid var(--beybdr);border-radius:10px;overflow:hidden}
.beyond-section>summary{background:var(--beybg);padding:12px 16px;cursor:pointer;
                         list-style:none;display:flex;align-items:center;gap:8px;
                         user-select:none}
.beyond-section>summary::-webkit-details-marker{display:none}
.beyond-arrow{font-size:.75rem;transition:transform .2s;display:inline-block}
.beyond-section[open]>.beyond-arrow,
.beyond-section[open]>summary .beyond-arrow{transform:rotate(90deg)}
.beyond-hint{font-size:.78rem;color:#3b82f6}
.beyond-body{padding:20px 24px;background:#fafeff}
.beyond-body h2,.beyond-body h3,.beyond-body h4{margin-top:22px}

/* ── Deck / Flashcards ── */
.deck-wrap{justify-content:center;align-items:flex-start;overflow-y:auto;padding:24px}
.deck-container{width:100%;max-width:780px}
.deck-topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}
.deck-progress-info{font-size:.82rem;color:var(--muted)}
.deck-progress-info strong{color:var(--txt)}
.pbar-track{height:5px;background:var(--bdr);border-radius:3px;margin-top:5px;width:260px}
.pbar-fill{height:100%;background:var(--acc);border-radius:3px;
           transition:width .35s;width:0}
.deck-actions{display:flex;gap:8px}
.btn-sm{padding:5px 12px;font-size:.78rem;border:1px solid var(--bdr);
        border-radius:6px;cursor:pointer;background:var(--surf);
        color:var(--muted);transition:background .12s}
.btn-sm:hover{background:#f1f5f9}
/* Card */
.flashcard{background:var(--surf);border-radius:14px;
           box-shadow:0 1px 3px rgba(0,0,0,.07),0 4px 16px rgba(0,0,0,.06);
           padding:28px}
.fc-header{display:flex;justify-content:space-between;align-items:center;
           margin-bottom:18px}
.fc-idx{font-size:.78rem;font-weight:600;color:var(--muted)}
.fc-src{font-size:.72rem;color:#cbd5e1;font-style:italic}
.fc-stem{font-size:.97rem;line-height:1.7;color:var(--txt);
         white-space:pre-wrap;margin-bottom:20px}
.fc-stem code{background:#f1f5f9;padding:1px 4px;border-radius:3px;
              font-family:'Cascadia Code','Consolas',monospace;font-size:.85em}
.multi-label{font-size:.75rem;color:var(--muted);font-style:italic;margin-bottom:8px}
.options-list{display:flex;flex-direction:column;gap:7px;margin-bottom:20px}
.opt{display:flex;gap:10px;padding:9px 13px;border:1.5px solid var(--bdr);
     border-radius:8px;cursor:pointer;transition:all .15s;font-size:.88rem;
     align-items:flex-start}
.opt:hover:not(.disabled){border-color:var(--acc);background:#eff6ff}
.opt.selected{border-color:#6366f1;background:#eef2ff}
.opt.correct{border-color:var(--ok);background:var(--okbg)}
.opt.wrong{border-color:#fca5a5;background:var(--badbg);opacity:.7}
.opt.disabled{cursor:default}
.opt-letter{font-weight:700;min-width:18px;color:var(--muted)}
.opt.correct .opt-letter{color:var(--ok)}
.opt.selected.correct .opt-letter::after{content:' ✓'}
.opt.selected.wrong .opt-letter::after{content:' ✗';color:var(--bad)}
/* Reveal button */
.reveal-btn{width:100%;padding:12px;background:var(--acc);color:#fff;border:none;
            border-radius:9px;font-size:.93rem;font-weight:500;cursor:pointer;
            margin-bottom:16px;transition:background .12s}
.reveal-btn:hover:not(:disabled){background:var(--acc2)}
.reveal-btn:disabled{background:#94a3b8;cursor:default}
/* Rationale */
.rationale{background:#f8fafc;border-left:4px solid var(--ok);border-radius:0 8px 8px 0;
           padding:13px 15px;margin-bottom:16px;font-size:.85rem;line-height:1.7;
           color:var(--txt);display:none;white-space:pre-wrap}
/* Verdict */
.verdict{display:none;justify-content:center;gap:12px}
.verdict.show{display:flex}
.v-got{padding:9px 26px;background:var(--ok);color:#fff;border:none;
       border-radius:8px;font-size:.88rem;font-weight:500;cursor:pointer}
.v-got:hover{background:#15803d}
.v-rev{padding:9px 26px;background:var(--badbg);color:var(--bad);
       border:1px solid #fca5a5;border-radius:8px;font-size:.88rem;
       font-weight:500;cursor:pointer}
.v-rev:hover{background:#fecaca}
/* Done banner */
.done-banner{text-align:center;padding:60px 24px}
.done-banner h2{font-size:1.6rem;margin-bottom:10px}
.done-banner p{color:var(--muted);margin-bottom:6px;font-size:.9rem}
.done-banner .final-score{font-size:2.5rem;font-weight:700;color:var(--acc);
                           margin:16px 0 8px}
.done-banner .btn-restart{padding:10px 24px;background:var(--acc);color:#fff;
  border:none;border-radius:8px;cursor:pointer;font-size:.9rem;margin:4px}
.done-banner .btn-review-only{padding:10px 24px;background:var(--surf);
  color:var(--txt);border:1px solid var(--bdr);border-radius:8px;
  cursor:pointer;font-size:.9rem;margin:4px}
"""

# ── JavaScript ────────────────────────────────────────────────────────────────

JS_TEMPLATE = r"""
const DOMAINS = __DOMAINS__;
const CARDS   = __CARDS__;   // {slug: [{id,stem,options:{},correct:[],rationale},...]}

// ── State ────────────────────────────────────────────────────────────────────
const queue   = {};   // slug -> ordered card array (current play order)
const qIdx    = {};   // slug -> index into queue
const revealed= {};   // slug -> bool (current card revealed?)
const chosen  = {};   // slug -> Set of letters user clicked
const tabState= {};   // slug -> 'guide'|'deck'

function lsKey(slug, k) { return `pl400_${slug}_${k}`; }
function getSet(slug, k) {
    try { return new Set(JSON.parse(localStorage.getItem(lsKey(slug,k)) || '[]')); }
    catch { return new Set(); }
}
function saveSet(slug, k, s) {
    localStorage.setItem(lsKey(slug,k), JSON.stringify([...s]));
}
function getAnswered(slug) { return getSet(slug,'answered'); }
function getCorrect(slug)  { return getSet(slug,'correct'); }

// ── Sidebar navigation ───────────────────────────────────────────────────────
function showDomain(slug) {
    document.querySelectorAll('.db').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelector(`.db[data-slug="${slug}"]`).classList.add('active');
    document.getElementById(`panel-${slug}`).classList.add('active');
    // restore last tab
    const tab = tabState[slug] || 'guide';
    activateTab(slug, tab, false);
}

// ── Tabs ─────────────────────────────────────────────────────────────────────
function activateTab(slug, tab, save=true) {
    if (save) tabState[slug] = tab;
    const panel = document.getElementById(`panel-${slug}`);
    panel.querySelectorAll('.tb').forEach(b => {
        b.classList.toggle('active', b.dataset.tab === tab);
    });
    panel.querySelectorAll('.guide-wrap,.deck-wrap').forEach(w => w.classList.remove('active'));
    panel.querySelector(`.${tab}-wrap`).classList.add('active');
    if (tab === 'deck') initDeck(slug);
}

// ── Deck initialisation ───────────────────────────────────────────────────────
function initDeck(slug) {
    const answered = getAnswered(slug);
    const allCards  = CARDS[slug];
    // Build queue: unanswered first, then answered (review pass)
    const unseen = allCards.filter(c => !answered.has(c.id));
    const seen   = allCards.filter(c =>  answered.has(c.id));
    queue[slug]  = [...unseen, ...seen];
    qIdx[slug]   = 0;
    revealed[slug] = false;
    chosen[slug]   = new Set();
    renderCurrentCard(slug);
    updateDeckHeader(slug);
}

function updateDeckHeader(slug) {
    const answered = getAnswered(slug);
    const correct  = getCorrect(slug);
    const total    = CARDS[slug].length;
    const ans      = answered.size;
    const cor      = correct.size;
    const pct      = ans > 0 ? Math.round(cor/ans*100) : 0;
    const el = document.getElementById(`deck-stats-${slug}`);
    if (el) el.innerHTML =
        `<strong>${ans}</strong>/${total} answered &nbsp;·&nbsp; `+
        `<strong style="color:var(--ok)">${pct}%</strong> correct`;
    const bar = document.getElementById(`pbar-${slug}`);
    if (bar) bar.style.width = (ans/total*100)+'%';
    // update ring in sidebar
    updateRing(slug, pct);
}

function updateRing(slug, pct) {
    const ring = document.querySelector(`.ring-fg[data-slug="${slug}"]`);
    const label= document.querySelector(`.ring-pct[data-slug="${slug}"]`);
    if (!ring) return;
    const offset = 88 - (88 * pct / 100);
    ring.style.strokeDashoffset = offset;
    if (label) label.textContent = pct ? pct+'%' : '';
}

// ── Render card ───────────────────────────────────────────────────────────────
function renderCurrentCard(slug) {
    const box = document.getElementById(`deck-box-${slug}`);
    const q   = queue[slug][qIdx[slug]];
    if (!q) { showDone(slug); return; }
    revealed[slug] = false;
    chosen[slug]   = new Set();
    const letters  = Object.keys(q.options);
    const multi    = q.correct.length > 1;
    const answered = getAnswered(slug);
    const wasAnswered = answered.has(q.id);

    box.innerHTML = `
    <div class="flashcard">
      <div class="fc-header">
        <span class="fc-idx">Card ${qIdx[slug]+1} of ${queue[slug].length}</span>
        <span class="fc-src">${q.id}</span>
      </div>
      <div class="fc-stem">${escHtml(q.stem)}</div>
      ${multi ? '<p class="multi-label">Select all correct answers:</p>' : ''}
      <div class="options-list" id="opts-${slug}">
        ${letters.map(l =>
          `<div class="opt" data-letter="${l}" onclick="pickOpt('${slug}','${l}')">
             <span class="opt-letter">${l}.</span>
             <span>${escHtml(q.options[l])}</span>
           </div>`
        ).join('')}
      </div>
      <button class="reveal-btn" id="reveal-${slug}" onclick="revealCard('${slug}')">
        Reveal Answer  <kbd style="font-size:.7rem;opacity:.7">Space</kbd>
      </button>
      <div class="rationale" id="rat-${slug}">${escHtml(q.rationale)}</div>
      <div class="verdict" id="verd-${slug}">
        <button class="v-got" onclick="markCard('${slug}',true)">✓ Got it  <kbd style="font-size:.7rem;opacity:.7">G</kbd></button>
        <button class="v-rev" onclick="markCard('${slug}',false)">✗ Review again  <kbd style="font-size:.7rem;opacity:.7">R</kbd></button>
      </div>
    </div>`;
}

function pickOpt(slug, letter) {
    if (revealed[slug]) return;
    const btn = document.querySelector(`#opts-${slug} .opt[data-letter="${letter}"]`);
    if (!btn) return;
    btn.classList.toggle('selected');
    if (btn.classList.contains('selected')) chosen[slug].add(letter);
    else chosen[slug].delete(letter);
}

function revealCard(slug) {
    if (revealed[slug]) return;
    revealed[slug] = true;
    const q = queue[slug][qIdx[slug]];
    const correctSet = new Set(q.correct);

    // colour options
    document.querySelectorAll(`#opts-${slug} .opt`).forEach(el => {
        const l = el.dataset.letter;
        el.classList.add('disabled');
        if (correctSet.has(l)) el.classList.add('correct');
        else if (chosen[slug].has(l)) el.classList.add('wrong');
    });
    // show rationale
    const rat = document.getElementById(`rat-${slug}`);
    if (rat) rat.style.display = 'block';
    // disable reveal button
    const rb = document.getElementById(`reveal-${slug}`);
    if (rb) rb.disabled = true;
    // show verdict
    const vd = document.getElementById(`verd-${slug}`);
    if (vd) vd.classList.add('show');

    // mark as answered
    const answered = getAnswered(slug);
    answered.add(q.id);
    saveSet(slug,'answered',answered);
    updateDeckHeader(slug);
}

function markCard(slug, gotIt) {
    const q = queue[slug][qIdx[slug]];
    if (gotIt) {
        const correct = getCorrect(slug);
        correct.add(q.id);
        saveSet(slug,'correct',correct);
    }
    qIdx[slug]++;
    updateDeckHeader(slug);
    if (qIdx[slug] >= queue[slug].length) { showDone(slug); return; }
    renderCurrentCard(slug);
}

function showDone(slug) {
    const answered = getAnswered(slug);
    const correct  = getCorrect(slug);
    const total    = CARDS[slug].length;
    const pct      = answered.size > 0 ? Math.round(correct.size/answered.size*100) : 0;
    const reviewQ  = CARDS[slug].filter(c => answered.has(c.id) && !correct.has(c.id));
    const box = document.getElementById(`deck-box-${slug}`);
    box.innerHTML = `
      <div class="done-banner">
        <div style="font-size:2.5rem">🎉</div>
        <h2>Round complete!</h2>
        <div class="final-score">${pct}%</div>
        <p>${correct.size} correct out of ${answered.size} answered</p>
        <p>${reviewQ.length} cards marked for review</p>
        <div style="margin-top:20px;display:flex;justify-content:center;flex-wrap:wrap;gap:8px">
          <button class="btn-restart" onclick="restartDeck('${slug}',false)">↺ Restart all cards</button>
          ${reviewQ.length
            ? `<button class="btn-review-only" onclick="restartDeck('${slug}',true)">🔁 Review only (${reviewQ.length})</button>`
            : ''}
          <button class="btn-review-only" onclick="resetDeck('${slug}')">🗑 Reset scores</button>
        </div>
      </div>`;
}

function restartDeck(slug, reviewOnly) {
    if (reviewOnly) {
        const answered = getAnswered(slug);
        const correct  = getCorrect(slug);
        queue[slug] = CARDS[slug].filter(c => answered.has(c.id) && !correct.has(c.id));
    } else {
        queue[slug] = [...CARDS[slug]];
    }
    qIdx[slug]    = 0;
    revealed[slug]= false;
    chosen[slug]  = new Set();
    renderCurrentCard(slug);
}

function resetDeck(slug) {
    localStorage.removeItem(lsKey(slug,'answered'));
    localStorage.removeItem(lsKey(slug,'correct'));
    initDeck(slug);
}

function shuffleDeck(slug) {
    const arr = queue[slug];
    for (let i = arr.length-1; i > 0; i--) {
        const j = Math.floor(Math.random()*(i+1));
        [arr[i],arr[j]] = [arr[j],arr[i]];
    }
    qIdx[slug] = 0;
    renderCurrentCard(slug);
}

// ── Keyboard shortcuts ────────────────────────────────────────────────────────
document.addEventListener('keydown', e => {
    const active = document.querySelector('.db.active');
    if (!active) return;
    const slug = active.dataset.slug;
    const tab  = tabState[slug] || 'guide';
    if (tab !== 'deck') return;
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    if (e.code === 'Space') { e.preventDefault(); if (!revealed[slug]) revealCard(slug); }
    if ((e.code === 'KeyG') && revealed[slug]) markCard(slug, true);
    if ((e.code === 'KeyR') && revealed[slug]) markCard(slug, false);
});

// ── Helpers ───────────────────────────────────────────────────────────────────
function escHtml(s) {
    return String(s)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;');
}

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    DOMAINS.forEach(([slug,,]) => {
        const ans = getAnswered(slug);
        const cor = getCorrect(slug);
        const pct = ans.size > 0 ? Math.round(cor.size/ans.size*100) : 0;
        updateRing(slug, pct);
    });
    showDomain(DOMAINS[0][0]);
});
"""

# ── HTML builder ──────────────────────────────────────────────────────────────

def build():
    all_cards = {}
    panels    = []

    for slug, name, weight in DOMAINS:
        toc, guide_html = render_guide(slug)
        cards = load_cards(slug)
        all_cards[slug] = cards

        panel = f"""
<div class="panel" id="panel-{slug}">
  <div class="tabs">
    <button class="tb active" data-tab="guide"
            onclick="activateTab('{slug}','guide')">📖 Concept Guide</button>
    <button class="tb" data-tab="deck"
            onclick="activateTab('{slug}','deck')">🃏 Study Deck ({len(cards)} cards)</button>
  </div>
  <!-- Guide -->
  <div class="guide-wrap active">
    <div class="guide-scroll">{guide_html}</div>
    <div class="toc-col"><div class="toc-label">Contents</div>{toc}</div>
  </div>
  <!-- Deck -->
  <div class="deck-wrap">
    <div class="deck-container">
      <div class="deck-topbar">
        <div>
          <div class="deck-progress-info" id="deck-stats-{slug}">
            <strong>0</strong>/{len(cards)} answered
          </div>
          <div class="pbar-track"><div class="pbar-fill" id="pbar-{slug}"></div></div>
        </div>
        <div class="deck-actions">
          <button class="btn-sm" onclick="shuffleDeck('{slug}')">🔀 Shuffle</button>
          <button class="btn-sm" onclick="resetDeck('{slug}')">↺ Reset</button>
        </div>
      </div>
      <div id="deck-box-{slug}"></div>
    </div>
  </div>
</div>"""
        panels.append(panel)

    # Sidebar buttons
    sb_items = []
    for slug, name, weight in DOMAINS:
        cards = all_cards[slug]
        sb_items.append(f"""
<button class="db" data-slug="{slug}" onclick="showDomain('{slug}')">
  <div class="ring-wrap">
    <svg width="36" height="36" viewBox="0 0 36 36">
      <circle class="ring-bg" cx="18" cy="18" r="14"/>
      <circle class="ring-fg" data-slug="{slug}" cx="18" cy="18" r="14"/>
    </svg>
    <span class="ring-pct" data-slug="{slug}"></span>
  </div>
  <div class="db-info">
    <span class="db-name">{name}</span>
    <span class="db-meta">
      <span>{weight}</span><span>{len(all_cards[slug])} Qs</span>
    </span>
  </div>
</button>""")

    # Serialize flashcard data for JS
    cards_json = json.dumps(all_cards, ensure_ascii=False)
    domains_json = json.dumps([[s,n,w] for s,n,w in DOMAINS], ensure_ascii=False)
    js = JS_TEMPLATE.replace("__DOMAINS__", domains_json).replace("__CARDS__", cards_json)

    total_q = sum(len(all_cards[s]) for s,_,_ in DOMAINS)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PL-400 Study Portal</title>
<style>{CSS}</style>
</head>
<body>
<aside class="sb">
  <div class="sb-head">
    <h1>PL-400 Study Portal</h1>
    <p>{total_q} questions · 6 domains</p>
  </div>
  <nav class="sb-nav">{''.join(sb_items)}</nav>
  <div class="sb-foot">Space=reveal · G=got it · R=review</div>
</aside>
<main class="main">
  {''.join(panels)}
</main>
<script>{js}</script>
</body>
</html>"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Written: {OUT}")
    print(f"Size:    {os.path.getsize(OUT)/1024:.0f} KB")

if __name__ == "__main__":
    build()
