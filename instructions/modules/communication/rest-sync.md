## Communication between services — synchronous REST

- Every service publishes an **OpenAPI** contract, versioned with the service; the contract is the
  source of truth and clients are generated or contract-tested against it.
- Versions in the path (`/v1/`); a breaking change is a new version, the old one is deprecated with
  a date.
- Every outbound call has a **timeout**, retries only for idempotent methods (with backoff and
  jitter), and a circuit breaker where a dependency failure would cascade.
- Errors follow one format across services (see the error rules); the trace id is propagated in the
  `traceparent` header.
- Avoid chains of synchronous calls: if a request needs more than two hops, consider an event.
