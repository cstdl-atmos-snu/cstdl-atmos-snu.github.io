"""Write src/content/publications/*.md from the CSTDL Google Sheet.

The sheet's "Web" tab (published as CSV; URL in SHEET_CSV_URL or a local
path as the first argument) is the single source of paper information.
Reading and parsing the sheet is shared with other templates in
sheet_core.py; this file only formats the result for Scholar-Lite.
"""
import json
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheet_core import load_papers  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "src", "content", "publications")
STATUS = {"Published": "published", "Accepted": "accepted", "Revised": "revised", "Submitted": "submitted"}
MONTH = {m: i + 1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}


def display_name(last, first):
    if first is None:            # corporate author
        return last
    if last == "others":
        return "et al."
    star = "*" if last.endswith("*") else ""
    last = last.rstrip("*")
    return f"{first} {last}{star}".strip() if first else f"{last}{star}"


def slugify(s, n=40):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:n].strip("-")


def main(src):
    papers = load_papers(src)
    if not papers:
        sys.exit("The Web tab returned no papers. Check that it is published as CSV.")
    this_year = date.today().year

    published = [p for p in papers if p["status"] == "Published"]
    numbered = [p for p in published if p["no"].isdigit()]
    new = sorted([p for p in published if not p["no"].isdigit()], key=lambda p: (p["year"], MONTH.get(p["month"], 0)))
    n = max([int(p["no"]) for p in numbered] or [0])
    for p in new:
        n += 1
        p["no"] = str(n)

    os.makedirs(OUT_DIR, exist_ok=True)
    for f in os.listdir(OUT_DIR):
        if f.endswith(".md"):
            os.remove(os.path.join(OUT_DIR, f))

    for i, p in enumerate(papers):
        status = STATUS.get(p["status"], "submitted")
        year = int(p["year"]) if p["year"].isdigit() else this_year
        venue = p["venue"].replace(" (book chapter)", "").replace(" (preprint)", "")
        fm = {
            "title": p["title"],
            "authors": [display_name(l, f) for l, f in p["authors"]],
            "year": year,
            "venue": venue,
            "type": "paper",
            "status": status,
            "sortKey": year * 100 + MONTH.get(p["month"], 0),
        }
        if status == "published":
            fm["number"] = int(p["no"])
        if p["citation"]:
            fm["citation"] = p["citation"]
        if p["doi"]:
            fm["doi"] = p["doi"]
        if p["funding"]:
            fm["funding"] = p["funding"]
        lines = ["---"] + [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fm.items()] + ["---", ""]
        prefix = f'{int(p["no"]):03d}' if status == "published" else f"pending-{i:03d}"
        name = f"{prefix}-{slugify(p['title'])}.md"
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))

    print(f"Wrote {len(papers)} papers to {OUT_DIR} "
          f"({len(published)} published, {len(papers) - len(published)} in press or under review)")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SHEET_CSV_URL", "")
    if not src:
        sys.exit("Set SHEET_CSV_URL to the published CSV link of the Web tab.")
    main(src)
