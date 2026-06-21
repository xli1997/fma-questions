"""Generate an HTML page with pop-up behavior for physics questions.

- Clicking the (A) link opens a modal showing the (A) picture and buttons.
- Clicking the (B) link opens a modal showing the (B) picture and buttons.
- Buttons open the (C) PDF or (D) BookSolution in a new browser window (if present).
- Column E (Difficulty) shows difficulty values from difficulty.json (display only, no saving).
  Each entry can be:
    - A single integer (e.g., "2008-02": 0) → displays one difficulty value
    - A list of three integers (e.g., "2008-01": [0, 0, 0]) → displays three difficulty values

Creates `question-pop-up.html` next to this script.
"""

import os
import json
from pathlib import Path
import html


ROOT = Path(__file__).resolve().parent

ALL_IN_ONE_DIR = ROOT / 'F=ma-1by1' / 'all-in-1'
PIC_BY_YEAR_DIR = ROOT / 'pic-question-by-year'
KEVIN_DIR = ROOT / 'KevinHuang'
BOOK_SOLUTION_DIR = ROOT / 'BookSolution'
DIFFICULTY_JSON = ROOT / 'difficulty.json'

OUT_HTML = ROOT / 'question-pop-up.html'

# Global difficulty data (loaded once)
difficulty_data = {}


def parse_name(name: str):
    base = os.path.splitext(name)[0]
    parts = base.split('-')
    if len(parts) == 3:
        year, section, num = parts
    elif len(parts) == 2:
        year, num = parts
        section = ''
    else:
        year = parts[0]
        section = ''
        num = parts[-1]
    return year, section, num.lstrip('0') or '0', base


def load_difficulty():
    """Load difficulty.json into global dictionary."""
    global difficulty_data
    if DIFFICULTY_JSON.exists():
        with open(DIFFICULTY_JSON, 'r', encoding='utf-8') as f:
            difficulty_data = json.load(f)
    else:
        difficulty_data = {}


def get_difficulty(key: str):
    """Get difficulty level for a key (e.g., '2008-01').
    Returns either a single value (int) or a list of three values [val1, val2, val3].
    """
    return difficulty_data.get(key, 0)


def find_pic_by_year(year: str, section: str, basename: str, num_str: str):
    folder_name = f"{year}-{section}" if section else year
    candidate = PIC_BY_YEAR_DIR / folder_name / f"{basename}.jpg"
    if candidate.exists():
        return candidate
    candidate2 = PIC_BY_YEAR_DIR / year / f"{basename}.jpg"
    if candidate2.exists():
        return candidate2
    try:
        num_i = int(num_str)
    except ValueError:
        num_i = num_str
    alt_name = f"question_{num_i}.jpg"
    candidate3 = PIC_BY_YEAR_DIR / folder_name / alt_name
    if candidate3.exists():
        return candidate3
    candidate4 = PIC_BY_YEAR_DIR / year / alt_name
    if candidate4.exists():
        return candidate4
    if isinstance(num_i, int) and 1 <= num_i < 10:
        alt_name_zero = f"question_0{num_i}.jpg"
        candidate5 = PIC_BY_YEAR_DIR / folder_name / alt_name_zero
        if candidate5.exists():
            return candidate5
        candidate6 = PIC_BY_YEAR_DIR / year / alt_name_zero
        if candidate6.exists():
            return candidate6
    return None


def find_pdf(year: str, section: str, num_str: str):
    section_key = section if section else ''
    folder_name = f"fma_{year}{section_key}_problems"
    pdf_dir = KEVIN_DIR / folder_name
    if not pdf_dir.exists():
        return None
    try:
        num_i = int(num_str)
    except ValueError:
        num_i = num_str
    pdf_name = f"{year}{section_key}_F_ma_Exam__Problem_{num_i}.pdf"
    candidate = pdf_dir / pdf_name
    if candidate.exists():
        return candidate
    for f in pdf_dir.iterdir():
        if f.is_file() and f.name.lower().endswith('.pdf') and f"Problem_{num_i}" in f.name:
            return f
    return None


def find_book_solution(year: str, section: str, num_str: str):
    folder_name = f"{year}-{section}" if section else year
    try:
        num_i = int(num_str)
    except ValueError:
        num_i = num_str
    if section:
        file_name = f"{year}.{section}.{num_i}.jpg"
    else:
        file_name = f"{year}.{num_i}.jpg"
    candidate = BOOK_SOLUTION_DIR / folder_name / file_name
    if candidate.exists():
        return candidate
    candidate2 = BOOK_SOLUTION_DIR / year / file_name
    if candidate2.exists():
        return candidate2
    return None


def make_file_link(path: Path):
    return f"file://{path.resolve()}"


