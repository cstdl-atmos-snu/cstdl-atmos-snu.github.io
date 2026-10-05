# CSTDL lab website (jin-phd template + sheet sync)

Files in this folder overwrite or add to the template. Papers are NOT edited
here: they come from the CSTDL Google Sheet (Paper progress -> Web tab).

- scripts/sheet_to_bib.py   Web tab (CSV) -> assets/ref.bib
- .github/workflows/deploy.yml   runs the script, then builds and deploys;
  on every push to `source`, daily at 03:00 KST, and via "Run workflow"
- _data/team_members.yml, pi.yml, grants.yml   people, PI bio, grants
- _pages/home.md, research.md, team.md, about.md, publications.md
- images/team/*.svg   placeholder initials; replace with photos when available

Repository secret required: SHEET_CSV_URL (published CSV link of the Web tab).
