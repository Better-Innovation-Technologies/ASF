## Errors — cause, context, action

Every error that can reach a person (a user, an operator, a developer reading a log) says three
things:

```
<cause> | context: <where, on what> | action: <what to do now>
```

- **Fail fast**: no empty `catch`, no `except: pass`, no silent fallback. Catch only what you can
  handle; log and re-raise the rest.
- Domain errors are typed (one class per failure the caller can act on), never a bare string.
- HTTP APIs return a JSON body with `error`, `next` (the action) and a stable machine-readable
  `reason`; the status code matches the failure (400 input, 403 permission, 404 missing, 409
  conflict, 422 rule violated, 5xx ours).
- The trace id is in every error response, so that a person can quote it.
