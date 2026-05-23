#!/usr/bin/env python3
"""
Parse the 5 PL-400 mock-exam QA files into structured data and emit:
  1. study_deck/   - Markdown flashcard decks grouped by exam domain (faithful restructure)
  2. _parsed/      - per-domain JSON-lines intermediate files (input for LLM synthesis)

The model never reads the raw 1.3MB; this script does all mechanical work.
"""
import re, json, glob, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
FILES = sorted(glob.glob(os.path.join(ROOT, "PL400_Practice_Set_*")))
DECK_DIR = os.path.join(ROOT, "study_deck")
PARSE_DIR = os.path.join(ROOT, "_parsed")

OPTION_RE = re.compile(r"^([A-Z])\.\s+(.*)$")
QHEAD_RE = re.compile(r"^Question\s+(\d+)\s*$")
STATUS_SET = {"Correct", "Incorrect"}
# markers that flag the option immediately following them
CORRECT_MARKERS = {"Correct answer", "Your answer is correct",
                   "Correct selection", "Your selection is correct"}
CHOSEN_MARKERS = {"Your answer is correct", "Your answer is incorrect",
                  "Your selection is correct", "Your selection is incorrect"}
ALL_MARKERS = CORRECT_MARKERS | CHOSEN_MARKERS
INSTRUCTION_RE = re.compile(r"^(Select only one answer\.|Select all that apply\.)\s*$")

# canonical domain name + exam weight, keyed by slug (Set F omits the weights)
DOMAIN_CANON = {
    "build_power_platform_solutions": ("Build Power Platform Solutions", "10–15%"),
    "create_a_technical_design": ("Create a Technical Design", "10–15%"),
    "develop_integrations": ("Develop Integrations", "10–15%"),
    "extend_the_platform": ("Extend the Platform", "30–35%"),
    "extend_the_user_experience": ("Extend the User Experience", "10–15%"),
    "implement_power_apps_improvements": ("Implement Power Apps Improvements", "10–15%"),
}

def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n").split("\n")

def split_questions(lines):
    blocks, cur, num = [], [], None
    for ln in lines:
        m = QHEAD_RE.match(ln.strip())
        if m:
            if cur:
                blocks.append((num, cur))
            num, cur = int(m.group(1)), []
        else:
            if num is not None:
                cur.append(ln)
    if cur:
        blocks.append((num, cur))
    return blocks

def clean(text):
    # collapse runs of blank lines, strip trailing ws
    out, blank = [], 0
    for ln in text:
        if ln.strip() == "":
            blank += 1
            if blank <= 1:
                out.append("")
        else:
            blank = 0
            out.append(ln.rstrip())
    return "\n".join(out).strip()

def parse_block(num, body):
    """Return dict with status, stem, options[], correct letter, rationale, domain."""
    # locate section anchors
    idx_overall = idx_resources = idx_domain = None
    for i, ln in enumerate(body):
        s = ln.strip()
        if s == "Overall explanation" and idx_overall is None:
            idx_overall = i
        elif s == "Resources":
            idx_resources = i
        elif s == "Domain":
            idx_domain = i

    status = body[0].strip() if body and body[0].strip() in STATUS_SET else ""
    start = 1 if status else 0

    # domain value = line after "Domain"
    domain = ""
    if idx_domain is not None:
        for ln in body[idx_domain + 1:]:
            if ln.strip():
                domain = ln.strip()
                break

    # overall explanation (canonical rationale) -> trim the repetitive
    # "Why the other options are incorrect" tail to keep it tight.
    rationale = ""
    if idx_overall is not None:
        end = idx_resources if idx_resources is not None else len(body)
        ov = body[idx_overall + 1:end]
        ov_text = clean(ov)
        cut = re.split(r"\n\s*Why the other options are incorrect:?\s*\n", ov_text, maxsplit=1)
        rationale = cut[0].strip()

    # single pass over the pre-Overall region: stem lines, then options.
    # markers that flag an option always appear on the line(s) just above it,
    # so we buffer pending markers and apply them when the option appears.
    opt_end = idx_overall if idx_overall is not None else len(body)
    options, correct, chosen = [], [], []
    pending = set()
    stem_lines, seen_option = [], False
    cur_opt = None
    for ln in body[start:opt_end]:
        s = ln.strip()
        m = OPTION_RE.match(s)
        if m:
            seen_option = True
            letter, text = m.group(1), m.group(2)
            cur_opt = {"letter": letter, "text": text.strip(), "_exp": []}
            options.append(cur_opt)
            if pending & CORRECT_MARKERS:
                correct.append(letter)
            if pending & CHOSEN_MARKERS:
                chosen.append(letter)
            pending = set()
            continue
        if s in ALL_MARKERS:
            pending.add(s)
            cur_opt = None  # marker breaks any explanation capture
            continue
        if s == "Explanation":
            if cur_opt is not None:
                cur_opt["_exp_mode"] = True
            continue
        if not seen_option:
            if not INSTRUCTION_RE.match(s):
                stem_lines.append(ln)
        elif cur_opt is not None and cur_opt.get("_exp_mode") and s:
            cur_opt["_exp"].append(s)

    stem = clean(stem_lines)
    for o in options:
        o["exp"] = " ".join(o.pop("_exp", [])).strip()
        o.pop("_exp_mode", None)

    return {
        "num": num,
        "status": status,
        "stem": stem,
        "options": options,
        "correct": correct,          # list of letters (supports multi-select)
        "chosen": chosen,
        "rationale": rationale,
        "domain": domain or "Uncategorized",
    }

