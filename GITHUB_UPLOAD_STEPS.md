# GitHub upload steps

Extract the ZIP into your existing repository root so the `docs/` directory sits alongside `app.py` and your Dockerfiles.

In PowerShell:

```powershell
git status --short
git check-ignore -v .env .streamlit/secrets.toml
git add docs
git status --short
git diff --cached --stat
git diff --cached
git commit -m "docs: add system and deployment architecture"
git push origin main
```

If your branch is not `main`, check it with `git branch --show-current` and push that branch instead.

To upload all other uncommitted source changes, inspect `git status` first and stage only intended source files. Do not blindly use `git add .`. Ensure `.env`, `.streamlit/secrets.toml`, credentials, private keys, local environments, personal data and unintended large model/data files are excluded. If a secret was ever committed, rotate it; a later deletion alone is not enough.

Add this to the root README:

```markdown
## Architecture & Design

See [`docs/`](docs/README.md) for:
- [System Architecture](docs/system-architecture.md)
- [Low-Level System Design](docs/low-level-system-design.md)
- [ELT Pipeline Architecture](docs/elt-pipeline-architecture.md)
- [Data Architecture](docs/data-architecture.md)
- [Deployment Architecture](docs/deployment-architecture.md)
```

Review every document against the current code before publishing. The 150-user design is a target until validated by load testing.