def generate():
    rows = []
    if not ALL_IN_ONE_DIR.exists():
        print(f"All-in-one folder not found: {ALL_IN_ONE_DIR}")
        return

    jpgs = sorted([p.name for p in ALL_IN_ONE_DIR.iterdir() if p.is_file() and p.name.lower().endswith('.jpg')])

    load_difficulty()
    for j in jpgs:
        year, section, num_str, basename = parse_name(j)

        a_path = ALL_IN_ONE_DIR / j
        b_path = find_pic_by_year(year, section, basename, num_str)
        c_path = find_pdf(year, section, num_str)
        d_path = find_book_solution(year, section, num_str)

        # Build difficulty key: include section (e.g. 'A' or 'B') when present
        if section:
            difficulty_key = f'{year}-{section}-{num_str.zfill(2)}'
        else:
            difficulty_key = f'{year}-{num_str.zfill(2)}'
        difficulty_val = get_difficulty(difficulty_key)
        
        # Handle both single values and lists of three values
        if isinstance(difficulty_val, list):
            # difficulty_val is a list [val1, val2, val3]
            val1, val2, val3 = difficulty_val[0], difficulty_val[1], difficulty_val[2]
            difficulty_display = f'<span class="difficulty-value">{val1}</span> <span class="difficulty-value">{val2}</span> <span class="difficulty-value">{val3}</span>'
        else:
            # difficulty_val is a single integer
            difficulty_display = f'<span class="difficulty-value">{difficulty_val}</span>'

        if c_path:
            a_link = f'<a href="#" class="a-link" data-a-src="{make_file_link(a_path)}" data-c-src="{make_file_link(c_path)}' + (f'" data-d-src="{make_file_link(d_path)}' if d_path else '" data-d-src=""') + f'">(A) {html.escape(j)}</a>'
        else:
            a_link = f'<a href="#" class="a-link" data-a-src="{make_file_link(a_path)}" data-c-src=""' + (f' data-d-src="{make_file_link(d_path)}"' if d_path else ' data-d-src=""') + f'>(A) {html.escape(j)}</a>'
        if b_path:
            b_link = f'<a href="#" class="b-link" data-b-src="{make_file_link(b_path)}" data-b-name="{html.escape(b_path.name)}"'
            if c_path:
                if d_path:
                    b_link += f' data-c-src="{make_file_link(c_path)}" data-d-src="{make_file_link(d_path)}">(B) {html.escape(b_path.name)}</a>'
                else:
                    b_link += f' data-c-src="{make_file_link(c_path)}" data-d-src="">(B) {html.escape(b_path.name)}</a>'
            else:
                if d_path:
                    b_link += f' data-c-src="" data-d-src="{make_file_link(d_path)}">(B) {html.escape(b_path.name)}</a>'
                else:
                    b_link += f' data-c-src="" data-d-src="">(B) {html.escape(b_path.name)}</a>'
        else:
            b_link = '(B) —'

        if c_path:
            c_link = f'<a href="{make_file_link(c_path)}" target="_blank">(C) {html.escape(c_path.name)}</a>'
        else:
            c_link = '(C) —'

        if d_path:
            d_link = f'<a href="{make_file_link(d_path)}" target="_blank">(D) {html.escape(d_path.name)}</a>'
        else:
            d_link = '(D) —'

        rows.append((a_link, b_link, difficulty_display, c_link, d_link))


    with OUT_HTML.open('w', encoding='utf-8') as f:
        f.write("<!doctype html>\n<html><head><meta charset=\"utf-8\"><title>Question pop-up</title>\n")
        f.write("<style>\n")
        f.write("  body{font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; padding:12px;}\n")
        f.write("  table{border-collapse:collapse; width:100%;}\n")
        f.write("  th{ text-align:left; padding:8px 10px; border-bottom:1px solid #ccc; background:#f7f7f7;}\n")
        f.write("  td{ vertical-align:top; padding:6px 8px; border-bottom:1px solid #eee; }\n")
        f.write("  .col-a{width:20%;} .col-b{width:20%;} .col-e{width:15%;} .col-c{width:22.5%;} .col-d{width:22.5%;}\n")
        f.write("  .difficulty-value{ font-weight:bold; color:#007bff; font-size:15px; padding:2px 8px; display:inline-block; margin-right:4px; }\n")
        f.write("  .modal-overlay{ display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); align-items:center; justify-content:center; z-index:1000;}\n")
        f.write("  .modal{ position:relative; background:#fff; padding:12px; max-width:96vw; max-height:94vh; min-width:320px; min-height:240px; overflow:auto; border-radius:6px; box-shadow:0 8px 30px rgba(0,0,0,0.25);}\n")
        f.write("  .modal img{ max-width:94vw; max-height:90vh; min-width:200px; min-height:150px; display:block; margin-bottom:8px; background:#f7f7f7; }\n")
        f.write("  .modal .controls{ position:absolute; right:12px; bottom:12px; display:flex; gap:8px; align-items:center; }\n")
        f.write("  .btn{ padding:8px 12px; background:#007bff; color:#fff; border:none; border-radius:4px; cursor:pointer; }\n")
        f.write("  .btn:disabled{ background:#999; cursor:default; }\n")
        f.write("</style>\n")
        f.write("</head><body>\n")
        f.write(f"<h1>Question pop-up ({len(rows)})</h1>\n")
        f.write("<table>\n")
        f.write("  <thead><tr><th class=\"col-a\">A (all-in-1)</th><th class=\"col-e\">E (Difficulty)</th><th class=\"col-b\">B (pic-by-year)</th><th class=\"col-c\">C (pdf)</th><th class=\"col-d\">D (BookSolution)</th></tr></thead>\n")
        f.write("  <tbody>\n")
        for row in rows:
            a, b, e, c, d = row
            f.write(f"    <tr><td class=\"col-a\">{a}</td><td class=\"col-e\">{e}</td><td class=\"col-b\">{b}</td><td class=\"col-c\">{c}</td><td class=\"col-d\">{d}</td></tr>\n")
        f.write("  </tbody>\n")
        f.write("</table>\n")
        f.write("<div id=\"modalOverlay\" class=\"modal-overlay\">\n")
        f.write("  <div class=\"modal\">\n")
        f.write("    <div id=\"modalBody\">\n")
        f.write("      <img id=\"modalImage\" src=\"\" alt=\"question\">\n")
        f.write("      <div class=\"controls\">\n")
        f.write("        <button id=\"openPdfBtn\" class=\"btn\">Solution</button>\n")
        f.write("        <button id=\"openDBtn\" class=\"btn\">Answer</button>\n")
        f.write("        <button id=\"closeBtn\" class=\"btn\" style=\"background:#6c757d\">Close</button>\n")
        f.write("      </div>\n")
        f.write("    </div>\n")
        f.write("  </div>\n")
        f.write("</div>\n")
        f.write("<script>\n")
        f.write("document.addEventListener('DOMContentLoaded', function(){\n")
        f.write("  const overlay = document.getElementById('modalOverlay');\n")
        f.write("  const img = document.getElementById('modalImage');\n")
        f.write("  const openPdfBtn = document.getElementById('openPdfBtn');\n")
        f.write("  const openDBtn = document.getElementById('openDBtn');\n")
        f.write("  const closeBtn = document.getElementById('closeBtn');\n")
        f.write("  let currentPdf = '';\n")
        f.write("  let currentD = '';\n")
        f.write("  function bindPopLinks(selector, srcAttr){\n")
        f.write("    document.querySelectorAll(selector).forEach(function(el){\n")
        f.write("      el.addEventListener('click', function(ev){\n")
        f.write("        ev.preventDefault();\n")
        f.write("        const src = el.getAttribute(srcAttr);\n")
        f.write("        const csrc = el.getAttribute('data-c-src');\n")
        f.write("        const dsrc = el.getAttribute('data-d-src');\n")
        f.write("        if(src){ img.src = src; } else { img.src = ''; }\n")
        f.write("        currentPdf = csrc || '';\n")
        f.write("        currentD = dsrc || '';\n")
        f.write("        openPdfBtn.disabled = !currentPdf;\n")
        f.write("        openDBtn.disabled = !currentD;\n")
        f.write("        overlay.style.display = 'flex';\n")
        f.write("      });\n")
        f.write("    });\n")
        f.write("  }\n")
        f.write("  bindPopLinks('.b-link','data-b-src');\n")
        f.write("  bindPopLinks('.a-link','data-a-src');\n")
        f.write("  openPdfBtn.addEventListener('click', function(){ if(currentPdf){ window.open(currentPdf, '_blank'); } });\n")
        f.write("  openDBtn.addEventListener('click', function(){ if(currentD){ window.open(currentD, '_blank'); } });\n")
        f.write("  closeBtn.addEventListener('click', function(){ overlay.style.display = 'none'; img.src = ''; currentPdf = ''; currentD = ''; openDBtn.disabled = true; openPdfBtn.disabled = true; });\n")
        f.write("  overlay.addEventListener('click', function(ev){ if(ev.target === overlay){ overlay.style.display = 'none'; img.src = ''; currentPdf = ''; currentD = ''; openDBtn.disabled = true; openPdfBtn.disabled = true; } });\n")
        f.write("});\n")
        f.write("</script>\n")
        f.write("</body></html>\n")

    print(f"Wrote {OUT_HTML} with {len(rows)} entries")


if __name__ == '__main__':
    generate()
