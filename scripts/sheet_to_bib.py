"""Generate assets/ref.bib from the CSTDL Google Sheet.

The sheet is the single place where papers are entered. Its "Web" tab is
published as CSV; this script reads it (URL in SHEET_CSV_URL, or a local
file path as the first argument) and writes a BibTeX file that Jekyll
Scholar turns into the publications page.

The script is split in two parts so the website template can be swapped
later: load_papers() returns plain records independent of any template;
to_bibtex() is the template-specific output.
"""
import csv
import io
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "ref.bib")
MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
PENDING_LABEL = {"Accepted": "Accepted", "Submitted": "Submitted"}

# ---------------------------------------------------------------- common part

INITIAL_PART = re.compile(r"^(?:[A-ZÀ-Þ]{1,2}\.?|[A-ZÀ-Þ][a-z]\.|(?:[A-ZÀ-Þ]\.){2,3})$")


def is_initials(tok):
    """'D.', 'S. J.', 'D.-Y.', 'N.-Y', 'M' -> True; 'Kim', 'Wu', 'An' -> False."""
    parts = [x for x in re.split(r"[\s-]+", tok.strip().rstrip("*")) if x]
    return bool(parts) and all(INITIAL_PART.match(x) for x in parts)


def parse_authors(s):
    """Turn the homepage-style author string into a list of (last, first)."""
    s = s.strip().rstrip(".")
    s = re.sub(r"\s*\(including [^)]*\)", "", s)          # '(including D. Kim)'
    s = re.sub(r",?\s+and\s+Coauthors|,?\s+et al\.?", ", and others", s)
    corporate = None
    if ";" in s:                                           # 'CLIVAR ... Working Group; D. Waliser, ...'
        corporate, s = [x.strip() for x in s.split(";", 1)]
    s = re.sub(r",?\s+and\s+", ", ", s)
    toks = [t.strip() for t in s.split(",") if t.strip()]
    names, pending_last = [], None
    for t in toks:
        if t == "others":
            names.append(("others", ""))
            continue
        if pending_last is not None and is_initials(t):    # 'Kim' + 'M.'  -> Kim, M.
            names.append((pending_last, t))
            pending_last = None
            continue
        if pending_last is not None:                       # lone surname with no initials
            names.append((pending_last, ""))
            pending_last = None
        if " " in t and not is_initials(t):                # 'S. J. Camargo', 'A. D. Del Genio'
            parts = t.split()
            i = 0
            while i < len(parts) - 1 and is_initials(parts[i]):
                i += 1
            if i == 0:
                if is_initials(parts[-1]):                 # 'Inoue N.' (surname first, no comma)
                    names.append((" ".join(parts[:-1]), parts[-1]))
                else:                                      # 'Del Genio' (surname, initials follow)
                    pending_last = t
            
            else:
                names.append((" ".join(parts[i:]), " ".join(parts[:i])))
        elif is_initials(t):                               # stray initials with no surname before
            names.append((t, ""))
        else:
            pending_last = t.rstrip(".") if t.endswith(".") else t
    if pending_last is not None:
        names.append((pending_last, ""))
    if corporate:
        names.insert(0, (corporate, None))
    return names


def split_citation(c):
    """'52, e2025GL115189' -> ('52', 'e2025GL115189'); '38, 4625–4639' -> ('38', '4625--4639')."""
    c = (c or "").strip()
    if not c:
        return "", ""
    first, _, rest = c.partition(",")
    first, rest = first.strip(), rest.strip()
    if not rest:
        if re.fullmatch(r"\d+", first):
            return first, ""
        return "", first.replace("–", "--")
    if re.fullmatch(r"\d+", first):
        return first, re.sub(r"(?<=\d)[–-](?=\d)", "--", rest).replace(" ", "")
    return "", c


