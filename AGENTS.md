# AGENTS.md — [Project Name]

> **ASF v8.5** · 2026-10-17 · _Attachments on every artifact_ · Francesco Bellifemine

> **L0 — Project Layer · Better Innovation Technologies**
> This file is the first context every AI agent loads before any operation on this codebase.
> Read it before `architecture.json`, `product.md`, and any L2/L3 file.
> Keep it accurate — outdated instructions here corrupt every downstream agent run.
> **Agents may not modify this file. Any change requires explicit Dev Lead deliberation.**

---

## 1. What is AGENTS.md — and how to use it

**ASF™ — Augmented Software Factory**, by Better Innovation Technologies, is an operating model for delivering enterprise-grade software. It runs a **compressed Scrum cycle** in which human operators and AI agents work in parallel: humans own decisions, approvals and architectural governance — every artifact that reaches production is signed at a gate by a human (Dev Lead or PM) — while agents own execution, artifact generation and state synchronisation. Context is organised in a strict layer hierarchy, the **Prompt Stack** (`AGENTS.md` L0 → L1 → L1.5 → L2 → L3 → L4), and agents load only the layers a task requires. *Full model, agent catalogue, human roles and KPI → `@docs/asf-overview.md` (load on demand).*

`AGENTS.md` is the **L0 layer of that Prompt Stack** for this project — the single entry point every AI agent and every Claude Code session loads first. Your role within ASF™ is precise: **fast and coherent execution within a defined perimeter**. You have no autonomous merge authority and you do not modify L0/L1 files without a gate.

### How to start any session

**Always read `docs/.asf/state.json` first — before any other action.** It is the **single source of truth** for statuses, planning decisions and references: sprints, epics and their tasks, requirements, user stories, bugs, and the Prompt Stack signatures. The `.md` files hold only text (titles, descriptions, AC) and never repeat a status or a reference. Never act on assumptions, and never act on this file alone — load the current state, then the task-specific files. *What to load per goal, and where each topic lives → §5 Navigation.*

**Priority chain (highest → lowest):**
`AGENTS.md (L0)` → `architecture.json / product.md / deployment.md / instructions.md (L1)` → `requirements/RF-XX.md (L1.5)` → `epics/EpicXXX.md (L2)` → `tasks/Task.EpicXX.N.md (L3)` → `triggers/*.json (L4)`

If an L3 instruction contradicts L0 or L1 → **signal the conflict before proceeding**. Never resolve contradictions silently. The chain ranks **text**; statuses and references have one source, `state.json`, so no `.md` file is ever weighed against it.

**Fundamental rule:** every output you produce must be validated by a human before it is committed to `main` or becomes an active GitLab Issue. You have no autonomous merge authority; you do not modify Prompt Stack L0 or L1 without a gate; you do not approve Change Requests.

> **Startup gate:** **Quality Gate Layer 1** is passed when every L0/L1 file is signed in `state.json` `prompt_stack[]` (§2 → *Prompt Stack signatures*); the first sprint does not open before. What the signers check (5 certification points) → `@docs/asf-overview.md` → *Quality Gate Layer 1*.

> **Placeholders:** the `{placeholder}` values in L1 files are resolved when the Prompt Stack is instantiated on a new project.

---

## 2. Prompt Stack & Quick Reference

### Quick reference — @ file map

| Layer | File | Purpose | Who can modify |
|---|---|---|---|
| **L0** | `docs/AGENTS.md` | Universal agent context — this file | Dev Lead BIT (deliberation required) |
| **L1** | `docs/.asf/architecture.json` | **The** architectural artifact (KArchitecture schema): tech stack, repo layout, components, integrations, patterns, domain rules, and the ADR log with its full rationale | Dev Lead (gate required) |
| **L1** | `docs/product.md` | Product identity, ASF™ process model, RF index | PM (signature required) |
| **L1.5** | `docs/requirements/RF-XX.md` · `RNF-XX.md` | Individual requirement text — RF: description and full AC (BDD); RNF: metric, threshold, verification | RF: KStudio BE on RF save, Epic & Task Agent on CR · RNF: after PM approval |
| **L1** | `docs/deployment.md` | K8s runbook, triggers, pipelines, GitLab integration | Dev Lead (gate required) |
| **L1** | `docs/instructions.md` | Dev rules, sprint execution, artifact formats, testing, label system | Dev Lead (gate required) |
| **L1** | `docs/Roadmap.md` | Strategic direction — the narrative of the delivery stages, whose dates and epics are in `state.json` `roadmap[]` (PM-owned) | PM |
| **L1** | `docs/ProductLog.md` | Prioritized product backlog (PM-owned narrative) | PM |
| **L2** | `docs/epics/EpicXXX.md` | Full epic spec — objective, scope, epic AC (its tasks are in `state.json`) | Epic & Task Agent (after Dev Lead approval) |
| **L3** | `docs/tasks/Task.EpicXX.N.md` | Atomic task — AC, prompt seed | Epic & Task Agent (after Dev Lead approval) |
| **L4** | `docs/triggers/*.json` | CI activation files — consumed and deleted by pipeline | KStudio BE; agents (deletion after consumption) |

