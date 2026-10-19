# Install the project-card update

1. Open your GitHub profile repository: https://github.com/Collinomics/Collinomics
2. Upload `README.md` **and the entire `assets/projects/` directory** to the repository root. Preserve paths:

```
Collinomics/
├── README.md
├── assets/
│   └── projects/
│       ├── kyu-ai-cris.svg
│       └── my-profile.svg
└── .github/workflows/snake.yml  # leave your existing workflow untouched
```

3. Commit the changes on `main`; refresh https://github.com/Collinomics.
4. To add genuine screenshots later, upload PNG/WebP images to `assets/projects/` and change the matching `<img src="...">` path in `README.md`.
5. Add live demo links only when a deployment exists and you have verified it works.

The SVGs are custom title cards, **not screenshots**. The project source links have been checked. Existing analytics and contribution snake are retained.