def load_papers(src):
    if src.startswith("http"):
        with urllib.request.urlopen(src, timeout=60) as r:
            text = r.read().decode("utf-8")
    else:
        with open(src, encoding="utf-8") as f:
            text = f.read()
    papers = []
    for row in csv.DictReader(io.StringIO(text)):
        if not (row.get("Title") or "").strip():
            continue
        status = row["Status"].strip()
        published = (row.get("Published") or "").strip()
        year = (row.get("Year") or published[:4]).strip()
        month = ""
        if "." in published:
            m = published.split(".")[1]
            if m.isdigit() and 1 <= int(m) <= 12:
                month = MONTHS[int(m) - 1]
        volume, pages = split_citation(row.get("Citation"))
        papers.append({
            "status": "Revised" if status.startswith("Revised") else status,
            "no": (row.get("No") or "").strip(),
            "authors": parse_authors(row["Authors"]),
            "year": year,
            "month": month,
            "title": row["Title"].strip(),
            "venue": (row.get("Journal") or "").strip(),
            "citation": (row.get("Citation") or "").strip(),
            "volume": volume,
            "pages": pages,
            "doi": (row.get("DOI") or "").strip().replace("https://doi.org/", ""),
            "funding": (row.get("Grants") or "").strip(),
        })
    return papers

# ------------------------------------------------------- template-specific part


def esc(s):
    return s.replace("\\", "").replace("&", r"\&").replace("%", r"\%").replace("#", r"\#").replace("_", r"\_")


def bib_author(names):
    out = []
    for last, first in names:
        if first is None:                                   # corporate author
            out.append("{" + esc(last) + "}")
        elif last == "others":
            out.append("others")
        else:
            out.append(f"{esc(last)}, {esc(first)}" if first else esc(last))
    return " and ".join(out)


def to_bibtex(papers):
    entries, used = [], set()
    published = [p for p in papers if p["status"] == "Published"]
    published.sort(key=lambda p: (int(p["no"]) if p["no"].isdigit() else 10_000, p["year"], p["month"]), reverse=True)
    pending = [p for p in papers if p["status"] != "Published"]
    for p in published + pending:
        first_last = (re.sub(r"[^A-Za-z]", "", (p["authors"][0][0] if p["authors"] else "anon")).lower() or "anon")[:20]
        key = f'{first_last}{p["year"] or "inprep"}{p["no"]}'
        while key in used:
            key += "a"
        used.add(key)
        f = {"author": bib_author(p["authors"]), "title": "{" + esc(p["title"]) + "}"}
        venue = p["venue"]
        if p["status"] != "Published" or "preprint" in venue.lower():
            kind = "unpublished"
            label = PENDING_LABEL.get(p["status"], "In revision" if p["status"] == "Revised" else p["status"])
            clean_venue = venue.replace(" (preprint)", "")
            f["note"] = esc(", ".join(x for x in [clean_venue, label] if x))
            if p["year"]:
                f["year"] = p["year"]
        elif "(book chapter)" in venue:
            kind = "incollection"
            f["booktitle"] = esc(venue.replace(" (book chapter)", ""))
            f["year"] = p["year"]
            if re.search(r"\d+-\d+", p["citation"]):
                f["pages"] = re.search(r"\d+-\d+", p["citation"]).group(0).replace("-", "--")
            if "Chap." in p["citation"]:
                f["note"] = esc(p["citation"])
        else:
            kind = "article"
            f["journal"] = esc(venue)
            f["year"] = p["year"]
            if p["month"]:
                f["month"] = p["month"]
            if p["volume"]:
                f["volume"] = p["volume"]
            if p["pages"]:
                f["pages"] = esc(p["pages"])
        if p["doi"] and kind != "unpublished":
            f["doi"] = p["doi"]
        if p["funding"]:
            f["funding"] = esc(p["funding"])
        body = ",\n".join(
            f"  {k} = {v}" if k == "month" else f"  {k} = {{{v}}}" for k, v in f.items())
        entries.append(f"@{kind}{{{key},\n{body}\n}}")
    return "\n\n".join(entries) + "\n"


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SHEET_CSV_URL", "")
    if not src:
        print("SHEET_CSV_URL is not set; keeping the existing assets/ref.bib.")
        sys.exit(0)
    papers = load_papers(src)
    if not papers:
        sys.exit("The Web tab returned no papers. Check that it is published as CSV.")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(to_bibtex(papers))
    n_pub = sum(p["status"] == "Published" for p in papers)
    print(f"Wrote {OUT}: {n_pub} published, {len(papers) - n_pub} in press or under review")
