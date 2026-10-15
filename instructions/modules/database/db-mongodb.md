## Database — MongoDB

MongoDB {{mongodb_version}}.

- Every collection has a **schema validator** (`$jsonSchema`) mirroring the application model;
  documents that do not validate are rejected, not stored.
- Model around the access patterns: embed what is read together, reference what grows unbounded.
- Every query used in a request path is covered by an index; slow-query logging is on.
- Multi-document changes that must be atomic use transactions; otherwise design for idempotency.
- Dates are stored as BSON dates in UTC.
