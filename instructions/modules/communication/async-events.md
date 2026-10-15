## Communication between services — asynchronous events

- Events are **facts in the past tense** (`OrderPlaced`), owned by the service that emits them,
  described in an **AsyncAPI** document and versioned; consumers tolerate unknown fields.
- Publish with the **transactional outbox**: the business change and the outgoing event are written
  in the same database transaction; a relay publishes them. Never "write then publish" in two steps.
- Delivery is **at least once**: every consumer is **idempotent**, deduplicating on the event id
  (an inbox table or an equivalent atomic store).
- An event carries its id, type, version, occurrence time, the producer and the trace id.
- Poison messages go to a dead-letter queue with an alert; they are never dropped silently.
- Long business processes across services are sagas with explicit compensations, not distributed
  transactions.
