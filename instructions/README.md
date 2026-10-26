# ASF instructions catalog

`instructions.md` is no longer written by hand from a template with `{fe_framework}`-style holes.
It is **composed** from this catalog: one module per choice, grouped by category, plus a final
**Project rules** section that belongs to the project and is never recomposed.

```
instructions/
├── catalog.json          # the index: categories, modules, requires/excludes, placeholders, defaults
├── header.md             # the top of every composed file
├── project-rules.md      # the initial Project rules section
└── modules/<category>/<module>.md
```

The contract is written in the PICO repository (`bit-farm-public/pico`):
`schema/pico-instructions-catalog.schema.json` (this index), `schema/pico-instructions.schema.json`
(what the `pico-instructions` agent answers) and `schema/pico-instructions-manifest.schema.json`
(`.asf/instructions.json`, written in the project next to the composed file).

## How a file is composed

1. The host (KStudio) downloads this catalog at a tagged ref — never during a conversation turn.
2. `pico-instructions` asks the person **few, targeted questions** — only where the project does
   not already answer them — always with a default, then picks **one module per `one` category**
   and any number in a `many` category, and fills the placeholders. It never writes instruction
   text and never invents a module.
3. The host checks cardinality, `requires` (every inner list is *any of*, all lists must hold) and
   `excludes`, and sends violations back to the agent.
4. The host writes, in category order: `header.md`, every chosen module between
   `<!-- asf:module id=… version=… -->` and `<!-- /asf:module -->` markers, then
   `<!-- asf:project-rules -->` and Project rules — everything after that marker is kept verbatim
   at the next composition, which is why the hand-written template carries it too.
   It records the choice in `.asf/instructions.json` with a hash of every composed section, so that
   a later recomposition **reports** a section edited by hand instead of overwriting it.

## Placeholders

Modules use `{{name}}` — double braces, so that code examples with `{ }` are never mistaken for a
placeholder. A module declares exactly the placeholders it uses
(`tools/validate-instructions-catalog.py` checks it). Values are one namespace per project: two
modules that use `{{be_modules_path}}` get the same value. `project_name`, `asf_version`,
`composed_at` and `catalog_ref` are filled by the host.

## Categories

| Order | Category | Cardinality | Required |
|---|---|---|---|
| 1 | Language | one | no default — stated at composition (D-8.30) |
| 2 | Localization | one | no |
| 3 | Principles | one | yes |
| 4 | System topology | one | yes |
| 5 | Internal structure | one | no |
| 6 | Communication between services | many | no (only distributed topologies) |
| 7 | Frontend stack | one | no |
| 8 | UX guidelines | one | no |
| 9 | Backend stack | many | no |
| 10 | Database | one | no |
| 11 | Code style | many | no |
| 12 | Comments and documentation | one | yes |
| 13 | Testing | many | yes |
| 14 | Logging and observability | one | yes |
| 15 | Errors | one | yes |
| 16 | Security | many | yes |
| 17 | Git workflow | one | yes |
| 18 | ASF method | one | yes |

**The languages are stated, never defaulted (D-8.30).** No `language` module is the default, and
`prose_language` and `business_language` have no default value: the language the team writes its
documents in, and the one the business speaks, are facts about the project that a default can only
guess. Ask them as their own question — *in which language do you write documents, comments and
commits?* — and do not deduce the prose from the language of the code: `language-english` means the
Prompt Stack documents are in English too. `tools/validate-instructions-catalog.py` keeps it so.

**UX guidelines** (`ux-design-guidelines`) bind interface work to `docs/requirements/ux/DESIGN.md`,
the skeleton every project is born with, and to the design tokens in the code (D-8.27).

**Topology and internal structure are two choices, not one**: microservices (topology) whose
services are each hexagonal (structure) is a normal combination.

**The ASF method** keeps its canonical section numbers (14–18): other documents cite
`instructions.md §15.x`. `asf-method-kstudio` is the method as KStudio installs it today
(state.json 1.x, ADR-020); `asf-method` is the ASF 8.3 method with the strict state.json 2.0.0.

## Adding a module

