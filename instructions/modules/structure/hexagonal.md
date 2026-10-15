## Internal structure — hexagonal (ports and adapters)

The **domain is the centre and depends on nothing**: no framework, no ORM, no HTTP, no SDK.

```
<module>/
├── domain/          # entities, value objects, domain services, domain errors — pure code
├── application/     # use cases; they define the PORTS they need (interfaces)
├── ports/           # (optional) port interfaces when shared by several use cases
└── adapters/
    ├── inbound/     # driving adapters: HTTP handlers, consumers, CLI — call use cases
    └── outbound/    # driven adapters: repositories, API clients, message publishers — implement ports
```

- Dependencies point **inwards only**: adapters → application → domain. The domain imports nothing
  from the outer rings; this is checked by an architecture test.
- **Inbound (driving) ports** are the use cases; **outbound (driven) ports** are interfaces the
  application declares and adapters implement (`OrderRepository`, `PaymentGateway`).
- Wiring (which adapter implements which port) happens in one composition root at startup.
- Domain and use cases are tested **without** infrastructure, with in-memory adapters; adapters
  are tested against the real thing (database, broker) in integration tests.
- Do not create a port for something that has exactly one implementation and no test need: the
  hexagon is about isolating the domain, not about interfaces for their own sake.
