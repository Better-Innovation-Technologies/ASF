## Logging and observability — OpenTelemetry

- Traces, metrics and logs are emitted through **OpenTelemetry** SDKs and exported over OTLP.
- Context propagation uses W3C `traceparent` across HTTP, gRPC and messages; every log line carries
  `trace_id` and `span_id` from the active span.
- Logs are structured (JSON); field names are consistent across services (`service.name`,
  `trace_id`, `span_id`, event name, entity ids).
- Each service exposes the RED metrics (rate, errors, duration) for its endpoints and consumers.
- Log sampling follows trace sampling; errors are always logged.
- No secrets or personal data in attributes, logs or span names.