def domain_slug(d):
    base = re.sub(r"\s*\(\d+.*?\)\s*$", "", d).strip()
    return re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")

def canon(d):
    """-> (slug, display_name, weight). Normalizes Set F's weight-less labels."""
    slug = domain_slug(d)
    name, weight = DOMAIN_CANON.get(slug, (d, "?"))
    return slug, name, weight

def main():
    os.makedirs(DECK_DIR, exist_ok=True)
    os.makedirs(PARSE_DIR, exist_ok=True)
    by_domain = {}   # slug -> {"name","weight","qs":[...]}
    set_counts = {}
    for path in FILES:
        set_name = os.path.basename(path).replace("PL400_Practice_Set_", "Set ")
        blocks = split_questions(read_lines(path))
        set_counts[set_name] = len(blocks)
        for num, body in blocks:
            q = parse_block(num, body)
            q["set"] = set_name
            slug, name, weight = canon(q["domain"])
            d = by_domain.setdefault(slug, {"name": name, "weight": weight, "qs": []})
            d["qs"].append(q)

    # ---- emit per-domain JSON-lines (synthesis input) + markdown deck ----
    index_lines = ["# PL-400 Study Deck — Index\n",
                   f"_Generated from {len(FILES)} mock-exam sets · {sum(len(d['qs']) for d in by_domain.values())} questions._\n"]
    total = 0
    for slug in sorted(by_domain, key=lambda s: -len(by_domain[s]["qs"])):
        d = by_domain[slug]
        qs, name, weight = d["qs"], d["name"], d["weight"]
        total += len(qs)

        # JSON-lines for subagents (compact, no markdown noise)
        with open(os.path.join(PARSE_DIR, f"{slug}.jsonl"), "w", encoding="utf-8") as jf:
            for q in qs:
                jf.write(json.dumps({
                    "id": f'{q["set"]}-Q{q["num"]}',
                    "stem": q["stem"],
                    "options": {o["letter"]: o["text"] for o in q["options"]},
                    "correct": q["correct"],
                    "rationale": q["rationale"],
                }, ensure_ascii=False) + "\n")

        # Markdown flashcard deck
        md = [f"# {name}  \n", f"_Exam weight {weight} · {len(qs)} questions across all sets._\n", "---\n"]
        for n, q in enumerate(qs, 1):
            md.append(f"### {n}. {q['stem']}\n")
            cset = set(q["correct"])
            for o in q["options"]:
                mark = " ✅" if o["letter"] in cset else ""
                md.append(f"- **{o['letter']}.** {o['text']}{mark}")
            md.append("")
            ans = []
            for L in q["correct"]:
                ot = next((o["text"] for o in q["options"] if o["letter"] == L), "")
                ans.append(f"{L}. {ot}")
            md.append(f"> **Answer:** {' · '.join(ans) if ans else '⚠️ not detected'}\n")
            if q["rationale"]:
                md.append(f"{q['rationale']}\n")
            md.append(f"<sub>{q['set']} · Q{q['num']}</sub>\n")
            md.append("---\n")
        with open(os.path.join(DECK_DIR, f"{slug}.md"), "w", encoding="utf-8") as mf:
            mf.write("\n".join(md))

        index_lines.append(f"- [{name}](study_deck/{slug}.md) — weight {weight}, {len(qs)} questions")

    with open(os.path.join(ROOT, "STUDY_INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines) + "\n")

    # ---- report ----
    print("Per-set question counts:", set_counts)
    print(f"Total parsed: {total}")
    print("Per-domain counts:")
    for slug in sorted(by_domain):
        qs = by_domain[slug]["qs"]
        missing = sum(1 for q in qs if not q["correct"])
        multi = sum(1 for q in qs if len(q["correct"]) > 1)
        norat = sum(1 for q in qs if not q["rationale"])
        print(f"  {slug:34} {len(qs):4}  | no-correct:{missing}  multi:{multi}  no-rationale:{norat}")

if __name__ == "__main__":
    main()
