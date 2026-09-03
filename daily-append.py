#!/usr/bin/env python3
"""Appends a daily placeholder entry+incident to index.html, commits and pushes.
Usage: daily-append.py [--dry-run]"""
import subprocess, sys, re
from pathlib import Path
from datetime import date

REPO = Path("/home/itsaddyon/.openclaw/workspace/main/human-nature")
HTML = REPO / "index.html"
TODAY = date.today().isoformat()
DRY_RUN = "--dry-run" in sys.argv

if DRY_RUN:
    print(f"[dry-run] today={TODAY}")

html = HTML.read_text(encoding="utf-8")

if f"'{TODAY}'" in html:
    print(f"skip: {TODAY} already present")
    sys.exit(0)

# Count only entries (inside var entries=[]), not incidents
m = re.search(r"var entries=\[([\s\S]*?)\n  \];", html)
entries_text = m.group(1) if m else ""
entries_count = len(re.findall(r"date:'20", entries_text))
day_num = entries_count + 1

if DRY_RUN:
    print(f"[dry-run] would add Day {day_num} ({TODAY})")
    sys.exit(0)

new_e = "{date:'" + TODAY + "',day:'Day " + str(day_num) + "',category:'Daily',title:'[Ishita to fill in]',text:'Ishita will write this observation at her next session.',insight:'[pending]'}"
new_i = "{date:'" + TODAY + "',day:'Day " + str(day_num) + "',source:'Daily',when:'AI',tag:'Reflection',title:'[Ishita to fill in]',what:'Ishita will write this reflection at her next session.',why:'[pending]',feel:'[pending]'}"

lines = html.splitlines(keepends=True)
out = []
i = 0
while i < len(lines):
    if "var entries=[" in lines[i]:
        out.append(lines[i])
        i += 1
        while i < len(lines) and "  ];" not in lines[i]:
            out.append(lines[i])
            i += 1
        if i < len(lines):
            out.append(new_e + ",\n")
            out.append(lines[i])
    elif "var incidents=[" in lines[i]:
        out.append(lines[i])
        i += 1
        while i < len(lines) and "  ];" not in lines[i]:
            out.append(lines[i])
            i += 1
        if i < len(lines):
            out.append(new_i + ",\n")
            out.append(lines[i])
    else:
        out.append(lines[i])
    i += 1

HTML.write_text("".join(out), encoding="utf-8")
print(f"done: Day {day_num} ({TODAY})")

subprocess.run(["git", "add", "index.html"], cwd=REPO, check=True)
r = subprocess.run(
    ["git", "commit", "-m", f"Day {day_num}: Daily entry — {TODAY}"],
    cwd=REPO, capture_output=True, text=True
)
if r.returncode == 0:
    subprocess.run(["git", "push", "origin", "master"], cwd=REPO, check=True)
    print(f"pushed: Day {day_num} — {TODAY}")
else:
    print("nothing to commit")