> **One architectural artifact, not two.** Until v8 the state lived in `architecture.json` and the rationale in an `architecture.md`, with a rule saying which won when they disagreed — a rule that exists only because two files can disagree at all. The ADR log now carries `context`, `options`, `rationale` and `consequences` itself, so there is nothing to reconcile.

**Supporting files (loaded on demand, not Prompt Stack layers):**

| File | Purpose |
|---|---|
| `docs/.asf/state.json` | Single source of truth — statuses, planning decisions and references; read by KStudio |
| `docs/bugs/BUG-XXX.md` | One bug: symptom, cause, expected behaviour, regression test. Status, severity and the RF/RNF it breaks are in `state.json` `bugs[]` |
| `docs/stories/US-XXX.md` | One user story: "As a … I want … so that …". Its RFs and priority are in `state.json` `user_stories[]` |
| `docs/tools/validate-stack.py` | The Prompt Stack validator — §2 *JSON contracts & validation* |
| `llm-config.json` in `docs/.asf/` (when the project has one) | Per-project LLM provider configuration |
| `docs/retro/*.md` | Sprint retrospective summaries (generated by Scrum Master Agent) |
| `fe/AGENTS.md` | L0.5 — FE-layer context (if present, load for frontend tasks) |
| `be/AGENTS.md` | L0.5 — BE-layer context (if present, load for backend tasks) |
| `api/AGENTS.md` | L0.5 — API-layer context (if present, load for API tasks) |

**RF resolution rule during implementation (agents — mandatory):**
1. Look for `docs/requirements/RF-XX.md` first (description, full AC).
2. If not found → fall back to the entry in `docs/product.md`.
3. If neither source contains the RF → raise an explicit error. Never proceed with incomplete context.

> Full repository tree (`docs/`, `fe/`, `be/`, `api/`, `infra/` layout) → `@docs/asf-overview.md` → *Standard ASF™ repository structure*.

### Prompt Stack signatures

Every L0/L1 file carries **one signature**, recorded in `state.json` `prompt_stack[]` as `{filename, validated_by, validated_at}`: who signed it and when. Who signs which file:

| Signer | Files |
|---|---|
| Dev Lead | `AGENTS.md` (`CLAUDE.md` in older projects), `.asf/architecture.json`, `instructions.md`, `deployment.md` |
| PM | `product.md`, `Roadmap.md`, `ProductLog.md` |

- **A role is not a signature.** `validated_by` is a person, `Name <email>` — never a role and never `agent:…`. Agents never write a signature.
- **Quality Gate Layer 1 is passed when every L0/L1 file is signed.** The first sprint does not open before.
- **A signature is renewed when its file changes after `validated_at`** (git history says when). A file changed after its signature counts as unsigned until it is signed again.
- ADRs are not in `prompt_stack[]`: they carry their own `accepted` status. Epics are signed in `epics[]` (`validated_by` + `validated_at`, written in the same commit as `done`), RNF verifications in `requirements.non_functional[]` (`verified_by` + `verified_at`). Human gates — approvals, trigger files under `docs/triggers/` — are unchanged.

### GitLab hierarchy mapping

| GitLab entity | Prompt Stack file | Relationship |
|---|---|---|
| **Milestone** | `Roadmap.md` | Milestone measures progress; Roadmap.md tells the direction |
| **GitLab Epic** | `docs/epics/EpicXXX.md` | GitLab Epic tracks child issues; the MD file is the cognitive spec |
| **GitLab Issue** | `docs/tasks/Task.EpicXX.N.md` | Issue is the operational tracker; Task.md is the cognitive context |
| **Iteration (Sprint)** | — | 1 week, auto roll-over, managed by Scrum Master Agent |
| **MR** | — | Mandatory Dev Lead gate before merge to `main` |

