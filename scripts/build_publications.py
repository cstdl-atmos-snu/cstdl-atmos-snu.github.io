"""Build publications.html from the CSTDL sheet's published "Web" tab.

The sheet is the only place paper information is entered. This script reads
the Web tab as CSV (URL in the SHEET_CSV_URL environment variable, or a local
file path given as the first argument) and writes publications.html.
"""
import csv
import html
import io
import os
import re
import sys
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PI_PATTERN = re.compile(r"\bD\. Kim\*?")


def load_rows(src):
    if src.startswith("http"):
        with urllib.request.urlopen(src, timeout=60) as r:
            text = r.read().decode("utf-8")
    else:
        with open(src, encoding="utf-8") as f:
            text = f.read()
    return [row for row in csv.DictReader(io.StringIO(text)) if (row.get("Title") or "").strip()]


def pub_key(p):
    """Chronological key: '2025.06' -> (2025, 6); '2025' -> (2025, 0)."""
    s = (p.get("Published") or p.get("Year") or "0").strip()
    y, _, m = s.partition(".")
    return (int(y or 0), int(m or 0))


def number_published(pubs):
    """Keep existing numbers; give new papers the next numbers in publication order."""
    numbered = [p for p in pubs if (p.get("No") or "").strip().isdigit()]
    new = sorted([p for p in pubs if not (p.get("No") or "").strip().isdigit()], key=pub_key)
    n = max([int(p["No"]) for p in numbered] or [0])
    for p in new:
        n += 1
        p["No"] = str(n)
    return sorted(pubs, key=lambda p: int(p["No"]), reverse=True)


def authors_html(a):
    return PI_PATTERN.sub(lambda m: f"<strong>{m.group(0)}</strong>", html.escape(a))


def status_label(s):
    if s.startswith("Revised"):
        return "Revised"
    return s


def entry(p, numbered=True):
    head = f'<span class="au">{authors_html(p["Authors"])}</span>'
    if numbered and p.get("Year"):
        head += f', {html.escape(p["Year"])}'
    parts = [head, f'<span class="ti">{html.escape(p["Title"])}</span>']
    venue = html.escape(p.get("Journal") or "")
    if p.get("Citation"):
        venue += (", " if venue else "") + html.escape(p["Citation"])
    if not numbered:
        venue += (", " if venue else "") + status_label(p["Status"])
    if venue:
        parts.append(f'<span class="jo">{venue}</span>')
    line = ". ".join(parts) + "."
    if p.get("DOI"):
        d = html.escape(p["DOI"])
        line += f' <a href="{d}">{d.replace("https://doi.org/", "doi:")}</a>'
    if p.get("Grants"):
        line += f'<span class="gr">Funding: {html.escape(p["Grants"])}</span>'
    num = f'<span class="no">{p["No"]}</span>' if numbered else ""
    return f"<li>{num}<p>{line}</p></li>"


def build(rows):
    published = number_published([r for r in rows if r["Status"] == "Published"])
    pending = [r for r in rows if r["Status"] != "Published"]
    rank = lambda r: 0 if r["Status"] == "Accepted" else (1 if r["Status"].startswith("Revised") else 2)
    pending.sort(key=rank)

    years = {}
    for p in published:
        years.setdefault((p.get("Year") or "Other").strip(), []).append(p)
    year_blocks = "\n".join(
        f'<section class="year" id="y{y}"><h3>{y}</h3><ol>{"".join(entry(p) for p in ps)}</ol></section>'
        for y, ps in years.items()
    )
    year_nav = "".join(f'<a href="#y{y}">{y}</a>' for y in years)

    with open(os.path.join(ROOT, "scripts", "publications_template.html"), encoding="utf-8") as f:
        tpl = f.read()
    return (
        tpl.replace("{{PENDING}}", "".join(entry(p, numbered=False) for p in pending))
        .replace("{{PUBLISHED}}", year_blocks)
        .replace("{{YEARNAV}}", year_nav)
        .replace("{{COUNT}}", str(len(published)))
        .replace("{{UPDATED}}", date.today().strftime("%B %Y"))
    )


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SHEET_CSV_URL")
    if not src:
        sys.exit("Set SHEET_CSV_URL to the published CSV link of the Web tab.")
    rows = load_rows(src)
    if not rows:
        sys.exit("The Web tab returned no papers; publications.html was left unchanged.")
    out = os.path.join(ROOT, "publications.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build(rows))
    print(f"Wrote {out} ({len(rows)} papers)")
