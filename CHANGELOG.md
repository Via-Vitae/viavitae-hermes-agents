# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/);
this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Security hardening
- Reject blank values for all seven boundary controls.
- Detect unequal audit event/hash lengths and refuse further appends with AuditTamperError.


### Added
- Initial repository scaffold (Python 3.12, uv-managed venv, ruff/mypy/pytest/bandit,
  gitleaks CI + pre-commit compensating controls).
