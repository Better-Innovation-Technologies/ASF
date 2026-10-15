## Communication between services — gRPC

- Contracts are `.proto` files in one shared, versioned location; code is generated, never written
  by hand.
- **Backward compatibility**: only add fields and methods; never rename, renumber or change the type
  of a field; mark removed fields `reserved`. A breaking change is a new package version
  (`acme.orders.v2`).
- Every call has a **deadline**; retries only for idempotent methods.
- Errors use the gRPC status codes with a rich error detail; the trace id travels in metadata.
- Use gRPC between services; expose REST/JSON at the edge for browsers and third parties.
