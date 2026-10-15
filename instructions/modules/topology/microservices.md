## System topology — microservices

The system is a set of **independently deployable services** under `{{services_root}}`, each owning
one business capability.

- **One service, one database.** No service reads or writes another service's data store; data
  is shared through APIs or events only.
- Every service has an **owner**, its own pipeline and its own versioned API contract. A breaking
  change to a contract is a new version, never an in-place change.
- Calls between services cross the network: they have timeouts, retries with backoff only on
  idempotent operations, and a defined behaviour when the other side is down.
- A request carries **one trace id across every service** (see the observability rules).
- No distributed transaction: consistency across services is eventual, through events or sagas,
  and every consumer is idempotent.
- Do not split further without a reason recorded as an ADR: every service is a deployment, a
  contract and an on-call surface.
