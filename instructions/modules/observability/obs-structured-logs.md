## Logging and observability

`console.log`, `print()` and their equivalents are **forbidden in production code**. Use the
project's structured logger.

Every log entry is **structured** (JSON) and carries:
- **`trace_id`** (`traceId` in TypeScript) — bound to the request or workflow, propagated to every
  call it makes;
- **`sub`** (optional) — the user's subject, for operations triggered by a user;
- an event name and the identifiers of the entities involved — never secrets or personal data.

```typescript
logger.info({ traceId: req.id, sub: req.user?.sub, entityId }, 'entity created');
```

```python
logger.info("entity created", trace_id=trace_id, sub=sub, entity_id=entity_id)
```

`console.log` / `print` are acceptable only in seed scripts, one-off CLI utilities and tests.
