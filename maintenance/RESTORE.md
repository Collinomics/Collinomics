# Collinomics automation recovery

## Active automation
- Daily Portfolio Maintenance: checks README structure, local assets, external links, workflow YAML, Dependabot configuration, and Contribution Snake output.
- Maintenance Fallback: runs later each day if the primary daily run did not succeed. It uses a separate, simpler script and avoids external-link checks.
- Maintenance Watchdog: checks daily maintenance, fallback, daily automation backup, and weekly repository backup freshness; it opens an issue if something is unhealthy.
- Daily Automation Backup: copies current and dated workflow/script snapshots to the automation-backup branch.
- Weekly Repository Backup: stores a compressed repository snapshot on the backup branch and in a GitHub Actions artifact retained for 90 days.
- Dependabot: checks GitHub Actions dependencies weekly and can open update pull requests.

## Restore a workflow or script
1. Open the automation-backup branch.
2. Find the file under automation/workflows/current or automation/scripts/current, or use a dated snapshot.
3. Copy it to the original path on main.
4. Review it before committing.

## Restore a repository snapshot
1. Download the newest collinomics-profile-YYYY-MM-DD.tar.gz from automation/repository-snapshots on the backup branch or from the weekly Actions artifact.
2. Extract it to a temporary folder.
3. Compare the files with the live repository.
4. Restore only what is needed.

## Limits
These backups are stored in the same GitHub repository. They help recover from accidental file changes or deletions, but cannot protect against repository deletion, account compromise, or a GitHub-wide outage. A separate private repository or off-platform copy is needed for independent disaster recovery.
