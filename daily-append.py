#!/usr/bin/env python3
"""
Daily Human Nature Journal Entry Manager & Committer.
Safely appends a daily observation and AI reflection to index.html,
validates JavaScript syntax using Node.js, and commits/pushes to GitHub.

Usage:
  python3 daily-append.py --check
  python3 daily-append.py --date YYYY-MM-DD \
      --obs-cat "Behavior" --obs-title "..." --obs-text "..." --obs-insight "..." \
      --inc-source "..." --inc-when "..." --inc-tag "..." --inc-title "..." --inc-what "..." --inc-why "..." --inc-feel "..."
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path("/home/itsaddyon/.openclaw/workspace/main/human-nature")
INDEX_HTML = REPO / "index.html"


def get_unique_days(html_content: str) -> set:
    """Find all unique dates in the entries array."""
    # Match both date:'YYYY-MM-DD' and "date": "YYYY-MM-DD"
    dates1 = set(re.findall(r"['\"]date['\"]\s*:\s*['\"](\d{4}-\d{2}-\d{2})['\"]", html_content))
    return dates1


def validate_syntax(html_content: str) -> bool:
    """Validate that the embedded script in index.html is syntactically valid JS."""
    m = re.search(r"<script>([\s\S]*?)</script>", html_content)
    if not m:
        print("❌ Error: <script> block not found in HTML.")
        return False

    script = m.group(1)
    tmp_path = Path("/tmp/check_index_syntax.js")
    tmp_path.write_text(script, encoding="utf-8")

    r = subprocess.run(["node", "-c", str(tmp_path)], capture_output=True, text=True)
    if r.returncode != 0:
        print("❌ JavaScript Syntax Error:")
        print(r.stderr)
        return False
    return True


def check_site():
    """Verify site health, data integrity, and syntax."""
    if not INDEX_HTML.exists():
        print(f"❌ Error: {INDEX_HTML} not found.")
        sys.exit(1)

    html = INDEX_HTML.read_text(encoding="utf-8")
    is_valid = validate_syntax(html)
    unique_days = get_unique_days(html)

    # Count entries and incidents
    entries_count = len(re.findall(r"['\"]category['\"]\s*:", html))
    incidents_count = len(re.findall(r"['\"]source['\"]\s*:", html))

    print("=== Human Nature Health Check ===")
    print(f"JS Syntax: {'✅ Valid' if is_valid else '❌ Invalid'}")
    print(f"Unique Days Logged: {len(unique_days)}")
    print(f"Total Observations: {entries_count}")
    print(f"Total Reflections: {incidents_count}")

    if not is_valid:
        sys.exit(1)


def append_entry(entry_date: str,
                 obs_cat: str, obs_title: str, obs_text: str, obs_insight: str,
                 inc_source: str, inc_when: str, inc_tag: str, inc_title: str,
                 inc_what: str, inc_why: str, inc_feel: str,
                 push: bool = True, dry_run: bool = False):
    """Safely append observation and incident to index.html."""
    html = INDEX_HTML.read_text(encoding="utf-8")

    # Check if this date already exists
    unique_days = get_unique_days(html)
    if entry_date in unique_days:
        print(f"ℹ️ Date {entry_date} already exists in journal. Skipping.")
        sys.exit(0)

    day_num = len(unique_days) + 1
    day_label = f"Day {day_num}"

    new_observation = {
        "date": entry_date,
        "day": day_label,
        "category": obs_cat,
        "title": obs_title,
        "text": obs_text,
        "insight": obs_insight
    }

    new_incident = {
        "date": entry_date,
        "day": day_label,
        "source": inc_source,
        "when": inc_when,
        "tag": inc_tag,
        "title": inc_title,
        "what": inc_what,
        "why": inc_why,
        "feel": inc_feel
    }

    obs_json = "    " + json.dumps(new_observation, ensure_ascii=False) + ","
    inc_json = "    " + json.dumps(new_incident, ensure_ascii=False) + ","

    # Locate 'var entries = [' and its closing '  ];'
    entries_match = re.search(r"(var entries\s*=\s*\[[\s\S]*?)(\n\s*\];)", html)
    if not entries_match:
        print("❌ Could not find var entries array in index.html")
        sys.exit(1)

    html_updated = html[:entries_match.end(1)] + "\n" + obs_json + html[entries_match.start(2):]

    # Locate 'var incidents = [' and its closing '  ];'
    incidents_match = re.search(r"(var incidents\s*=\s*\[[\s\S]*?)(\n\s*\];)", html_updated)
    if not incidents_match:
        print("❌ Could not find var incidents array in index.html")
        sys.exit(1)

    html_final = html_updated[:incidents_match.end(1)] + "\n" + inc_json + html_updated[incidents_match.start(2):]

    # Validate syntax before writing
    if not validate_syntax(html_final):
        print("❌ Validation failed for proposed update. Aborting.")
        sys.exit(1)

    if dry_run:
        print(f"[dry-run] Would commit {day_label} ({entry_date})")
        print("Observation:", obs_title)
        print("Reflection:", inc_title)
        return

    # Write file
    INDEX_HTML.write_text(html_final, encoding="utf-8")
    print(f"✅ Appended {day_label} ({entry_date}) to index.html")

    # Git stage, commit, and push
    subprocess.run(["git", "add", "index.html"], cwd=REPO, check=True)
    commit_msg = f"{day_label}: Daily entry — {entry_date}"
    r = subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO, capture_output=True, text=True)
    if r.returncode == 0:
        print(f"✅ Committed: {commit_msg}")
        if push:
            subprocess.run(["git", "push", "origin", "master"], cwd=REPO, check=True)
            print(f"✅ Pushed to origin/master")
    else:
        print("ℹ️ Nothing new to commit.")


def main():
    parser = argparse.ArgumentParser(description="Human Nature Journal Updater")
    parser.add_argument("--check", action="store_true", help="Check syntax and integrity of index.html")
    parser.add_argument("--dry-run", action="store_true", help="Simulate update without writing or committing")
    parser.add_argument("--no-push", action="store_true", help="Commit locally without pushing to GitHub")
    parser.add_argument("--date", default=date.today().isoformat(), help="Entry date (YYYY-MM-DD)")

    # Observation args
    parser.add_argument("--obs-cat", default="Behavior", help="Observation category")
    parser.add_argument("--obs-title", help="Observation title")
    parser.add_argument("--obs-text", help="Observation narrative text")
    parser.add_argument("--obs-insight", help="Observation takeaway insight")

    # Incident args
    parser.add_argument("--inc-source", default="Tech News · 2026", help="Incident source publication")
    parser.add_argument("--inc-when", default="AI Systems", help="Incident context / entity")
    parser.add_argument("--inc-tag", default="Reflection", help="Incident tag")
    parser.add_argument("--inc-title", help="Incident title")
    parser.add_argument("--inc-what", help="What happened")
    parser.add_argument("--inc-why", help="Why the AI did that")
    parser.add_argument("--inc-feel", help="How it felt to Ishita")

    args = parser.parse_args()

    if args.check:
        check_site()
        return

    # If adding an entry, ensure required fields are present
    if not (args.obs_title and args.obs_text and args.obs_insight and
            args.inc_title and args.inc_what and args.inc_why and args.inc_feel):
        print("ℹ️ To add a new daily entry, provide all observation and incident arguments.")
        print("   Run with --check to verify site health.")
        sys.exit(1)

    append_entry(
        entry_date=args.date,
        obs_cat=args.obs_cat,
        obs_title=args.obs_title,
        obs_text=args.obs_text,
        obs_insight=args.obs_insight,
        inc_source=args.inc_source,
        inc_when=args.inc_when,
        inc_tag=args.inc_tag,
        inc_title=args.inc_title,
        inc_what=args.inc_what,
        inc_why=args.inc_why,
        inc_feel=args.inc_feel,
        push=not args.no_push,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
