# CSTDL lab website (Scholar-Lite)

Papers are NOT edited here. They come from the CSTDL Google Sheet
(Paper progress -> Web tab) every time the site builds.

Edit directly in this repository:
- src/config.ts                 lab name, hero text, menu, contact
- src/content/team/*.md         one file per person; photo in src/assets/team/
- src/content/research/*.md     research areas
- src/content/news/*.md         news items
- src/pages/join.astro          openings
- src/styles/global.css         SNU colors and font

Automatic:
- scripts/sheet_to_site.py      sheet -> src/content/publications/ (do not edit those files)
- .github/workflows/deploy.yml  builds on every push to main, daily at 03:00 KST,
                                and via Actions > Build and Deploy > Run workflow

Repository secret required: SHEET_CSV_URL (published CSV link of the Web tab).
Settings > Pages > Source must be "GitHub Actions".
