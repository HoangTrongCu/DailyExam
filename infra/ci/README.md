# CI/CD Setup

Workflow shipped as `ci.yml.template` because the current PAT lacks `workflow` scope.

To activate:

1. Visit https://github.com/settings/tokens and grant `workflow` scope to your PAT
2. Then:

```bash
mkdir -p .github/workflows
git mv infra/ci/ci.yml.template .github/workflows/ci.yml
git commit -m "Enable CI workflow"
git push
```

Jobs:
- **backend** — Python 3.11, ruff + pytest (≥85% coverage gate)
- **frontend** — Node 20, jest coverage + next build
- **duplication** — jscpd (fails if duplication >2.5%)

Current local metrics:
- Backend coverage: ~91%
- Frontend coverage: ~98%
- Duplication: ~0.2%
