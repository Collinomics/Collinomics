# Collinomics V3 — setup

This version replaces the previous README. It is intentionally shorter, avoids unreliable third-party stat cards, and uses locally stored graphics.

## Upload

1. Open https://github.com/Collinomics/Collinomics
2. Upload **README.md** to the repository root, replacing the existing version.
3. Upload the **assets** folder and its three SVG files to the repository root. The paths must be `assets/hero.svg`, `assets/project-kyu.svg`, and `assets/project-profile.svg`.
4. Keep the existing `.github/workflows/snake.yml` file and the `output` branch. Do not replace or delete them.
5. Commit to `main`, then visit https://github.com/Collinomics and hard refresh.

**Important:** GitHub renders the README with limited HTML/CSS capabilities. The animated hero is native SVG. There is no custom JavaScript or fake interactivity. The project visuals are illustrations, not real screenshots. No unverified live demo URLs are included.

If the snake fails, check that the `output` branch has `github-contribution-grid-snake.svg`. The link in README assumes that exact filename. Existing snake workflow may use a different filename; adjust it if necessary.

## Improve the real projects

- Add safe public screenshots to the projects' own repositories and swap the SVG cards for screenshots later.
- Add a useful README, installation instructions, and example screenshots to `kyu-ai-cris`.
- Review any demo credentials or secrets before sharing the repo or deploying publicly.
- Pin `kyu-ai-cris` and `My-profile` on your GitHub profile.
