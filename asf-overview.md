# ASF™ Overview — reference, load on demand

> **ASF v8.6** · 2026-10-20 · _Attachments and project layers_ · Francesco Bellifemine

> **This file is NOT a layer of the Prompt Stack.**
> Load it only when you need to understand the factory model itself: the agent
> catalogue, human roles, the startup Quality Gate, or the full repository layout.
> In a normal working session (implementing a task, planning an epic) you do **not** need this file.
> The operational entry point is always `@docs/AGENTS.md` (L0).

---

## 1. The ASF™ model in one page

**ASF™ — Augmented Software Factory**, by Better Innovation Technologies, is an operating model for delivering enterprise-grade software. It runs a **compressed Scrum cycle** in which human operators and AI agents work in parallel:

- **Humans** own decisions, approvals and architectural governance — every artifact that reaches production is signed at a gate by a human (Dev Lead or PM).
- **Agents** own execution, artifact generation and state synchronisation — fast, coherent execution within a defined perimeter, with no autonomous merge authority.

Context is organised in a strict layer hierarchy, the **Prompt Stack** (`AGENTS.md` L0 → L1 → L1.5 → L2 → L3 → L4). Agents load only the layers a task requires; lower layers never override higher ones, and conflicts are surfaced, never resolved silently.

The cycle runs **Startup → Planning → Sprint Execution → Sprint Closure → Release**, producing a versioned, deployable release every iteration.

### ASF™ KPI — engagement targets

| KPI | Target | Rationale |
|---|---|---|
| First delivery | 30 days | Working software on staging, not a prototype |
| Sprint duration | 1 week | Compression via AI acceleration on execution |
| Engagement duration | 12 months min | Full transfer: methodology, trained developers, operational factory |

---

## 2. Quality Gate Layer 1 — mandatory before the first sprint

Quality Gate Layer 1 is **passed when every L0/L1 file is signed**: one signature per file in
`state.json` `prompt_stack[]`, by the Dev Lead or the PM according to the file (who signs which
file → `@docs/AGENTS.md` → *Prompt Stack signatures*). Before signing, the signers certify 5 points:

1. `architecture.json` initialized with components, tech stack and the first ADRs in `adLog`.
2. `product.md` complete with vision, target user, look & feel, linked Figma files and draft AC for the candidate epics.
3. `deployment.md` aligned with the pipeline in `infra/`.
4. `AGENTS.md` initialized for every layer repo (`fe/`, `be/`, `api/`) with context, conventions and domain rules.
5. Epic Board populated with at least 3 sprints of backlog.

If even a single point is missing, the files it concerns are not signed and Startup is extended. Never start a sprint before the gate. A signature is renewed when its file changes after `validated_at`; until then the file counts as unsigned.

---

## 3. Standard ASF™ repository structure

```
[group-slug]/
├── docs/                # Prompt Stack — factory brain
│   ├── AGENTS.md        # L0 — universal agent context
│   ├── product.md       # L1 — product identity, ASF™ process model, RF index
│   ├── requirements/    # L1.5 — RF-NN.md and RNF-NN.md, one per requirement (v0.4+)
│   ├── deployment.md    # L1 — K8s runbook, triggers, pipelines
│   ├── instructions.md  # L1 — dev rules, sprint execution, artifact formats
│   ├── Roadmap.md       # Strategic direction (PM-owned)
│   ├── ProductLog.md    # Prioritized backlog (PM-owned)
│   ├── epics/           # L2 — EpicXXX.md per feature
│   ├── tasks/           # L3 — Task.EpicXX.N.md per task
│   ├── bugs/            # v8.3 — BUG-XXX.md per bug (status and references in state.json)
│   ├── stories/         # v8.3 — US-XXX.md per user story (its RFs in state.json)
│   ├── retro/           # Retrospective summaries per sprint
│   ├── triggers/        # JSON files for CI agent activation
│   ├── decisions/       # decision-log.json (Decision Records, DR); ADR-*.md where a project keeps
│   │                    #   ADRs as files — the ADR log itself is architecture.json → adLog[]
│   ├── tools/
│   │   └── validate-stack.py    # v8.3 — Prompt Stack validator, copied from the standard, run in CI
│   └── .asf/
│       ├── architecture.json    # L1 — KArchitecture: tech stack, repo layout, components,
│       │                        #      integrations, patterns, domain rules, adLog with rationale
│       ├── state.json           # Single source of truth: statuses, planning, references, signatures
│       ├── llm-config.json      # LLM provider config, per project
│       ├── action-catalog.json  # v8.0 — the action codes agents may emit
│       └── schema/              # state.schema.json, frontmatter.schema.json and the other contracts
├── fe/                  # Frontend — with AGENTS.md layer (7-section standard)
├── be/                  # Backend — with AGENTS.md layer (7-section standard)
├── api/                 # OpenAPI contracts — with AGENTS.md layer
└── infra/               # IaC Pulumi — managed by Infrastructure Agent
    └── environments/<env>/  # each environment's configuration (product.md and deployment.md point here)
```

