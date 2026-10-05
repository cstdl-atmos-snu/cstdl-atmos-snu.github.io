# Convective Systems/Tropical Dynamics Lab website

Static site served by GitHub Pages. `publications.html` is generated from the
**Web** tab of the CSTDL Google Sheet; edit papers in the sheet, not here.

- `index.html`, `group.html`: edit directly.
- `scripts/publications_template.html`: layout of the publications page.
- `scripts/build_publications.py`: reads the Web tab (CSV) and writes `publications.html`.
- `.github/workflows/update-publications.yml`: runs the build every day at 03:00 KST
  and on demand (Actions tab, "Run workflow").

Local preview: `python scripts/build_publications.py path/to/web.csv`
