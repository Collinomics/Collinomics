#!/usr/bin/env python3
"""Independent fallback checks for the Collinomics profile-maintenance workflow."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import re
import subprocess
import sys
import os

root = Path.cwd()
readme = root / "README.md"
report_dir = root / "maintenance" / "fallback-reports"
report_dir.mkdir(parents=True, exist_ok=True)
now = datetime.now(ZoneInfo("Africa/Kampala"))
passed, warnings, failures = [], [], []

def ok(message): passed.append(message)
def warn(message): warnings.append(message)
def fail(message): failures.append(message)

if readme.is_file():
    text = readme.read_text(encoding="utf-8", errors="replace")
    ok("README exists and is readable")
else:
    text = ""
    fail("README.md is missing")

for section in ("TECHNOLOGY", "PROJECTS"):
    if section.lower() in text.lower():
        ok(f"README section present: {section}")
    else:
        fail(f"README section missing: {section}")

references = re.findall(r'''(?:src|href)\s*=\s*["']([^"']+)["']''', text, flags=re.I)
references += re.findall(r'''!?\[[^\]]*\]\(([^)]+)\)''', text)
local_targets = set()
for raw in references:
    raw = raw.strip().split()[0].strip("<>") if raw.strip() else ""
    if not raw or raw.startswith(("#", "mailto:", "data:", "javascript:", "http://", "https://")):
        continue
    if raw.startswith("/"):
        continue
    local_targets.add(raw.split("#", 1)[0].split("?", 1)[0])

missing = sorted(path for path in local_targets if path and not (root / path).exists())
if missing:
    for path in missing:
        fail(f"Missing README target: {path}")
else:
    ok(f"All {len(local_targets)} local README targets exist")

workflow_files = sorted((root / ".github" / "workflows").glob("*.yml"))
workflow_files += sorted((root / ".github" / "workflows").glob("*.yaml"))
if workflow_files:
    try:
        result = subprocess.run(
            ["ruby", "-e", "require 'yaml'; ARGV.each { |f| YAML.parse_file(f) }"]
            + [str(path) for path in workflow_files],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            ok(f"YAML parsed for {len(workflow_files)} workflow files")
        else:
            fail("Workflow YAML parse error: " + (result.stderr.strip() or result.stdout.strip()))
    except (OSError, subprocess.TimeoutExpired) as error:
        warn(f"YAML validation could not run: {error}")
else:
    fail("No workflow files found")

snake_path = root / ".github" / "workflows" / "snake.yml"
if snake_path.is_file():
    snake = snake_path.read_text(encoding="utf-8", errors="replace")
    if "Collinomics" in snake and "target_branch: output" in snake:
        ok("Contribution Snake configuration is present")
    else:
        fail("Contribution Snake configuration is missing or incorrect")
else:
    fail("Contribution Snake workflow is missing")

status = "FAIL" if failures else ("PASS WITH WARNINGS" if warnings else "PASS")
report = [
    "# Fallback Maintenance Report",
    "",
    f"- Run time: {now.strftime('%Y-%m-%d %H:%M %Z')}",
    f"- Status: {status}",
    "- This independent fallback checks local files and workflow syntax; it does not perform external URL checks.",
    "",
    "## Passed",
] + ([f"- {item}" for item in passed] or ["- None"]) + [
    "", "## Warnings",
] + ([f"- {item}" for item in warnings] or ["- None"]) + [
    "", "## Failures",
] + ([f"- {item}" for item in failures] or ["- None"]) + [
    "", "## Achievement guidance",
    "- Pull Shark: merge useful pull requests that solve real problems.",
    "- Pair Extraordinaire: collaborate on a genuinely co-authored merged pull request.",
    "- Galaxy Brain: provide helpful answers in GitHub Discussions.",
    "- Starstruck: build projects people choose to star.",
    "- Automation does not guarantee achievements or count as personal contributions.",
]
output = "\n".join(report) + "\n"
(report_dir / f"{now.strftime('%Y-%m-%d')}.md").write_text(output, encoding="utf-8")
(root / "maintenance" / "fallback_latest.md").write_text(output, encoding="utf-8")
summary = Path(os.environ.get("GITHUB_STEP_SUMMARY", "/tmp/fallback-summary.md"))
summary.parent.mkdir(parents=True, exist_ok=True)
summary.write_text(output, encoding="utf-8")
print(output)
if failures:
    sys.exit(1)
