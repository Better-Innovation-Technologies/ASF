## System topology — modular monolith

The system is **one deployable application made of modules with enforced boundaries** under
`{{modules_root}}`. It keeps the simplicity of one deployment while preparing the seams along which a
service could be extracted later — the recommended starting point for a new product
("monolith first").

- One module per business capability. A module exposes a **public interface** (a package entry
  point / an `index` file) and everything else is internal.
- A module **never imports another module's internals** and **never reads another module's tables**;
  it calls the public interface. The rule is enforced by a lint or architecture test, not by review.
- Each module owns its data: its own schema (or table prefix) in the shared database.
- Cross-module side effects go through in-process domain events when the caller must not wait or
  must not know who reacts.
- A module's public interface is treated as a contract: changing it breaks the build of its callers,
  on purpose.
