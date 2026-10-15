## System topology — serverless

The system is made of **functions and managed services** (queues, object storage, managed
databases) on {{cloud_provider}}.

- One function, one responsibility, one trigger. Handlers are thin: they parse the event and call
  domain code that is testable without the cloud runtime.
- Functions are **stateless and idempotent**: any invocation can be retried by the platform.
- Configuration and secrets come from the platform's configuration/secret services, never from the
  package.
- Cold start and timeout limits are design constraints: long work goes through a queue, not a
  longer timeout.
- Infrastructure is code (the IaC tool of the project), reviewed like application code.
