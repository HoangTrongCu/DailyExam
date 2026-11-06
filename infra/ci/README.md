# CI/CD Setup

The GitHub Actions workflow is provided as `ci.yml.template` in this folder.

## Why not already at `.github/workflows/ci.yml`?

GitHub blocks pushing workflow files when the Personal Access Token (PAT) lacks the `workflow` scope. The initial commit was created via a PAT without that scope, so the workflow is shipped as a template.

## How to activate

Option A — Update your PAT:
1. Go to https://github.com/settings/tokens
2. Edit the token you use for this repo, check the `workflow` scope, save
3. Then run:

```bash
mkdir -p .github/workflows
git mv infra/ci/ci.yml.template .github/workflows/ci.yml
git commit -m "Enable CI workflow"
git push
```

Option B — Add the workflow via GitHub web UI:
1. On GitHub, go to `Actions` → `New workflow` → `set up a workflow yourself`
2. Paste the contents of `ci.yml.template`
3. Commit directly via the web UI

## What the workflow does

- **Backend job**: Python 3.11, installs backend package, runs `ruff` + `pytest` with `>=85%` coverage gate
- **Frontend job**: Node 20, installs web package, runs `jest` with `>=85%` coverage gate, then `next build`
- **Duplication job**: installs `jscpd` and fails if duplication exceeds `2.5%`

Current local metrics:
- Backend coverage: **100%**
- Frontend coverage: **100%**
- Duplication: **0%**