**Issue rule:** every Issue must include a direct link to its `Task.EpicXX.N.md` in the description. This is the contract that allows the Scrum Master Agent to load the correct context.

**Mandatory labels per Issue:** `status::` + `priority::` + `type::` + at least one `area::`. The `agent::` label is applied by the agent at intervention time — never set manually. Full label spec → `@docs/instructions.md` → *Label System ASF™ & GitLab Boards*.

### Document authority & agent commit governance

Agents are authorized to commit **autonomously** (without human gate) only the following:

| File / path | Autonomous commit | Condition |
|---|---|---|
| `docs/.asf/state.json` | ✅ always | Immediately after every write — never leave modified without committing |
| `docs/epics/EpicXXX.md` | ✅ after Dev Lead approval | Generated artifacts |
| `docs/tasks/Task.EpicXX.N.md` | ✅ after Dev Lead approval | Generated artifacts |
| `docs/requirements/RF-XX.md` | ✅ always | Created by KStudio BE on RF save; updated by Epic & Task Agent on CR |
| `docs/requirements/RNF-XX.md` | ✅ after PM approval | Non-functional requirement text; added with its `requirements.non_functional[]` entry in the same commit |
| `docs/bugs/BUG-XXX.md` | ✅ after Dev Lead approval | Bug report; added with its `bugs[]` entry in the same commit |
| `docs/stories/US-XXX.md` | ✅ after PM approval | Product content, like the RFs it groups; added with its `user_stories[]` entry in the same commit |
| `docs/retro/*.md` | ✅ always | Retrospective summaries — end of sprint closure job |
| `docs/triggers/*.json` | ✅ always | Deletion after consumption |
| `docs/AGENTS.md` | ❌ never | L0 — requires Dev Lead BIT deliberation |
| `docs/.asf/architecture.json` | ❌ never | L1 — as-built snapshot (KArchitecture), requires Dev Lead gate |
| `docs/product.md` | ❌ never | L1 index — requires PM signature |
| `docs/deployment.md` | ❌ never | L1 — requires Dev Lead gate |
| `docs/instructions.md` | ❌ never | L1 — requires Dev Lead gate |
| `docs/.asf/action-catalog.json` | ❌ never | Governs which actions an agent may emit at all — Dev Lead gate |
| commit gate checklist | ❌ never | Installation-wide policy: it decides what every commit is judged against — Dev Lead gate |

**Invariant — nothing an agent may do is decided by an agent.** The Action Catalogue and the
commit gate checklist define, respectively, what an agent may propose and what it is measured
against. Both are Dev Lead territory. An agent that could edit either would be setting its own
perimeter, and the record of what it was allowed to do would move with it.

**Invariant:** an agent that writes `state.json` must commit immediately in the same CI job. A write without commit is an inconsistent state — KStudio would display data GitLab has not yet received.

**Invariant — Double Bifurcation (mandatory for every `state.json` write):** follow `read-SHA → mutate → commit-with-SHA-verify`. Read the current blob SHA, apply the mutation, then commit verifying the SHA has not changed meanwhile; if it has, re-read and re-apply. This prevents race conditions between concurrent CI jobs writing the single source of truth.

**Invariant — Fibonacci story points only:** estimate every task on `1 · 2 · 3 · 5 · 8`. Never above 8 — split the task. Never mix layers in a single task (fe OR be OR api OR docs, never combined).

**Commit message format:**
```
[agent:<agent-name>] <short action> — <reason>

Examples:
[agent:scrum-master] state.json update — sprint 2 closure
[agent:epic-task] state.json + EpicXXX.md — Sprint Planning
[agent:documentation] state.json release — v0.2.0 created
[agent:coding] RF-XX done — project discovery service implemented
```

### JSON contracts & validation

Every JSON file you write or modify must declare its `$schema` and be **validated against that schema before the commit**. The frontmatter of every artifact `.md` you write is validated the same way, against the `$def` its folder selects in `frontmatter.schema.json`, and carries no `$schema` key. Load the schema first; if it is missing or cannot be loaded, that is a **blocking error** — do not write the file, surface it to the Dev Lead. This is what keeps the artifacts agents produce concordant and machine-consumable.