> **What is not here.** The agent specifications and their importable definitions live in the
> standard repository under `agents/`, not in a project. They are what you need to *install* the
> factory on an agentic platform; a project consumes the agents, it does not carry their
> configuration.
>
> The standard's own `tools/` is not here either: it holds `validate-stack.py`, which a project
> copies into `docs/tools/` (above), and `migrate-to-8.3.py`, which converts a v8.2 `docs/` tree
> once and is not kept in the project.

---

## 4. Agents — who does what

**Status** says whether the agent exists as something you can install today. An agent is
*implemented* when it has a specification and an importable definition under
[`agents/`](agents/README.md); anything else is a description of intent, however precise.
The distinction is not bookkeeping: the Action Catalogue names some of these agents as the
executors of its codes, and an analysis agent will emit an action addressed to one of them.

| Agent | Status | Activated by | Produces | Cannot do |
|---|---|---|---|---|
| **Commit Gate Agent** (v8.0+) | [implemented](agents/commit-gate/commit-gate.md) | Any push on any branch, and merge request events | `commit-gate` report: per-check verdict, navigable findings, ranked actions as catalogue codes | Write to any repo, block a merge, execute the actions it emits |
| **ASF Compliance Agent** (v8.0+) | [implemented](agents/asf-compliance/asf-compliance.md) | On demand, before a gate review or on taking over a project | Conformance report: ASF phase, Quality Gate L1 status, `state.json` health, per-area verdict, ordered actions | Write to any repo, create missing artifacts, sign Quality Gate L1 |
| **ASF Area Agent** (v8.0+) | [implemented](agents/asf-area/asf-area.md) | Delegation from another agent, sharing its workspace | One area verdict with counts, and what it could not read | Write, clone, or judge an area it was not asked about |
| **ASF Dev Agent** (v8.0+) | [implemented](agents/asf-dev/asf-dev.md) | A bounded implementation objective, from a human or a dispatched `CODE.GENERATE.CHANGE` | Modified files in the conversation workspace, plus a report compiled from the diff | Commit, push, open or approve an MR, modify L0/L1, plan its own work |
| **Pitch Agent** (v8.1+) | [implemented](agents/pitch/pitch.md) | A person, through a host that owns the conversation | A **pitch package**: context, requirements functional and non-functional, user stories, epics, diagrams, coverage and provenance per field — method-neutral, with local keys | Hold any tool, read or write a repository, assign an identifier, create a file, declare itself complete, sign |
| **Pitch Translation Agent** | **to be implemented** | A pitch package marked `ready` | ASF artifacts from a package: `RF-XX.md`, `EpicNNN.md`, the RF index — and the identifiers the pitch deliberately does not assign | Sign the gate, or invent what the package does not say |
| **Epic & Task Agent** | **to be implemented** | `epic-ready.json` or `cr-approved.json` trigger | `EpicXXX.md`, `Task.EpicXX.N.md`, `state.json` updates | Modify L0/L1, approve epics autonomously |
| **Task Generation Agent** | **to be implemented** | `epic-tasks-gen-<epic_id>.json` trigger (or BE in-process) | `Task.EpicXX.N.md`, the epic's `tasks[]` in `state.json` `epics[]` | Generate production code |
| **Test Generation Agent** | **to be implemented** | Commit on a feature branch (CI) | Playwright/Pytest tests from the AC in Task.md | Define test strategy (the QA Lead's responsibility) |
| **Scrum Master Agent** | **to be implemented** | `sprint-close.json` trigger + scheduled CI cron | `docs/retro/*.md`, sprint closure in `state.json` `sprints[]`, GitLab issue sync | Modify backlog priorities, approve a CR |
| **Documentation Agent** | **to be implemented** | `release-ready.json` trigger | Release notes, GitLab Release, `state.json` `releases` | Commit L0/L1 autonomously |
| **Infrastructure Agent** | **to be implemented** | `infra-bootstrap.json` or `infra-change.json` trigger | `deployment.md`, Pulumi code, K8s provisioning | Run `apply` without Dev Lead approval |
| **Code Generation Agent** (interactive) | external tool | Developer Senior in an editor | Code, scaffold, refactoring | Commit autonomously, open an MR, modify L0/L1 |
| **Code Review Agent** (GitLab Duo) | external product | MR opened on GitLab | Structured review comments on the diff | Approve or reject an MR (advisory only) |
| **RIB Delta Engine** (v7.0+) | external product (KStudio) | PM opens a CR in KStudio | Impact report: affected RF, epics, tasks, effort estimate, risks | Modify the Prompt Stack (read-only analysis) |

**external** means the capability is provided by another product and will not gain an ASF
specification: GitLab Duo and KStudio are not ours to specify, and the interactive Code
Generation Agent is a person driving an editor. Its unattended counterpart **is** ours, and
is the ASF Dev Agent above.

**Eight of the fifteen actions in the Action Catalogue name an executor that is not yet
implemented**, and they carry `executor_implemented: false` so that a caller learns this from
the catalogue rather than from a dispatch that finds nobody home. The four agents concerned
are `epic-task-agent`, `task-generation-agent`, `test-generation-agent` and
`documentation-agent`.

---|---|---|---|
| **Code Generation Agent** (Claude Code, interactive) | Developer Senior in VS Code | Code, scaffold, refactoring | Commit autonomously, open MR, modify L0/L1 |
| **Epic & Task Agent** | `epic-ready.json` or `cr-approved.json` trigger | `EpicXXX.md`, `Task.EpicXX.N.md`, `state.json` updates | Modify L0/L1, approve epics autonomously |
| **Task Generation Agent** | `epic-tasks-gen-<epic_id>.json` trigger (or BE in-process) | `Task.EpicXX.N.md`, the epic's `tasks[]` in `state.json` `epics[]` | Generate production code |
| **RIB Delta Engine** (v7.0+) | PM opens CR in KStudio | Impact report: impacted RF, epics, tasks, effort estimate, risks | Modify Prompt Stack (read-only analysis) |
| **Code Review Agent** (GitLab Duo) | MR opened on GitLab | Structured review comments on diff | Approve or reject MR (advisory only) |
| **Test Generation Agent** | Commit on feature branch (CI) | Playwright/Pytest tests from AC in Task.md | Define test strategy (QA Lead's responsibility) |
| **Infrastructure Agent** | `infra-bootstrap.json` or `infra-change.json` trigger | `deployment.md`, Pulumi code, K8s provisioning | Run `apply` without Dev Lead approval |
| **Scrum Master Agent** | `sprint-close.json` trigger + scheduled CI cron | `docs/retro/*.md`, sprint closure in `state.json` `sprints[]`, GitLab issue sync | Modify backlog priorities, approve CR |
| **Documentation Agent** | `release-ready.json` trigger | Release notes, GitLab Release, `state.json` `releases` | Commit L0/L1 autonomously |
| **Commit Gate Agent** (v8.0+) | Any push on any branch, and merge request events | `commit-gate` report: per-check verdict, navigable findings, ranked actions as catalogue codes | Write to any repo, block a merge, execute the actions it emits |
| **ASF Compliance Agent** (v8.0+) | On demand, before a gate review or on taking over a project | Conformance report: ASF phase, Quality Gate L1 status, `state.json` health, per-area verdict, ordered actions | Write to any repo, create missing artifacts, sign Quality Gate L1 |
| **ASF Area Agent** (v8.0+) | Delegation from another agent, sharing its workspace | One area verdict with counts, and what it could not read | Write, clone, or judge an area it was not asked about |
| **ASF Dev Agent** (v8.0+) | A bounded implementation objective, from a human or a dispatched `CODE.GENERATE.CHANGE` | Modified files in the conversation workspace, plus a report compiled from the diff | Commit, push, open or approve an MR, modify L0/L1, plan its own work |
| **Pitch Agent** (v8.1+) | A person, through a host that owns the conversation | A method-neutral **pitch package** with provenance per field | Hold any tool, touch a repository, assign an identifier, create a file, sign |

---

Full specifications live in [`agents/`](agents/README.md), one directory per agent: the
specification and the importable definition side by side. Agents that **read** hold no tool
that can write — the separation is enforced by permissions, not by instruction, so that a
finding and its remedy always come from different actors.

---

## 4-bis. Vocabulary introduced in v8.0

**Action Catalogue** — the closed set of remediation actions an agent may emit
(`.asf/action-catalog.json`). Each entry is a stable code, `DOMAIN.PRIMITIVE.OBJECT`, with an
executor, a target, an idempotency flag and a JSON Schema for its parameters. It exists
because a recommendation written in prose is readable by everyone and dispatchable by nobody:
hooking a finding to an API function needs an identifier and typed parameters. **An agent
selects a code; it never invents one** — an improvised code silently breaks every caller that
mapped the catalogue.

**Primitive** — one of the eight verbs codes are built from: `LINK`, `CREATE`, `UPDATE`,
`RUN`, `GENERATE`, `REQUEST`, `ESCALATE`, `NONE`. A caller that implements the primitives can
dispatch codes added later without new integration work.

**Commit Gate** — the analysis that runs on every push, on any branch, and judges one commit
against a configurable checklist. It returns a verdict, a navigable list of findings and
ranked actions as catalogue codes. It is **advisory**: enforcement is a CI or MR rule owned
by the project, never the agent's own act.

**Checklist** — the policy the Commit Gate judges against. Versioned configuration rather
than prompt content, so that changing what a commit is measured against is an administrative
act and not a release. Owned by the Dev Lead.

**Next Best Action (NBA)** — one emitted action, ranked across the whole report, so that
"what to do next" is `rank: 1` rather than a judgement left to the reader. It names an
executor and is never carried out by the agent that emitted it.

---

## 5. Human roles

| Role | Key responsibilities | Owns |
|---|---|---|
| **PM / Product Owner** | Stakeholder interface, RF elicitation, epic candidate selection, CR signature, Roadmap update, signature of the files below in `prompt_stack[]` (Quality Gate L1) | `product.md`, `Roadmap.md`, `ProductLog.md` |
| **Dev Lead / Tech Lead** | Architecture governance, signature of `AGENTS.md`, `architecture.json`, `deployment.md`, `instructions.md` in `prompt_stack[]` (Quality Gate L1), MR gate, Prompt Stack L0-L1 ownership, pattern promotion, **commit gate checklist and Action Catalogue** | `AGENTS.md`, `architecture.json`, `deployment.md`, `instructions.md`, `action-catalog.json`, commit gate checklist |
| **Developer Senior** | Task execution with Code Gen Agent, output validation, MR opening, layer AGENTS.md ownership | `fe/AGENTS.md`, `be/AGENTS.md`, `api/AGENTS.md` |
| **QA Lead** | AC definition strategy, test coverage validation, acceptance gate pre-Review | AC quality in `product.md` / Task.md |

> **Code Generation Agent — pre-implementation checklist:** see `@docs/instructions.md §14`.
> **AGENTS.md layer structure (7-section standard):** see `@docs/instructions.md §18`.
