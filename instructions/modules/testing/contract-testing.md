## Testing — contract tests between services

- Every service-to-service interaction has a **consumer-driven contract** (Pact or equivalent): the
  consumer states what it needs, the provider verifies it in its own pipeline.
- A provider cannot be deployed if it breaks a published consumer contract.
- Contracts check the **shape** of messages; integration tests still check behaviour.
- Event schemas (AsyncAPI) and protobuf files are checked for backward compatibility in CI.
