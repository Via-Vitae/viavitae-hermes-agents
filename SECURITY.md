# Security

## Reporting a vulnerability

Do **not** open a public issue. Report security vulnerabilities privately to
the Via-Vitae security team (see organisation `SECURITY.md` / GitHub private
vulnerability reporting).

## Controls

- Secret scanning + push protection enabled (public repo, GitHub Free).
- `gitleaks` runs in CI as a license-free compensating control.
- Secrets are provided via the environment (`.env` locally, GitHub Actions
  secrets in CI). **Never** commit real credentials; `.env` is git-ignored.
