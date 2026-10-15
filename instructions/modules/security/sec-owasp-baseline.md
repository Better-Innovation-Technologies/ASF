## Security — OWASP baseline

- **Validate every input** at the boundary with a schema (type, length, format, range); reject,
  do not sanitize-and-continue.
- **Encode every output** for its context (HTML, SQL via parameters only, shell never with user
  input).
- **Authorization on every request**, server-side, deny by default; check ownership of the resource,
  not only the role.
- Passwords and tokens are never logged; authentication relies on a vetted provider (OIDC), not on
  home-made crypto.
- Dependencies are pinned and scanned (SCA) in CI; a known critical vulnerability blocks the merge.
- SAST runs on every merge request; findings are fixed or justified in the merge request.
- Security headers and TLS everywhere; cookies `Secure`, `HttpOnly`, `SameSite`.