| JSON file | Authoritative schema |
|---|---|
| `docs/.asf/state.json` | `docs/.asf/schema/state.schema.json` |
| frontmatter of `docs/requirements/`, `epics/`, `tasks/`, `bugs/`, `stories/` and `decisions/ADR-*` `.md` files | `docs/.asf/schema/frontmatter.schema.json` — the `$def` selected by the file's folder |
| `docs/.asf/architecture.json` (KArchitecture) | KRS resource schema — declared in the file's own `$schema` field (`schemas.kronoid.org/krs/v0/…`); enforced by the KStudio BE `KArchitecture` validator |
| `llm-config.json` in `docs/.asf/` (when the project has one) | `docs/.asf/schema/llm-config.schema.json` |
| `docs/triggers/*.json` | `docs/triggers/schema/<trigger-name>.schema.json` |
| `docs/decisions/decision-log.json` | `docs/decisions/decision-log.schema.json` |
| `docs/.asf/action-catalog.json` | `docs/.asf/schema/action-catalog.schema.json` |
| commit gate checklist (installation policy) | `docs/.asf/schema/commit-gate-checklist.schema.json` |
| commit gate report | `docs/triggers/schema/commit-gate.report.schema.json` |

- **`state.json`** is the single source of truth and the most-written artifact. It is strict: a key the schema does not list is an error, and an optional array is absent rather than empty. Its `meta.schema_version` must match a version `state.schema.json` accepts. Never add or drop a top-level key without a matching schema change (Dev Lead gate). What it holds, and what is derived and never stored → `@docs/product.md` → *ASF™ Process Model — Concepts*.
- **Artifact frontmatter holds only text.** RF, RNF, epic, task, bug and story frontmatter keeps exactly the keys of its `$def` — id, title and descriptive fields, plus the two optional fields added in 8.5, `attachments` (files committed in the flat folder `docs/attachments/`, cited as pointers) and `links` (http(s) URLs of material living outside, never opened by any check); a `status`, an `epic` or any other key is an error, because statuses and references are in `state.json` only — `attachments` and `links` included, which are artifact text and never state. Their first H1 is exactly `# <id> — <title>`. ADR frontmatter is unchanged and keeps its own status.
- **`state.schema.json` is the contract**, written in the standard. Backend models, TypeScript types and Pydantic models follow it, never the reverse: if a tool and the schema disagree, the tool is wrong. Fix the tool; never patch JSON to dodge validation.
- **The schemas cannot see across files; the validator does.** `docs/tools/validate-stack.py` (copied from the standard's `tools/`, run in CI) validates both schemas plus the cross-file rules: unique ids, resolvable references, task id prefixes, an epic in at most one sprint and one roadmap stage, a story in at most one epic, no dependency cycles, repo names and `files` globs, Prompt Stack files that exist, every artifact with its file (an RF may be only a row of the `product.md` index) and every file with its entry, frontmatter id = file name, the H1, the shape of `attachments` and `links` (plus an orphan warning for an uncited file in `docs/attachments/`), and the `product.md` RF index = the RFs in `state.json`. Run `python3 docs/tools/validate-stack.py` before committing a change to `state.json` or to an artifact: exit 0 prints `Prompt Stack valid.`; exit 1 prints `N ERRORS:` and one `docs/<path>: …` line each — do not commit until it passes.

### Decision Records

When you hit a **non-obvious** architectural choice, a requirement ambiguity, or a conflict between Prompt Stack layers, produce a **Decision Record (DR) before proceeding** — never resolve it silently. All DRs live in a single file, `docs/decisions/decision-log.json` (schema `docs/decisions/decision-log.schema.json`), as entries in the `records[]` array.

**Procedure — mandatory:**
1. **Trigger.** A DR is required when any of these holds: task AC are ambiguous or contradictory; two or more valid approaches exist with non-trivial trade-offs; an RF is missing and the fallback also fails; the change would affect a component outside the task's declared scope; a pattern in `architecture.json` looks inapplicable to the case.
2. **Load** `decision-log.json` (its schema first — JSON contracts rule above). If the file does not exist yet → create it with `{"$schema": "decision-log.schema.json", "records": []}`.
3. **Next id.** Highest existing `id` in `records[]` + 1, zero-padded to 4 digits → `DR-000N`.
4. **Write the record.** Fill every required field (`id`, `date`, `agent`, `trigger`, `options[]` with `pros`/`cons`, `decision`, `impact`, `gate_required`). `status` must start at `"pending"` — never write `"approved"` or `"rejected"` yourself, that is Dev Lead territory.
5. **Commit immediately, on its own:** `[agent:<name>] DR-000N pending — <trigger summary>`. Do not bundle it with other changes.
6. **Block or proceed on `gate_required`.** `true` → halt and wait for the Dev Lead to set `status: "approved"` before continuing. `false` → you may proceed, but the record must be committed before the implementing commit.

`status` lifecycle: `pending` → `approved` | `rejected` (Dev Lead) → optionally `superseded` (a later DR replaces it). Agents create and maintain `pending` records; only the Dev Lead ratifies them at the gate.

---

## 3. Agents & roles — who does what

The full catalogue of **CI agents** (who activates them, what they produce, what they cannot do) and the **human roles** (PM, Dev Lead, Developer Senior, QA Lead) live in `@docs/asf-overview.md` → *Agents* and *Human roles* — they are not needed in a working session, load them only if you need to understand the factory model.

What is operational for you in session is already above: **what you may commit and in what format** → *Document authority & agent commit governance* (§2).

> **Code Generation Agent — pre-implementation checklist:** see `@docs/instructions.md` → *Code Generation Agent*.
> **Layer instructions and the layer AGENTS.md loader (7-section standard):** see `@docs/instructions.md` → *Layer instructions & layer AGENTS.md loader*.

---

## 4. Agent commands — Shortcuts

> The "read `state.json` first" rule (§1) applies to every command below — it is the precondition, not a step to skip.

### Command: "Develop / Implement EpicXXX"

When the user asks to develop or implement an epic, follow these steps in the exact order given:

1. **Read `docs/.asf/state.json`** → find the epic in `epics[]` and collect what it brings in: the RFs its tasks cite (`epics[].tasks[].rf_refs`), its `rnf_refs` and `user_story_refs`, the bugs its tasks fix (`bug_refs`), and the `depends_on` of the epic and of its tasks. Do not make assumptions — read the data.
2. **Resolve every linked artifact**: each RF from `docs/requirements/RF-XX.md` (fallback: its row in the `docs/product.md` RF index), each RNF from `docs/requirements/RNF-XX.md`, each story from `docs/stories/US-XXX.md`, each bug from `docs/bugs/BUG-XXX.md`. If one cannot be resolved → blocking error. Never proceed with incomplete context.
3. **Read `docs/epics/EpicXXX.md`** → verify objective, scope and epic AC.
4. **Read the `Task.EpicXXX.N.md` files** in the order their `depends_on` in `state.json` gives.
5. **Only after steps 1–4**: start implementation following the rules in `@docs/instructions.md` → *Sprint Execution*.

---

## 5. Navigation — what to load, where to find what

This is the single navigation map. (The layer/ownership reference is §2; this section is the only place that answers "where does topic X live".)

**What to load per goal** — always *after* reading `state.json`; `@docs/AGENTS.md` (this file) is implicit:

| Goal | Also load |
|---|---|
| Understand the project | — |
| Architecture / ADR | `@docs/.asf/architecture.json` |
| Plan an epic / review requirements | `@docs/.asf/architecture.json @docs/product.md` |
| Generate tasks for an epic | `@docs/.asf/architecture.json @docs/product.md @docs/epics/EpicXXX.md` |
| Implement a task | `@docs/.asf/architecture.json @docs/product.md @docs/requirements/RF-XX.md @docs/epics/EpicXXX.md @docs/tasks/Task.EpicXX.N.md` — plus the `RNF-XX.md`, `US-XXX.md` and `BUG-XXX.md` files its epic and task cite in `state.json` |
| Deploy / infrastructure | `@docs/deployment.md` |

**Where each topic lives** — section *names*, stable across renumbering:

| Topic | File → Section |
|---|---|
| ASF™ process model (state.json and what is derived from it, RF, RNF, CR, Epic, Task, Bug, User story, Sprint, Roadmap, Release, signatures) | `@docs/product.md` → *ASF™ Process Model — Concepts* |
| Sprint execution + prompt templates (planning, developing, completing, closure, release) | `@docs/instructions.md` → *Sprint Execution* |
| Artifact formats (RF, RNF, Epic, Task, Bug, User story, Release Notes, Retrospective) | `@docs/instructions.md` → *Artifact Formats — Templates* |
| Bugs and user stories (one file each) | `docs/bugs/BUG-XXX.md` · `docs/stories/US-XXX.md` — a bug's status, severity and references in `state.json` `bugs[]`; a story's RFs in `user_stories[]` (its status is derived from them) |
| JSON contracts, frontmatter, the validator · Prompt Stack signatures | this file → §2 *JSON contracts & validation* · *Prompt Stack signatures* |
| Label system & GitLab boards | `@docs/instructions.md` → *Label System ASF™ & GitLab Boards* |
| Layer instructions & layer AGENTS.md loader (7-section standard for fe/be/api) | `@docs/instructions.md` → *Layer instructions & layer AGENTS.md loader* |
| Code quality standards & anti-patterns | `@docs/instructions.md` → *Logging* … *Anti-patterns to avoid* |
| Code Generation Agent pre-implementation checklist | `@docs/instructions.md` → *Code Generation Agent* |
| Triggers, pipelines, GitLab sync | `@docs/deployment.md` → *Triggering & Pipelines* |
| GitLab integration (RF completion, MR policy) | `@docs/deployment.md` → *GitLab Integration* |
| Tech stack, repo layout, components, integrations, patterns, domain rules, ADR | `@docs/.asf/architecture.json` (full file, KArchitecture schema) |
| LLM provider config | `llm-config.json` in `docs/.asf/` (per-project data, when the project has one) · `@docs/.asf/architecture.json` → `llmPolicy` (the rule) |
| Product vision, target user, flows, RF index | `@docs/product.md` → *Product vision* … *Open issues* |
| ASF™ model, agent catalogue, human roles, KPI, startup gate, repo tree | `@docs/asf-overview.md` (load on demand) |

---

## 6. Commands

These are the **general** dev-tool commands for the ASF™ stack, verified against the BIT projects (KStudio, AIRA) — the baseline that applies to most projects. They are **not exhaustive**: additional or project-specific commands (and any that diverge from this baseline) are listed in `@docs/instructions.md` → *Reference stack*, scoped to the project's particular stack and tooling. A project's layer `AGENTS.md` may also override an entry — when it does, that file wins for its layer.

**Frontend (`fe/`) — Vite · TypeScript · Vitest · ESLint (npm)**
- Dev: `npm run dev` (Vite, port 5173)
- Build: `npm run build` (`tsc -b && vite build`)
- Typecheck: `npm run typecheck` (`tsc --noEmit`)
- Lint: `npm run lint` (`eslint .`)
- Test: `npm test` (`vitest run`)
- Single test: `npx vitest run path/to/file.spec.ts`
- Test (watch): `npm run test:watch`

**Backend — Python/FastAPI (`be/`, e.g. KStudio) — pip + setuptools**
- Install (dev): `pip install -e ".[dev]"`
- Dev: `uvicorn app.main:app --reload --port 8000`
- Test: `pytest`
- Single test: `pytest path/to/test_file.py::test_name`

**Backend — Node/Prisma (`be/`, e.g. AIRA) — npm**
- Dev: `npm run dev` (`tsx watch src/index.ts`)
- Build: `npm run build` (`tsc`) · Start: `npm start` (`node dist/index.js`)
- Test: `npm test` (`vitest run`)
- Codegen (Prisma client): `npx prisma generate`
- New migration: `npx prisma migrate dev --name <desc>`
- Apply migrations: `npm run db:migrate` (`prisma migrate deploy`)
- Seed DB: `npm run db:seed` (`tsx prisma/seed.ts`)

**Local environment**
- Full stack up: `docker compose up -d` (KStudio: be on 8000, fe on 5173)

**Git workflow** (full spec → `@docs/instructions.md` → *Git Workflow*)
- Branch: `feature/<area>-<desc>` (e.g. `feat/EpicXXX-N-user-auth`); urgent fix `hotfix/<desc>`
- Open MR: squash-and-merge, PR title `[vX.Y.Z] <task name>`, no merge without green CI (incl. SAST/DAST) — Code Generation Agent never opens MRs autonomously
- Agent commit: `[agent:<name>] <short action> — <reason>` (full spec → *Document authority & agent commit governance*)
