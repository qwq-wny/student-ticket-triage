# Deployment notes

Branches:

```text
feature/* -> dev -> staging -> main
```

CI runs on every PR to `dev`, `staging`, and `main`:

1. Ruff format check
2. Ruff static analysis
3. Pytest
4. Docker image build

CD runs after merge:

- `staging`: writes `.env` from `STAGING_SECRET`, then builds `ticket-triage:staging`
- `main`: writes `.env` from `PRODUCTION_SECRET`, then builds `ticket-triage:production`

The workflow saves each image as an artifact but does not deploy it.

Required GitHub settings:

- environments: `staging` and `production`
- secrets: `STAGING_SECRET` and `PRODUCTION_SECRET`
- branch protection on `dev`, `staging`, and `main`
- require the CI check before merging
