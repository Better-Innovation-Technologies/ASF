## System topology — monolith

The system is **one deployable application**. That is a deliberate choice: one build, one
deployment, one database, in-process calls, transactions that just work.

- Keep it **modular inside**: one folder per business capability, with its own models, services and
  tests; a module never reads another module's tables directly — it calls the other module's public
  functions.
- No network calls between parts of the same application.
- Split something out only with a measured reason (independent scaling, a different release
  cadence, a team boundary), recorded as an ADR.
