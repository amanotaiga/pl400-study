#!/usr/bin/env python3
"""
generate_html.py
Creates PL400_Study.html — one self-contained file, no internet required.

Left sidebar  : 6 domains sorted by exam weight + per-domain progress rings.
Concept Guide : rendered markdown, "Beyond the Exam" collapsed by default.
Study Deck    : interactive flashcards — guess → reveal → Got it / Review.
                Score + progress persist across sessions via localStorage.
"""
import json, os, re, html as htmllib
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

_FENCE_RE = re.compile(r'^\s*(```|~~~)')
_LIST_RE  = re.compile(r'^\s*([-*+]|\d+\.)\s+\S')

def fix_list_spacing(text):
    """Python-Markdown only treats `- `/`1.` lines as a list when a blank line
    precedes them; otherwise they fold into the previous paragraph and render
    inline. Insert that blank line before any list that directly follows prose.
    Fenced code blocks are skipped so bullet-like code (flags, YAML) is safe."""
    out, in_fence = [], False
    for ln in text.split("\n"):
        if _FENCE_RE.match(ln):
            in_fence = not in_fence
        elif (not in_fence and _LIST_RE.match(ln)
              and out and out[-1].strip() and not _LIST_RE.match(out[-1])):
            out.append("")
        out.append(ln)
    return "\n".join(out)

def render_guide(slug):
    path = os.path.join(ROOT, "concept_guides", f"{slug}.md")
    text = fix_list_spacing(read_utf8(path))
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

# ── Reconstructed exhibits ────────────────────────────────────────────────────
# 8 questions reference a "Row 1-4" exhibit table that was an image in the source
# and never got captured during scraping. Each table below is rebuilt strictly
# from that question's own "Why each option is wrong" rationale in the raw set —
# so it shows the same data the learner needs without revealing the answer.
# Keyed by parsed card id ("Set X-Qn"). headers[0] is always the Row label.
EXHIBITS = {
    "Set B-Q74": {
        "headers": ["Row", "Execution mode", "Filtering attributes"],
        "rows": [
            ["Row 1", "Asynchronous", "firstname, lastname"],
            ["Row 2", "Synchronous", "(none)"],
            ["Row 3", "Asynchronous", "(none)"],
            ["Row 4", "Synchronous", "firstname, lastname"],
        ],
    },
    "Set C-Q3": {
        "headers": ["Row", "Requirement", "Proposed out-of-the-box feature"],
        "rows": [
            ["Row 1", "Show an aggregate value over related records", "Rollup column"],
            ["Row 2", "Identify potential duplicate records", "Duplicate detection rules"],
            ["Row 3", "Guide users through staged steps on a form", "Business process flow"],
            ["Row 4", "Display a calculated value while in mobile offline mode", "Formula column"],
        ],
    },
    "Set C-Q32": {
        "headers": ["Row", "Control base class", "Key lifecycle assumption"],
        "rows": [
            ["Row 1", "ReactControl", "init() receives an HTMLDivElement container; updateView returns a ReactElement"],
            ["Row 2", "ReactControl", "init() has no container parameter; updateView returns a ReactElement"],
            ["Row 3", "StandardControl", "Dataset values are initialized in init()"],
            ["Row 4", "StandardControl", "Uses allocatedWidth / allocatedHeight in updateView without calling trackContainerResize(true)"],
        ],
    },
    "Set C-Q52": {
        "headers": ["Row", "Extension step", "Start trigger", "Completion action"],
        "rows": [
            ["Row 1", "Pre-export", "OnDeploymentRequested", "UpdatePreExportStepStatus"],
            ["Row 2", "Delegated deployment", "OnApprovalStarted", "UpdateApprovalStatus"],
            ["Row 3", "Pre-deployment", "OnPreDeploymentStarted", "UpdatePreDeploymentStepStatus"],
            ["Row 4", "Pre-deployment Step Required", "OnDeploymentCompleted", "UpdatePreDeploymentStepStatus"],
        ],
    },
    "Set C-Q55": {
        "headers": ["Row", "Requirement", "Proposed runtime policy template"],
        "rows": [
            ["Row 1", "Add an api-version query string value to selected operations", "Set Query String Parameter"],
            ["Row 2", "Reroute selected operations to another relative path on the same service", "Route Request"],
            ["Row 3", "Select the backend host dynamically from connection parameters", "Set Host URL"],
            ["Row 4", "Change the host from api.contoso.com to eu.api.contoso.com", "Route Request"],
        ],
    },
    "Set F-Q30": {
        "headers": ["Row", "pageInput object passed to Xrm.Navigation.navigateTo"],
        "rows": [
            ["Row 1", '{ pageType: "custom", name: "<custom page logical name>", entityName: "<table>", recordId: "<id>" }'],
            ["Row 2", '{ pageType: "entityrecord", entityName: "<table>", recordId: "<id>" }'],
            ["Row 3", '{ pageType: "custom", pageId: "<custom page id>", entityName: "<table>", recordId: "<id>" }'],
            ["Row 4", '{ pageType: "webresource", webresourceName: "<page>.html", data: "..." }'],
        ],
    },
    "Set F-Q45": {
        "headers": ["Row", "Requirement", "Proposed solution component"],
        "rows": [
            ["Row 1", "Surface external ERP data without copying it into Dataverse", "Standard table"],
            ["Row 2", "Enforce validation on every server-side write path", "JavaScript web resource"],
            ["Row 3", "Expose a reusable operation that developers and flows can call", "Custom API"],
            ["Row 4", "Launch an interactive dialog from a model-driven command bar", "Cloud flow trigger"],
        ],
    },
    "Set F-Q57": {
        "headers": ["Row", "Endpoint type", "Stated behavior"],
        "rows": [
            ["Row 1", "Webhook", "Sends Dataverse server events to an external web application"],
            ["Row 2", "Event Hub", "Uses OAuth authorization"],
            ["Row 3", "Azure Service Bus relay contract", "An active listener is optional"],
            ["Row 4", "Azure Service Bus queue contract", "Requires a listener actively listening at the moment of post"],
        ],
    },
}