Write `modules/<category>/<id>.md` starting with a `## ` heading, declare it in `catalog.json`
with its placeholders, `when` signals, `requires`/`excludes`, then run
`python3 tools/validate-instructions-catalog.py`. A change to a module's text bumps its `version`;
projects see the new version at their next recomposition.

## Sources

Language and domain terms
- [PEP 8 — identifiers in English for the standard library and global projects](https://peps.python.org/pep-0008/)
- [GNU Coding Standards — Comments (write them in English)](https://www.gnu.org/prep/standards/html_node/Comments.html)
- [Is This Code Written in English? A Study of the Natural Language of Comments and Identifiers](https://teamscale.com/hubfs/Publications/2015-is-this-code-written-in-english-a-study-of-the-natural-language-of-comments-and-identifiers-in-practice.pdf)
- [“Write in English, Nobody Understands Your Language Here” — non-English trends in open source (ACM)](https://dl.acm.org/doi/10.1145/3744916.3787766)
- [Ubiquitous Language — Agile Alliance glossary](https://agilealliance.org/glossary/ubiquitous-language/)
- [Ubiquitous Language in DDD: A Practical Guide](https://milanjovanovic.tech/blog/ubiquitous-language-ddd)
- [How to build a ubiquitous language](https://aardling.eu/en/insights/how-to-build-a-ubiquitous-language)

Localization
- [ICU User Guide — Formatting Messages](https://unicode-org.github.io/icu/userguide/format_parse/messages/)
- [ICU message format: plurals, dates and localization syntax](https://simplelocalize.io/blog/posts/what-is-icu/)
- [9 Best Practices for i18n](https://lingoport.com/blog/9-best-practices-for-internationalization/)

Architecture
- [Hexagonal Architecture — Ports & Adapters explained](https://www.happycoders.eu/software-craftsmanship/hexagonal-architecture/)
- [Clean vs Onion vs Hexagonal Architecture](https://milanjovanovic.tech/blog/clean-architecture-vs-onion-vs-hexagonal)
- [Is Vertical Slice Architecture better than Clean Architecture or Ports and Adapters?](https://codeopinion.com/is-vertical-slice-architecture-better-than-clean-architecture-or-ports-and-adapters/)
- [What Is a Modular Monolith?](https://milanjovanovic.tech/blog/what-is-a-modular-monolith)
- [Modular monolith vs microservices](https://pretius.com/blog/modular-software-architecture)

Communication between services
- [Transactional Outbox Pattern](https://james-carr.org/posts/2026-01-15-transactional-outbox-pattern/)
- [Event-Driven Microservices: Outbox, Idempotency, and Saga Patterns](https://blog.habsi.net/event-driven-microservices-outbox-idempotency-and-saga-patterns/)
- [AsyncAPI: Bringing OpenAPI to Event-Driven Systems](https://james-carr.org/posts/2026-01-16-asyncapi-event-driven-documentation/)
- [Versioning gRPC services (Microsoft Learn)](https://learn.microsoft.com/en-us/aspnet/core/grpc/versioning?view=aspnetcore-10.0)

Testing
- [Test Pyramid vs Testing Trophy](https://www.baytechconsulting.com/blog/test-pyramid-vs-testing-trophy-whats-the-difference)
- [Contract testing with Pact (CircleCI)](https://circleci.com/blog/contract-testing-with-pact/)

Comments and documentation
- [Google documentation best practices](https://google.github.io/styleguide/docguide/best_practices.html)
- [Google Python Style Guide — comments and docstrings](https://google.github.io/styleguide/pyguide.html)

Observability, security, git
- [OpenTelemetry Logging specification](https://opentelemetry.io/docs/specs/otel/logs/)
- [Structured logging best practices](https://openobserve.ai/blog/structured-logging-best-practices/)
- [OWASP Secure Coding Practices — checklist](https://owasp.github.io/www-project-secure-coding-practices-quick-reference-guide/stable-en/02-checklist/05-checklist)
- [OWASP secrets management and environment variables](https://aquilax.ai/blog/owasp-secrets-management-environment-variables)
- [Trunk Based Development](https://trunkbaseddevelopment.com/)
- [AWS DevOps Guidance — keep feature branches short-lived](https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/dl.scm.2-keep-feature-branches-short-lived.html)
