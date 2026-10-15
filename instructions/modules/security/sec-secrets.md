## Security — secrets

- **No secret in git**, ever — not in code, not in `.env` committed, not in test fixtures. Secret
  scanning runs on pre-commit and in CI; a leaked secret is rotated, not just deleted.
- Secrets come from the platform's secret store (vault, Kubernetes secrets, CI variables), injected
  at runtime; different secrets per environment; least privilege.
- Never print the environment or a config object; loggers use an allowlist of fields.
- CI authenticates to clouds with short-lived credentials (OIDC federation) instead of long-lived
  keys.