def build_exhibit_html(ex):
    """Render a reconstructed exhibit as a trusted (pre-escaped) HTML table."""
    heads = "".join(f"<th>{htmllib.escape(h)}</th>" for h in ex["headers"])
    body = []
    for row in ex["rows"]:
        cells = []
        for c in row:
            c = str(c)
            if c.startswith("{") or c.startswith("GET "):
                cells.append(f'<td><code class="cell-code">{htmllib.escape(c)}</code></td>')
            else:
                cells.append(f"<td>{htmllib.escape(c)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return ('<div class="exhibit-cap">📋 Exhibit (reconstructed from the explanation)</div>'
            f'<table class="exhibit-table"><thead><tr>{heads}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table>')

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

/* ── Quiz ── */
.sb-quiz{padding:6px 12px 10px;border-bottom:1px solid var(--sb2)}
.quiz-btn{display:flex;width:100%;padding:11px 14px;border:none;cursor:pointer;
  align-items:center;gap:10px;border-radius:8px;background:var(--sb2);
  color:#e2e8f0;font-size:.86rem;font-weight:600;transition:all .15s}
.quiz-btn:hover{background:#334155}
.quiz-btn.active{background:var(--sba);color:#fff}
.quiz-btn .qb-emoji{font-size:1.1rem}
.quiz-title{padding:11px 0;font-size:.85rem;font-weight:600;color:var(--txt)}
.quiz-wrap{flex:1;overflow-y:auto;padding:28px 24px;display:flex;
  justify-content:center;align-items:flex-start}
.quiz-inner{width:100%;max-width:760px}
/* setup */
.quiz-setup h2{font-size:1.35rem;margin-bottom:6px;color:#0f172a}
.quiz-setup .sub{color:var(--muted);font-size:.88rem;margin-bottom:22px}
.qs-label{font-weight:700;text-transform:uppercase;font-size:.7rem;
  letter-spacing:.06em;color:var(--muted);margin:18px 0 10px}
.dom-grid{display:flex;flex-direction:column;gap:8px}
.dom-row{display:flex;align-items:center;gap:11px;padding:11px 14px;
  border:1.5px solid var(--bdr);border-radius:9px;cursor:pointer;
  transition:all .15s;background:var(--surf)}
.dom-row:hover{border-color:var(--acc);background:#f8fafc}
.dom-row.on{border-color:var(--acc);background:#eff6ff}
.dom-row input{width:17px;height:17px;accent-color:var(--acc);cursor:pointer}
.dom-row .dn{flex:1;font-size:.9rem;font-weight:500}
.dom-row .dc{font-size:.76rem;color:var(--muted)}
.dom-row.all-row{background:#0f172a;border-color:#0f172a;color:#f1f5f9}
.dom-row.all-row:hover{background:#1e293b}
.dom-row.all-row .dc{color:#94a3b8}
.count-grid{display:flex;gap:10px;flex-wrap:wrap}
.count-btn{padding:12px 22px;border:1.5px solid var(--bdr);border-radius:9px;
  background:var(--surf);cursor:pointer;font-size:1rem;font-weight:600;
  color:var(--txt);transition:all .15s;min-width:64px}
.count-btn:hover{border-color:var(--acc)}
.count-btn.on{background:var(--acc);border-color:var(--acc);color:#fff}
.quiz-pool-note{font-size:.8rem;color:var(--muted);margin-top:10px}
.start-quiz-btn{margin-top:26px;width:100%;padding:14px;background:var(--acc);
  color:#fff;border:none;border-radius:10px;font-size:1rem;font-weight:600;
  cursor:pointer;transition:background .12s}
.start-quiz-btn:hover:not(:disabled){background:var(--acc2)}
.start-quiz-btn:disabled{background:#94a3b8;cursor:not-allowed}
/* runner */
.quiz-run-top{display:flex;justify-content:space-between;align-items:center;
  margin-bottom:8px}
.quiz-run-top .qn{font-size:.82rem;font-weight:600;color:var(--muted)}
.quiz-run-top .qd{font-size:.74rem;color:#cbd5e1;font-style:italic}
.quiz-pbar{height:6px;background:var(--bdr);border-radius:3px;margin-bottom:22px}
.quiz-pbar > div{height:100%;background:var(--acc);border-radius:3px;
  transition:width .3s}
.quiz-nav{display:flex;justify-content:space-between;margin-top:20px;gap:10px}
.quiz-nav button{padding:11px 24px;border-radius:9px;font-size:.9rem;
  font-weight:600;cursor:pointer;border:1px solid var(--bdr);background:var(--surf);
  color:var(--txt)}
.quiz-nav .next{background:var(--acc);border-color:var(--acc);color:#fff}
.quiz-nav .next:hover{background:var(--acc2)}
.quiz-nav button:disabled{opacity:.45;cursor:not-allowed}
/* results */
.quiz-score-card{text-align:center;padding:28px;background:var(--surf);
  border:1px solid var(--bdr);border-radius:14px;margin-bottom:24px}
.quiz-score-card .big{font-size:3rem;font-weight:800;margin:6px 0}
.quiz-score-card .lbl{color:var(--muted);font-size:.9rem}
.quiz-score-card.pass .big{color:var(--ok)}
.quiz-score-card.fail .big{color:var(--bad)}
.review-head{font-weight:700;font-size:1.05rem;margin:8px 0 14px;color:#0f172a}
.rev-card{border:1px solid var(--bdr);border-radius:12px;padding:18px 20px;
  margin-bottom:14px;background:var(--surf)}
.rev-stem{font-size:.92rem;line-height:1.65;white-space:pre-wrap;margin-bottom:14px}
.rev-ans{font-size:.85rem;margin:4px 0;line-height:1.5}
.rev-ans .you{color:var(--bad);font-weight:600}
.rev-ans .cor{color:var(--ok);font-weight:600}
.rev-rat{background:#f8fafc;border-left:4px solid var(--ok);border-radius:0 6px 6px 0;
  padding:11px 14px;margin:12px 0;font-size:.84rem;line-height:1.65;white-space:pre-wrap}
.goto-guide{display:inline-flex;align-items:center;gap:7px;padding:8px 15px;
  background:var(--beybg);border:1px solid var(--beybdr);border-radius:8px;
  color:var(--acc2);font-size:.83rem;font-weight:600;cursor:pointer;
  transition:background .12s}
.goto-guide:hover{background:#dbeafe}
.rev-src{font-size:.72rem;color:#cbd5e1;font-style:italic;margin-top:10px}
.quiz-results-actions{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;
  margin:8px 0 26px}
.quiz-results-actions button{padding:11px 22px;border-radius:9px;font-size:.9rem;
  font-weight:600;cursor:pointer;border:1px solid var(--bdr);background:var(--surf);
  color:var(--txt)}
.quiz-results-actions .primary{background:var(--acc);border-color:var(--acc);color:#fff}
.all-correct{text-align:center;padding:30px;color:var(--ok);font-weight:600}

/* ── Stem with code snippet ── */
.stem-text{white-space:pre-wrap}
.stem-text.stem-q{margin-top:12px;font-weight:600;color:#0f172a}
.code-snippet{background:var(--codebg);color:var(--codetxt);padding:14px 16px;
  border-radius:8px;overflow-x:auto;margin:13px 0;white-space:pre;tab-size:2;
  font-family:'Cascadia Code','Consolas','Courier New',monospace;
  font-size:.8rem;line-height:1.55}
.code-snippet code{font-family:inherit;background:none;padding:0;color:inherit}
.rev-stem .code-snippet{font-size:.78rem}

/* ── Reconstructed exhibit table ── */
.exhibit-cap{font-size:.72rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.04em;color:var(--muted);margin:14px 0 6px}
.exhibit-table{border-collapse:collapse;width:100%;margin:0 0 4px;
  font-size:.82rem;border:1px solid var(--bdr);border-radius:8px;overflow:hidden}
.exhibit-table th{background:#1e293b;color:#f1f5f9;padding:8px 11px;
  text-align:left;font-weight:600;white-space:nowrap}
.exhibit-table td{padding:8px 11px;border-top:1px solid var(--bdr);
  vertical-align:top;line-height:1.5}
.exhibit-table tr:nth-child(even) td{background:#f8fafc}
.exhibit-table td:first-child{font-weight:700;color:var(--muted);white-space:nowrap}
.cell-code{font-family:'Cascadia Code','Consolas',monospace;font-size:.92em;
  background:#f1f5f9;padding:2px 5px;border-radius:4px;display:inline-block;
  white-space:pre-wrap;word-break:break-word}
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
    const qb = document.getElementById('quiz-btn');
    if (qb) qb.classList.remove('active');
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
      <div class="fc-stem">${renderStem(q.stem, q.exhibit)}</div>
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

// Render a question stem, pulling any "Snippet" code block into a monospace
// <pre> so code/JSON/formulas stay readable instead of wrapping like prose.
// Shape in the source data: <scenario> \n Snippet \n <code> \n [<question?>]
function renderStem(stem, exhibitHtml) {
    const lines = String(stem).split('\n');

    // Exhibit case: the stem has a bare "Exhibit N" line and we have a
    // reconstructed table to drop in its place (scenario above, question below).
    if (exhibitHtml) {
        let ek = -1;
        for (let i = 0; i < lines.length; i++) {
            if (/^\s*exhibit\s*\d*\s*$/i.test(lines[i])) { ek = i; break; }
        }
        if (ek !== -1) {
            const lead = lines.slice(0, ek).join('\n').trim();
            const after = lines.slice(ek + 1).join('\n').trim();
            let h = '';
            if (lead)  h += `<div class="stem-text">${escHtml(lead)}</div>`;
            h += exhibitHtml;
            if (after) h += `<div class="stem-text stem-q">${escHtml(after)}</div>`;
            return h;
        }
    }

    let mark = -1;
    for (let i = 0; i < lines.length; i++) {
        if (/^\s*snippet\s*$/i.test(lines[i])) { mark = i; break; }
    }
    if (mark === -1) return `<div class="stem-text">${escHtml(stem)}</div>`;

    const lead = lines.slice(0, mark);
    let rest = lines.slice(mark + 1);
    while (rest.length && !rest[0].trim()) rest.shift();          // drop blank after marker

    // Peel a trailing prose question off the end (it follows the code block).
    const isQuestion = l => {
        const t = l.trim();
        if (!t || /[{};=]/.test(t)) return false;                 // looks like code
        if (/^(GET|POST|PUT|PATCH|DELETE|HTTP|OData|Prefer|Preference)\b/i.test(t)) return false;
        return /\?\s*$/.test(t) || /Select (only one answer|all that apply|TWO|THREE)/i.test(t);
    };
    const tail = [];
    while (rest.length) {
        const last = rest[rest.length - 1];
        if (!last.trim()) { rest.pop(); continue; }
        if (isQuestion(last)) tail.unshift(rest.pop());
        else break;
    }
    while (rest.length && !rest[rest.length - 1].trim()) rest.pop();

    let html = '';
    const leadText = lead.join('\n').trim();
    if (leadText) html += `<div class="stem-text">${escHtml(leadText)}</div>`;
    if (rest.length) html += `<pre class="code-snippet"><code>${escHtml(rest.join('\n'))}</code></pre>`;
    const tailText = tail.join('\n').trim();
    if (tailText) html += `<div class="stem-text stem-q">${escHtml(tailText)}</div>`;
    return html;
}

// ══ QUIZ MODE ═══════════════════════════════════════════════════════════════
// Cross-domain randomized quiz. Pool is flattened from CARDS; each item keeps
// its domain slug so a wrong answer can link straight to that concept guide.

const DOMAIN_NAME = {};            // slug -> display name
DOMAINS.forEach(([s,n,]) => DOMAIN_NAME[s] = n);

function buildQuizPool() {
    const pool = [];
    DOMAINS.forEach(([slug,,]) => {
        (CARDS[slug] || []).forEach(c => pool.push({...c, slug}));
    });
    return pool;
}
const QUIZ_POOL = buildQuizPool();

const COUNTS = [10, 20, 60, 80];
const quizCfg   = { domains: new Set(DOMAINS.map(d => d[0])), count: 20 };
let   quizState = null;   // {order:[cards], idx, answers:[Set,...]}

function openQuiz() {
    document.querySelectorAll('.db').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.getElementById('quiz-btn').classList.add('active');
    document.getElementById('panel-quiz').classList.add('active');
    if (!quizState) renderQuizSetup();   // keep an in-progress quiz on tab return
}

function poolFor(domSet) {
    return QUIZ_POOL.filter(c => domSet.has(c.slug));
}

function renderQuizSetup() {
    quizState = null;
    const inner = document.getElementById('quiz-inner');
    const allOn = quizCfg.domains.size === DOMAINS.length;
    const domRows = DOMAINS.map(([slug,name,]) => {
        const n = (CARDS[slug] || []).length;
        const on = quizCfg.domains.has(slug);
        return `<label class="dom-row ${on?'on':''}" data-slug="${slug}">
            <input type="checkbox" ${on?'checked':''} onchange="toggleDomain('${slug}')">
            <span class="dn">${name}</span><span class="dc">${n} Qs</span>
          </label>`;
    }).join('');
    const countBtns = COUNTS.map(n =>
        `<button class="count-btn ${quizCfg.count===n?'on':''}"
                 onclick="setCount(${n})">${n}</button>`).join('');
    inner.innerHTML = `
      <div class="quiz-setup">
        <h2>Build a practice quiz</h2>
        <p class="sub">Randomly sample questions from the domains you pick, answer
           them, then review every miss with a jump to the right concept guide.</p>
        <div class="qs-label">Domains</div>
        <div class="dom-grid">
          <label class="dom-row all-row ${allOn?'on':''}" onclick="toggleAll(event)">
            <input type="checkbox" ${allOn?'checked':''} onclick="event.stopPropagation()" onchange="toggleAll(event)">
            <span class="dn">All domains</span>
            <span class="dc">${QUIZ_POOL.length} Qs</span>
          </label>
          ${domRows}
        </div>
        <div class="qs-label">How many questions</div>
        <div class="count-grid">${countBtns}</div>
        <div class="quiz-pool-note" id="pool-note"></div>
        <button class="start-quiz-btn" id="start-btn" onclick="startQuiz()">Start quiz →</button>
      </div>`;
    updatePoolNote();
}

function updatePoolNote() {
    const avail = poolFor(quizCfg.domains).length;
    const note  = document.getElementById('pool-note');
    const btn   = document.getElementById('start-btn');
    if (!note) return;
    if (quizCfg.domains.size === 0) {
        note.textContent = 'Select at least one domain.';
        btn.disabled = true; return;
    }
    btn.disabled = false;
    const n = Math.min(quizCfg.count, avail);
    note.innerHTML = `Quiz will draw <strong>${n}</strong> question${n!==1?'s':''} `
        + `from a pool of <strong>${avail}</strong>.`
        + (quizCfg.count > avail
            ? ` (Only ${avail} available in the selected domains.)` : '');
}

function toggleDomain(slug) {
    if (quizCfg.domains.has(slug)) quizCfg.domains.delete(slug);
    else quizCfg.domains.add(slug);
    renderQuizSetup();
}
function toggleAll(e) {
    if (e) e.preventDefault();
    if (quizCfg.domains.size === DOMAINS.length) quizCfg.domains = new Set();
    else quizCfg.domains = new Set(DOMAINS.map(d => d[0]));
    renderQuizSetup();
}
function setCount(n) { quizCfg.count = n; renderQuizSetup(); }

function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length-1; i > 0; i--) {
        const j = Math.floor(Math.random()*(i+1));
        [a[i],a[j]] = [a[j],a[i]];
    }
    return a;
}

function startQuiz(customPool) {
    const base = customPool || poolFor(quizCfg.domains);
    if (base.length === 0) return;
    const n = customPool ? base.length : Math.min(quizCfg.count, base.length);
    const order = shuffle(base).slice(0, n);
    quizState = { order, idx: 0, answers: order.map(() => new Set()) };
    renderQuizQuestion();
}

function renderQuizQuestion() {
    const { order, idx, answers } = quizState;
    const q = order[idx];
    const letters = Object.keys(q.options);
    const multi = q.correct.length > 1;
    const sel = answers[idx];
    const inner = document.getElementById('quiz-inner');
    inner.innerHTML = `
      <div class="quiz-run-top">
        <span class="qn">Question ${idx+1} of ${order.length}</span>
        <span class="qd">${escHtml(DOMAIN_NAME[q.slug])}</span>
      </div>
      <div class="quiz-pbar"><div style="width:${(idx)/order.length*100}%"></div></div>
      <div class="flashcard">
        <div class="fc-stem">${renderStem(q.stem, q.exhibit)}</div>
        ${multi ? '<p class="multi-label">Select all that apply:</p>' : ''}
        <div class="options-list" id="quiz-opts">
          ${letters.map(l =>
            `<div class="opt ${sel.has(l)?'selected':''}" data-letter="${l}"
                  onclick="pickQuizOpt('${l}',${multi})">
               <span class="opt-letter">${l}.</span>
               <span>${escHtml(q.options[l])}</span>
             </div>`).join('')}
        </div>
      </div>
      <div class="quiz-nav">
        <button onclick="prevQuizQuestion()" ${idx===0?'disabled':''}>← Back</button>
        <button class="next" onclick="nextQuizQuestion()">
          ${idx === order.length-1 ? 'Finish & see score' : 'Next →'}
        </button>
      </div>`;
}

function pickQuizOpt(letter, multi) {
    const sel = quizState.answers[quizState.idx];
    if (multi) {
        if (sel.has(letter)) sel.delete(letter); else sel.add(letter);
    } else {
        sel.clear(); sel.add(letter);
    }
    document.querySelectorAll('#quiz-opts .opt').forEach(el =>
        el.classList.toggle('selected', sel.has(el.dataset.letter)));
}

function prevQuizQuestion() {
    if (quizState.idx > 0) { quizState.idx--; renderQuizQuestion(); }
}
function nextQuizQuestion() {
    if (quizState.idx < quizState.order.length-1) {
        quizState.idx++; renderQuizQuestion();
    } else {
        gradeQuiz();
    }
}

function setsEqual(a, b) {
    if (a.size !== b.size) return false;
    for (const x of a) if (!b.has(x)) return false;
    return true;
}

function gradeQuiz() {
    const { order, answers } = quizState;
    const wrong = [];
    let correct = 0;
    order.forEach((q, i) => {
        if (setsEqual(answers[i], new Set(q.correct))) correct++;
        else wrong.push({ q, chosen: answers[i] });
    });
    renderQuizResults(correct, order.length, wrong);
}

function fmtLetters(set, opts) {
    const ls = [...set].sort();
    if (ls.length === 0) return '(no answer)';
    return ls.map(l => `${l}. ${opts[l] || ''}`).join('  ·  ');
}

function renderQuizResults(correct, total, wrong) {
    const pct = Math.round(correct/total*100);
    const pass = pct >= 70;   // PL-400 pass mark is 700/1000
    const inner = document.getElementById('quiz-inner');
    const reviewHtml = wrong.length === 0
      ? `<div class="all-correct">🎉 Perfect score — every answer correct!</div>`
      : `<div class="review-head">Review your ${wrong.length} missed question${wrong.length!==1?'s':''}</div>`
        + wrong.map(({q, chosen}) => `
          <div class="rev-card">
            <div class="rev-stem">${renderStem(q.stem, q.exhibit)}</div>
            <div class="rev-ans"><span class="you">Your answer:</span> ${escHtml(fmtLetters(chosen, q.options))}</div>
            <div class="rev-ans"><span class="cor">Correct:</span> ${escHtml(fmtLetters(new Set(q.correct), q.options))}</div>
            ${q.rationale ? `<div class="rev-rat">${escHtml(q.rationale)}</div>` : ''}
            <button class="goto-guide" onclick="gotoGuide('${q.slug}')">
              📖 Read up: ${escHtml(DOMAIN_NAME[q.slug])} guide
            </button>
            <div class="rev-src">${q.id}</div>
          </div>`).join('');
    const retryWrong = wrong.length
      ? `<button onclick='retryWrong()'>🔁 Retry these ${wrong.length}</button>` : '';
    inner.innerHTML = `
      <div class="quiz-score-card ${pass?'pass':'fail'}">
        <div class="lbl">You scored</div>
        <div class="big">${pct}%</div>
        <div class="lbl">${correct} of ${total} correct${pass?' · above the 70% pass mark':' · below the 70% pass mark'}</div>
      </div>
      <div class="quiz-results-actions">
        <button class="primary" onclick="renderQuizSetup()">↺ New quiz</button>
        ${retryWrong}
      </div>
      ${reviewHtml}`;
    // stash the missed pool for "retry these"
    quizState._wrongPool = wrong.map(w => w.q);
}

function retryWrong() {
    const pool = quizState && quizState._wrongPool;
    if (pool && pool.length) startQuiz(pool);
}

function gotoGuide(slug) {
    showDomain(slug);
    activateTab(slug, 'guide');
    const scroll = document.querySelector(`#panel-${slug} .guide-scroll`);
    if (scroll) scroll.scrollTop = 0;
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
        for c in cards:
            if c["id"] in EXHIBITS:
                c["exhibit"] = build_exhibit_html(EXHIBITS[c["id"]])
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
  <div class="sb-quiz">
    <button class="quiz-btn" id="quiz-btn" onclick="openQuiz()">
      <span class="qb-emoji">📝</span><span>Practice Quiz</span>
    </button>
  </div>
  <nav class="sb-nav">{''.join(sb_items)}</nav>
  <div class="sb-foot">Space=reveal · G=got it · R=review</div>
</aside>
<main class="main">
  <div class="panel" id="panel-quiz">
    <div class="tabs"><span class="quiz-title">📝 Practice Quiz</span></div>
    <div class="quiz-wrap"><div class="quiz-inner" id="quiz-inner"></div></div>
  </div>
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
