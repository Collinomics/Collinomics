#!/usr/bin/env python3
"""Daily profile maintenance checks and report generation."""
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import re, subprocess, sys, os
import xml.etree.ElementTree as ET

root=Path.cwd(); readme=root/"README.md"; report_dir=root/"maintenance/reports"
report_dir.mkdir(parents=True,exist_ok=True)
date=datetime.now(timezone.utc).strftime("%Y-%m-%d")
stamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
passed=[]; warnings=[]; failures=[]

def check(msg): passed.append(msg)
def warn(msg): warnings.append(msg)
def fail(msg): failures.append(msg)
def status(url):
    for method in ("HEAD","GET"):
        try:
            req=Request(url,method=method,headers={"User-Agent":"Collinomics-Maintenance/1.0"})
            with urlopen(req,timeout=6) as r: return r.status
        except HTTPError as e:
            if method=="HEAD" and e.code in (403,405,501): continue
            return e.code
        except (URLError,TimeoutError,OSError):
            if method=="HEAD": continue
            return None
    return None

if readme.is_file():
    text=readme.read_text(encoding="utf-8",errors="replace"); check("README exists and is readable")
else:
    text=""; fail("README.md is missing")
for section in ("TECHNOLOGY","PROJECTS"):
    if section.lower() in text.lower(): check(f"README section present: {section}")
    else: fail(f"README section missing: {section}")

refs=re.findall(r'''(?:src|href)\s*=\s*["']([^"']+)["']''',text,flags=re.I)
refs+=re.findall(r'''!?\[[^\]]*\]\(([^)]+)\)''',text)
local=set(); external=set()
for raw in refs:
    raw=raw.strip().split()[0].strip("<>") if raw.strip() else ""
    if not raw or raw.startswith(("#","mailto:","data:","javascript:")): continue
    if raw.startswith(("http://","https://")): external.add(raw); continue
    if raw.startswith("/"): continue
    local.add(raw.split("#",1)[0].split("?",1)[0])
missing=[p for p in sorted(local) if p and not (root/p).exists()]
if missing:
    for p in missing: fail(f"Missing local README target: {p}")
else: check(f"All {len(local)} local README targets exist")
svg_errors=[]; svg_count=0
for p in sorted(local):
    if p.lower().endswith(".svg") and (root/p).is_file():
        try: ET.parse(root/p); svg_count+=1
        except ET.ParseError as e: svg_errors.append(f"{p}: {e}")
if svg_errors:
    for e in svg_errors: fail("Invalid SVG: "+e)
else: check(f"{svg_count} local SVG file(s) parse correctly")

hrefs=re.findall(r'''<a\b[^>]*\bhref\s*=\s*["']([^"']+)["']''',text,flags=re.I)
image_srcs=re.findall(r'''<img\b[^>]*\bsrc\s*=\s*["']([^"']+)["']''',text,flags=re.I)
md_links=re.findall(r'''(?<!\!)\[[^\]]+\]\((https?://[^)]+)\)''',text)
md_images=re.findall(r'''!\[[^\]]*\]\((https?://[^)]+)\)''',text)
urls=sorted(set(u.strip().rstrip(".,") for u in hrefs+md_links+image_srcs+md_images if u.startswith(("http://","https://"))))
if len(urls)>20: warn(f"External link checks limited to 20 of {len(urls)} links")
for u in urls[:20]:
    code=status(u)
    if code is None: warn(f"External URL timed out: {u}")
    elif code>=400: warn(f"External URL returned HTTP {code}: {u}")
    else: check(f"External link OK ({code}): {u}")

wf = sorted((root / ".github" / "workflows").glob("*.yml")) + sorted((root / ".github" / "workflows").glob("*.yaml"))
dependabot=root/".github/dependabot.yml"
if wf:
    cmd=["ruby","-e","require 'yaml'; ARGV.each { |f| YAML.parse_file(f) }"]+[str(p) for p in wf]
    if dependabot.is_file():
        cmd.append(str(dependabot))
        check("Dependabot configuration exists")
    else:
        warn("Dependabot configuration is missing")
    res=subprocess.run(cmd,capture_output=True,text=True)
    if res.returncode==0: check(f"YAML parsed for {len(wf)} workflow file(s) and Dependabot")
    else: fail("Workflow/Dependabot YAML parse error: "+(res.stderr.strip() or res.stdout.strip()))
else: fail("No workflow files found")
snake=root/".github/workflows/snake.yml"
if snake.is_file() and "Collinomics" in snake.read_text(errors="replace") and "target_branch: output" in snake.read_text(errors="replace"):
    check("Contribution Snake configuration points to the output branch")
else: fail("Contribution Snake workflow missing or misconfigured")
for file in ("github-contribution-grid-snake.svg","github-contribution-grid-snake-dark.svg"):
    url=f"https://raw.githubusercontent.com/Collinomics/Collinomics/output/{file}"
    code=status(url)
    if code is not None and code<400: check(f"Snake file published: {file}")
    else: warn(f"Snake output not currently reachable: {file}")

state="FAIL" if failures else ("PASS WITH WARNINGS" if warnings else "PASS")
lines=["# Daily Portfolio Maintenance Report","",f"- Run time: {stamp}",f"- Status: {state}",f"- External links checked: {min(len(urls),20)} of {len(urls)}","","## Passed"]
lines += [f"- {v}" for v in passed] or ["- None"]
lines += ["","## Warnings"] + ([f"- {v}" for v in warnings] or ["- None"])
lines += ["","## Failures"] + ([f"- {v}" for v in failures] or ["- None"])
lines += ["","## Genuine achievement focus","- Pull Shark: merge useful pull requests.","- Pair Extraordinaire: work with a collaborator on a genuinely co-authored merged PR.","- Galaxy Brain: contribute helpful answers in GitHub Discussions.","- Starstruck: build useful projects people choose to star.","These are reminders, not automatic badge checks or guarantees.","","## Automation note","This report and its commits are generated by GitHub Actions. They are transparent repository maintenance records, not manually authored contributions."]
report="\n".join(lines)+"\n"
(report_dir:=report_dir).mkdir(parents=True,exist_ok=True)
(report_dir/f"{date}.md").write_text(report,encoding="utf-8")
(root/"maintenance/latest.md").write_text(report,encoding="utf-8")
summary=Path(os.environ.get("GITHUB_STEP_SUMMARY","/tmp/summary.md")); summary.parent.mkdir(parents=True,exist_ok=True); summary.write_text(report,encoding="utf-8")
print(report)
if failures: sys.exit(1)
