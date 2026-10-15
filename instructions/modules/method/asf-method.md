<!-- ASF 8.3 method: state.json schema 2.0.0 (strict). Sections keep their canonical numbers: other documents cite them as instructions.md §15.x. -->

## 14. Code Generation Agent — pre-implementation checklist

**What to check before generating:**
- Does the Task.md have explicit AC? If not → ask before proceeding.
- Does the output respect patterns in `architecture.json` and applicable ADRs?
- Is the layer-specific AGENTS.md (`fe/AGENTS.md` or `be/AGENTS.md`) in context? If not → load it.
- Am I about to touch something that would change `architecture.json` or `product.md`? If yes → flag it for Retrospective, do not modify.
- Has the **Code Review Agent** (GitLab Duo) flagged patterns from previous MRs? Check comments.
- Are the **Test Generation Agent** tests aligned with the AC? Verify before marking task done.

---

## 15. Sprint Execution — Step by Step

> Per le definizioni dei concetti (Epic, Task, Sprint, ecc.) → `@docs/product.md §12. ASF™ Process Model`.

### 15.1 SCRUM AI phases overview

```
Startup → Planning → Sprint Execution → Sprint Closure (Review + Retrospective) → Release
```

| Phase | Key actors | Key outputs |
|---|---|---|
| **Startup** | PM, Dev Lead, Infrastructure Agent | Project bootstrapped, GitLab configured, `state.json` initialized, Quality Gate L1 passed (every L0/L1 file signed in `prompt_stack[]`) |
| **Planning** | PM, Dev Lead, Epic & Task Agent | `EpicXXX.md`, `Task.EpicXX.N.md`, `state.json` updated, GitLab Issues created |
| **Sprint Execution** | Developer Senior, Code Gen Agent, Code Review Agent, Test Gen Agent, QA Lead | Code committed, MRs merged, `state.json` updated task by task |
| **Sprint Review** | PM, Dev Lead, Documentation Agent, cliente | Demo su staging, release notes, Roadmap.md aggiornato |
| **Retrospective** | Dev Lead, Developer Senior, QA Lead, Scrum Master Agent | Pattern promotion, Prompt Stack updated |
| **Release** | Documentation Agent, Dev Lead | Release notes, GitLab Release tag, release recorded in `state.json → releases[]` |

### 15.2 Startup phase

1. PM configures project in KStudio (GitLab URL, PAT, group, project name).
2. KStudio BE bootstraps `docs/` with all L1 template files, initializes `state.json`.
3. PM fills `docs/product.md` and signs it (Block ①).
4. PM builds and signs `Roadmap.md` and `ProductLog.md`. Epic & Task Agent supports first epic generation (Block ②).
5. Dev Lead initializes and signs `AGENTS.md`, `architecture.json`, `deployment.md` and `instructions.md`, and writes the AGENTS.md loader per layer (Block ③).
   `architecture.json` must include at least one completed ADR in `adLog[]` (not an empty
   placeholder) — a precondition for certifying point 1 of Quality Gate Layer 1.
6. **Quality Gate Layer 1** is passed when every L0/L1 file is signed: one `prompt_stack[]` entry
   per file in `state.json`, with `validated_by` (a person, `Name <email>`) and `validated_at`.
   It is derived, never stored; the first sprint does not open before. A signature must be renewed
   when its file changed after `validated_at` (git history). Who signs which file → AGENTS.md;
   the certification checklist → `asf-overview.md`.
7. PM commits `infra-bootstrap.json` to trigger Infrastructure Agent (v1.0+).

### 15.3 Planning — from RF to Epic to Task

**Pre-condition:** Quality Gate Layer 1 passed (every L0/L1 file signed in `prompt_stack[]`). `docs/product.md` must be complete for the sprint scope, with a PM signature newer than its last change.

1. PM selects epic candidates from `docs/ProductLog.md`.
2. Dev Lead reviews technical feasibility against `docs/.asf/architecture.json`.
3. PM opens gate `epic-ready` → KStudio BE commits `epic-ready.json` in `docs/triggers/`.
4. Epic & Task Agent reads L0 + L1, generates `EpicXXX.md` per approved epic.
5. Agent decomposes each epic into atomic tasks → generates `Task.EpicXX.N.md`.
6. Agent plans each epic in **one commit**: the epic enters `state.json → epics[]` together with all
   its tasks (`epics[].tasks[]`, at least one) and, if it is planned in a sprint, its id is added to
   that sprint's `epic_refs` (an epic in no sprint is in the backlog). The epic carries `status`,
   `product_priority`, `kind`, `depends_on`, `user_story_refs`, `rnf_refs`; each task `status`,
   `points`, `rf_refs` / `bug_refs`, `depends_on`, `files`. Nothing else is written: titles live in
   the `.md` files, points and the epic's RFs are derived from its tasks.
7. Agent commits: `[agent:epic-task] state.json + EpicXXX.md — Sprint Planning S[N]` (the epic, its
   Task.md files and the `state.json` change together).
8. Dev Lead reviews all files. Scrum Master Agent creates GitLab Issues from Task.md.
9. Approved → Sprint Execution starts.

**Task decomposition rules:**
- 1 task = 1 layer (fe OR be OR api OR docs): every glob in its `files` starts with the same
  repository name. The layer is not a field — it is read from `files`.
- `files` = the globs the task is expected to touch, relative to the folder holding the repos
  (`<repo>/<path>`, `<repo>/<folder>/**`; `<repo>` is the last segment of its URL in
  `project.repos`, without `.git`). Two tasks with no file in common and no `depends_on` between
  them may run in parallel. It is a forecast: once the task is closed, its commits are the truth.
- Every task cites ≥1 RF (`rf_refs`) or bug (`bug_refs`), unless its epic has `rnf_refs`.
- Task ids start with their epic id and are numbered in order (`Task.EpicXXX.N`, N = 1, 2, 3, …).
- Bugs enter an epic only through the task that fixes them (`bug_refs`); the tasks fixing the
  sprint's bugs are collected in an epic of `kind: container`.
- 1 task = 1 cohesive responsibility
- Story points: Fibonacci 1/2/3/5/8 — split if >8
- AC in BDD format — granular enough for Test Generation Agent

**Prompt for Epic & Task Agent (Sprint Planning):**
```
@docs/AGENTS.md @docs/.asf/architecture.json @docs/product.md @docs/ProductLog.md

Sprint Planning — [date].
Epic candidates: [list from ProductLog.md].
For each approved epic generate:
1. docs/epics/EpicXXX.md — objective, scope, AC (format: instructions.md §16.4)
2. docs/tasks/Task.EpicXX.N.md — per atomic task with context, BDD AC and prompt seed (§16.5)
3. the state.json entries of §15.3 step 6 — epic depends_on, rnf_refs, user_story_refs;
   per task points, rf_refs / bug_refs, depends_on, files

Do not commit. Output as proposal for Dev Lead review.
```

### 15.4 Developing an Epic

Work task by task, in dependency order. **Use the "Develop EpicXXX" command (AGENTS.md §4) as the mandatory entry point.**

**Before starting any task:**
1. Read `state.json` → the epic's requirements: the RFs cited by its tasks (`rf_refs`), its `rnf_refs` and `user_story_refs`, and the bugs in its tasks' `bug_refs`.
2. Resolve each one: RF → `docs/requirements/RF-XX.md` (fallback: its row in the `docs/product.md` RF index); RNF → `docs/requirements/RNF-XX.md`; user story → `docs/stories/US-XXX.md`; bug → `docs/bugs/BUG-XXX.md`. A reference that cannot be resolved is a blocking error.
3. Leggi `docs/epics/EpicXXX.md` e il `Task.EpicXX.N.md` attivo → verifica AC espliciti.
4. Genera codice rispettando i pattern in `architecture.json` e gli ADR.
5. Presenta l'output al Developer Senior prima di qualsiasi commit.

Never start implementing an epic without approved Task.md files.

### 15.4bis Task verification — tests and DoD

Tests are part of the task, not a follow-up. They must be written in the same session as the implementation and must be green before the MR is opened.

**Who writes the tests:** Code Generation Agent proposes them; **Test Generation Agent** translates AC into Playwright/Pytest; **QA Lead** validates strategic coverage; Developer Senior reviews and runs them.

**What to test per task:**
- Every AC in the Task.md must have at least one corresponding test.
- AC in BDD format (`Given / When / Then`) map directly to test cases.
- Unit tests cover business logic in isolation.
- Integration tests cover boundaries: API endpoints, external calls, DB interactions.
- Frontend component tests cover user-visible behavior, not implementation details.

**DoD checklist — mandatory before closing a task:**

- [ ] Code implemented and buildable
- [ ] All task AC covered by tests
- [ ] Tests green locally
- [ ] TypeScript `strict` typecheck clean / mypy clean
- [ ] No new `any`, no swallowed exceptions, no silent fallbacks
- [ ] SAST/DAST security scan clean
- [ ] MR opened with link to Task.md in description
- [ ] Code Review Agent (GitLab Duo) comments resolved
- [ ] Dev Lead approve on MR

**If tests fail:** fix the implementation before marking the task done.

**If a discovered edge case is not covered by existing AC:** flag it to the Developer Senior before implementing a fix. It may require a new task or a CR.

### 15.5 Completing a Task — mandatory state updates

**Every task completion is one commit — never deferred — with exactly these two changes:**

1. `state.json → epics[].tasks[]`: the task's `status` → `"done"`.
2. `docs/tasks/Task.EpicXX.N.md`: its AC checked `[x]`.

Nothing else is written — no counters, no milestones, no `meta` timestamps, no status line in a
`.md`. Epic progress and points, velocity and burndown are derived from the tasks (`product.md` §12).

**RF completion:** an RF goes `done` in `state.json → requirements.functional[]` when all its AC are
implemented and tested. Only its `status` changes; `product.md` and `RF-XX.md` carry no status.

**Epic validation gate — mandatory before setting the epic's `status: "done"`:**

When every task of the epic is `done` (the epic may meanwhile be `review`: delivered, awaiting the signature):
1. Developer Senior verifies all epic-level AC satisfied.
2. Developer Senior confirms all tests pass.
3. Developer Senior confirms last task MR has Dev Lead approval.
4. Only then, in one commit: the epic's `status: "done"`, `validated_by: "Name <email>"`,
   `validated_at: "YYYY-MM-DD"`, and its AC checked `[x]` in `EpicXXX.md`.

An epic is `done` if and only if it is signed. `validated_by` is a person written as a commit author
(`Name <email>`) — never `"agent:*"`; a role is not a signature.

### 15.6 state.json ↔ .md — one fact, one place

- `state.json` holds statuses, planning decisions and references; the `.md` files hold only text
  (titles, descriptions, AC). Nothing is copied between them. Concept → `product.md` §12.
- No `.md` repeats state or references: no `**Status**` or `**Layer**` lines, no `Validated by`,
  `Area`, `RF covered` or `Dependencies` header lines, no "RF in scope" tables, no ✅ or status
  columns. Frontmatter holds only the keys of §16 (`frontmatter.schema.json`) and the first H1
  is `# <id> — <title>`. AC checkboxes stay: they are AC text.
- The `product.md` RF index lists exactly the RFs of `state.json` (id and title): it changes only
  when an RF is added, removed or retitled, and the PM signature is then renewed.
- What can be derived is never written: epic points and progress, velocity, the RFs of an epic,
  the epics of an RF or bug, story status, file paths, who changed what and when (git).

**One source for state:** a status exists only in `state.json`, so there is no precedence between
`state.json`, `product.md`, `RF-XX.md` and `EpicXXX.md` about statuses. Conflicts of text still
follow the layer hierarchy (AGENTS.md priority chain). `docs/tools/validate-stack.py`, run in CI,
checks these rules (AGENTS.md, JSON contracts).

### 15.7 Sprint Review

Day 5. With the client. On staging environment. Max 1 hour.

1. PM presents results on staging — software funzionante, not slides.
2. Dev Lead brings technical data: velocity, test coverage, merged MRs.
3. Documentation Agent has already generated release notes from MRs.
4. Client evaluates, accepts or provides feedback.
5. If feedback modifies specs → PM updates `product.md` before Retrospective.
6. **Roadmap.md must be updated** — it certifies the direction, sprint after sprint.
7. Scrum Master Agent closes Iteration and auto-reassigns incomplete Issues.

### 15.8 Sprint Closure — Retrospective

Same day as Review. Internal team only. 45 minutes.

Scrum Master Agent prepares objective synthesis: velocity, cycle time, MRs with most comments, pipeline failure rate.

**Pattern promotion (Dev Lead decision):**
- Pattern for current project → `architecture.json` or layer `AGENTS.md`
- Pattern for all BIT projects → `AGENTS.md` aziendale (L0) — explicit deliberation required
- Anti-pattern → Anti-patterns section of appropriate AGENTS.md
- `deployment.md` updated if pipeline revealed gaps

Scrum Master Agent then:
1. Generates `docs/retro/<YYYY-WW>.md`.
2. Closes the sprint in `state.json`, in one commit: `status: "closed"` and `closed_on`; normally the
   epics not yet `done` move from its `epic_refs` to the next sprint's `epic_refs` (an epic is in at
   most one sprint). Nothing else is written — the final velocity is derived from the `done` tasks.
3. Commits: `[agent:scrum-master] state.json — sprint [N] closed`.
4. When the next sprint starts: its `status: "active"` with `start_date` and `end_date`, in one
   commit. At most one sprint is `active`; none is valid between a close and the next start.

### 15.9 Change Request (CR) — with RIB Delta Engine

**Mandatory flow (v7.0+):**
1. PM describes the change in KStudio.
2. **RIB Delta Engine** produces impact report (read-only analysis).
3. PM + Dev Lead both sign after reading the RIB report.
4. Epic & Task Agent receives `cr-approved.json` and propagates cascade:
   `product.md` → `RF-XX.md` → impacted `EpicXXX.md` → impacted `Task.EpicXX.N.md` → `state.json`.
5. Dev Lead validates every file before commit.

**Cascade order is invariable** — never skip levels, never commit partial cascade.

**Prompt for Epic & Task Agent on CR:**
```
@docs/AGENTS.md @docs/.asf/architecture.json @docs/product.md

Approved Change Request: [CR description].
RIB Impact Report: [summary of impacted RF, epics, tasks].
Propagate cascade top-down:
1. Identify product.md sections to update
2. Update impacted RF-XX.md files
3. Update/create impacted EpicXXX.md
4. Regenerate impacted Task.md files

Output: complete proposal for Dev Lead review. Do not commit.
Flag every non-obvious cascade dependency explicitly.
```

### 15.10 Release

Triggered by `release-ready.json`. Documentation Agent:
1. Reads merged MRs from GitLab API.
2. Generates release notes grouped by area.
3. Creates GitLab Release with version tag.
4. Proposes updates to `deployment.md` if infra changed (Dev Lead approval required).
5. Records the release in `state.json → releases[]` (optional dashboard section, unchanged from v8.2).
6. Commits: `[agent:documentation] state.json release — v[X.Y.Z] created`.

**Retrospective — Scrum Master Agent prompt:**
```
@docs/AGENTS.md @docs/.asf/architecture.json

Retrospective Sprint [N] — [date].
Commit history: [paste git log --oneline]
Observed patterns: [list from Dev Lead]
Observed anti-patterns: [list from Dev Lead]

For each pattern: propose wording for architecture.json or layer AGENTS.md.
For each anti-pattern: propose entry for Anti-patterns block of layer AGENTS.md.
Do not modify anything — proposal for Dev Lead approval.
```

---

## 16. Artifact Formats — Templates

Every artifact file opens with a YAML frontmatter holding only the keys shown (any other key — a
`status`, an `epic`, … — is an error: `.asf/schema/frontmatter.schema.json`), and its first H1 is
exactly `# <id> — <title>` (em dash), with the frontmatter title. Statuses, priorities and
references live in `state.json`, never in the file. Folders, ids and lifecycle → `product.md` §12.
Ids below are placeholders: write the real id, which is also the file name. AC carry a bold,
progressive id (`**AC-01**`, `**AC-02**`, …); RF and Task files need at least one.

### 16.1 RF-XX.md (`requirements/`)

```markdown
---
id: RF-XX                     # RF-NN, same as the file name
title: Search projects by name
owner: Name Surname <name.surname@example.com>   # optional
---

# RF-XX — Search projects by name

## Description

[What the system must do, for whom and why — 2-4 sentences]

## Acceptance Criteria

- [ ] **AC-01** — Given [context], when [action], then [observable result]
- [ ] **AC-02** — ...
```

An RF may also exist only as a row (id and title) of the `product.md` RF index. Status and priority
→ `state.json → requirements.functional[]`; its stories → `user_stories[].rf_refs`; its epics are
those whose tasks cite it.

### 16.2 RNF-XX.md (`requirements/`)

```markdown
---
id: RNF-XX                    # RNF-NN, same as the file name
title: Project list latency
category: performance         # optional · performance | security | reliability | usability | maintainability | compliance | observability | portability | cost
metric: p95 latency of GET /projects            # optional
threshold: "< 300 ms"         # optional
verification: k6 load test in the staging pipeline, at every release   # required
owner: Name Surname <name.surname@example.com>   # optional
---

# RNF-XX — Project list latency

## Requirement

[The quality the system must keep, in 1-2 sentences]

## How it is measured

[Test, pipeline check, scan, measurement or documented review — and where its result is found]

## Scope

[Which parts of the system it constrains; what it does not cover]
```

RNFs live in `requirements/`, next to the RFs (no `nfr/` folder). Status — never `done`: it is
satisfied at a date — with `verified_by` / `verified_at` and priority → `state.json →
requirements.non_functional[]`; the epics bound to it cite it in `rnf_refs`.

### 16.3 US-XXX.md (`stories/`)

```markdown
---
id: US-XXX                    # US-NNN, same as the file name
title: Find a project quickly
actor: Project manager        # optional · the «as a …»: a role, not a person
owner: Name Surname <name.surname@example.com>   # optional
---

# US-XXX — Find a project quickly

As a [actor], I want [goal], so that [benefit].
```

No list of requirements in the file: its RFs (≥1) and priority → `state.json → user_stories[]`;
its status is derived from its RFs; the epic that delivers it cites it in `user_story_refs`.

### 16.4 EpicXXX.md (`epics/`)

```markdown
---
id: EpicXXX                   # EpicNNN, same as the file name
title: Project discovery
---

# EpicXXX — Project discovery

## Objective

[2-4 sentences: what the user can do after this epic]

## Scope

**In scope:**
- [what the epic delivers, in words]

**Out of scope:**
- [explicitly excluded features]

## Acceptance Criteria

- [ ] **AC-01** — Given [context], when [action], then [observable result]
- [ ] **AC-02** — ...

## Technical Notes

[Patterns from architecture.json, integration constraints, ADR references.]
```

Status, product priority, kind, dependencies, user stories, RNFs, tasks and the signature →
`state.json → epics[]`; its sprint and roadmap stage → their `epic_refs`. The task breakdown, the
epic's points and the RFs it covers are derived from its tasks.

### 16.5 Task.EpicXX.N.md (`tasks/`)

```markdown
---
id: Task.EpicXXX.N            # same as the file name
title: Project search endpoint
adr: [ADR-XXX]                # ADRs the task must follow — [] if none
rules: [R-XX]                 # rules (R-NN) the task must follow — [] if none
reads:                        # files to read before starting — [] if none
  - docs/.asf/architecture.json
  - be/app/projects/service.py
---

# Task.EpicXXX.N — Project search endpoint

## Context

[1-2 sentences: what is implemented in this atomic task, and why]

## Acceptance Criteria

- [ ] **AC-01** — Given [context], when [action], then [observable result] (`RF-XX/AC-01`)
- [ ] **AC-02** — ...

## Technical Notes

[Patterns to use, function/module to create, edge cases.]

## Prompt Seed

[1. Exact context: "Implement service X that does Y"]
[2. Explicit constraints: "Use Repository pattern."]
[3. Expected output: "Produces: file be/app/services/X.py"]
[4. Expected tests: "Tests in be/tests/unit/test_X.py — coverage of 3 AC"]

DoD: the checklist of §15.4bis — verified on the MR, not ticked in this file.
```

Status, points, `rf_refs`, `bug_refs`, `depends_on` and `files` → `state.json → epics[].tasks[]`;
its epic is the one whose id starts its own. An AC that implements an RF acceptance criterion cites
it as `` `RF-NN/AC-NN` ``, and that RF must be in the task's `rf_refs`.

### 16.6 BUG-XXX.md (`bugs/`)

```markdown
---
id: BUG-XXX                   # BUG-NNN, same as the file name
title: Archived projects appear in the project list
area: [fe, be]                # optional · layers where it shows: fe | be | api | core | worker | deployer | notify | infra | docs
found_in: v0.4.1 on staging   # optional · release, environment or commit that reproduces it
reported_by: Name Surname <name.surname@example.com>   # optional
reported_at: 2026-10-01       # optional · YYYY-MM-DD
regression_test: be/tests/integration/test_projects.py::test_archived_hidden   # optional · fails before the fix, passes after
---

# BUG-XXX — Archived projects appear in the project list

## Symptom

[What happens, and the steps that reproduce it]

## Cause

[Root cause, once known]

## Expected behaviour

[What should happen instead]

## Regression test

[The test that fails before the fix and passes after it]
```

Status, severity, the RFs/RNFs it breaks (`rf_refs`, `rnf_refs`, set when it is reported) and
`duplicate_of` → `state.json → bugs[]`. It enters an epic through the task that fixes it
(`bug_refs`); its points are those of the fixing tasks.

### 16.7 Release Notes (Documentation Agent)

```markdown
# Release [vX.Y.Z] — Sprint [N]

**Date:** [YYYY-MM-DD]
**Environment:** staging
**Sprint:** [N] · [start date] → [end date]

## What's New

### Frontend
- [#NNN] [MR title] — [1-line description]

### Backend
- [#NNN] [MR title] — [1-line description]

### Infrastructure
- [#NNN] [MR title] — [1 line]

## Bug Fixes
- [#NNN] [MR title]

## Sprint Metrics
- Story points: [N] done of [M] planned — read from state.json when this file is written (derived)
- MRs merged: [N]
- Velocity at release: [N] pts, read from state.json when this file is written (derived; the final velocity can still rise)

## Links
- Staging: [URL]
- GitLab Release: [URL]
```

### 16.8 Retrospective Summary (Scrum Master Agent)

```markdown
# Retrospective — Sprint [N] · [YYYY-WW]

**Sprint closed:** [YYYY-MM-DD]
**Velocity at closure:** [N] pts, read from state.json when this file is written (derived; the final velocity can still rise)
**Issues completed:** [N] / [N]
**Issues rolled over:** [N]

## Sprint Summary
[3-5 sentences: facts from commit history and MR comments only]

## Observed Patterns
- [pattern 1]: [evidence]

## Observed Anti-Patterns
- [anti-pattern 1]: [evidence]

## Blockers Detected
- Issue #[NNN]: stalled [N] hours — cause: [if derivable]

## Recommendations for Next Sprint
- [recommendation 1]

---
*Generated by Scrum Master Agent. Pattern promotion requires Dev Lead deliberation.*
```

---

## 17. Label System ASF™ & GitLab Boards

> Per ASF™ Operating Model §10.3. Labels are defined at GitLab Group level,
> cascadano automaticamente su tutti i repository figli.

### 17.1 Label taxonomy

#### status:: (scoped — mutually exclusive)

| Label | Color HEX | Uso |
|---|---|---|
| `status::to-do` | `#6B6B6B` | Issue da iniziare |
| `status::in-progress` | `#185FA5` | Lavoro attivo |
| `status::in-review` | `#BFBF09` | MR aperta, in attesa di review |
| `status::done` | `#0F6E56` | Completata e chiusa |
| `status::blocked` | `#BF0025` | Bloccata — richiede intervento |
| `status::triage` | `#B85C00` | Reported, not yet qualified |

#### priority:: (scoped — mutually exclusive)

| Label | Color HEX | Uso |
|---|---|---|
| `priority::now` | `#BF0025` | Da fare nello sprint corrente |
| `priority::next` | `#B85C00` | Queued for the next sprint |
| `priority::later` | `#6B6B6B` | Unprioritised backlog |

#### type:: (scoped — mutually exclusive)

| Label | Color HEX | Uso |
|---|---|---|
| `type::feature` | `#185FA5` | Nuova funzionalità |
| `type::bug` | `#BF0025` | Difetto da correggere |
| `type::maintenance` | `#6B6B6B` | Refactoring, aggiornamento dipendenze |
| `type::research` | `#534AB7` | Spike tecnico o analisi |

#### area (NON scoped — un'issue può avere più area)

| Label | Color HEX | Uso |
|---|---|---|
| `area::fe` | `#185FA5` | Componente frontend |
| `area::be` | `#0F6E56` | Componente backend |
| `area::api` | `#534AB7` | Contratti API / OpenAPI |
| `area::infra` | `#B85C00` | Infrastruttura e DevOps |
| `area::docs` | `#BFBF09` | Documentazione e Prompt Stack |

#### agent:: (NON scoped — apposta dall'agente all'intervento, mai manualmente)

| Label | Color HEX | Uso |
|---|---|---|
| `agent::epic-task` | `#534AB7` | Issue generata da Epic & Task Agent |
| `agent::scrum-master` | `#0F6E56` | Aggiornata da Scrum Master Agent |
| `agent::infra` | `#B85C00` | Gestita da Infrastructure Agent |
| `agent::documentation` | `#BFBF09` | Prodotta da Documentation Agent |
| `agent::test` | `#185FA5` | Generata da Test Generation Agent |

### 17.2 Le quattro bacheche ASF™

Created by the Infrastructure Agent at bootstrap Block ③, at Group level.

| Board | Type | Columns | Who uses it |
|---|---|---|---|
| **Release Planning** | Epic Board | `priority::later` → `priority::next` → `priority::now` | PM durante Backlog Refinement |
| **Sprint Board** | Issue Board (filtro: Iteration corrente) | `status::to-do` → `status::in-progress` → `status::in-review` → `status::acceptance` → `status::done` \| `status::blocked` | Team durante Sprint Execution |
| **Sprint Planning** | Issue Board (filtro: no Iteration) | `priority::later` → `priority::next` → `priority::now` | PM + Dev Lead durante Sprint Planning |
| **Agent Monitor** | Issue Board (no filtro) | `agent::epic-task` \| `agent::scrum-master` \| `agent::test` \| `agent::documentation` \| `agent::infra` | Dev Lead per audit attività agenti |

### 17.3 Iteration configuration

| Parametro | Valore |
|---|---|
| Durata | 1 settimana |
| Rollover automatico | Attivo — Issues incomplete riassegnate alla successiva |
| Iterations future pre-create | 4 |
| Scheduling automatico | Abilitato |
| Target per sprint | 4–10 stories, capacity based on the velocity of the last 3 sprints |

---

## 18. Layer instructions & layer AGENTS.md loader

> **Change from earlier versions:** layer-specific rules no longer live inside the application
> repository's `AGENTS.md`, where they duplicated and drifted. They live in one governed place:
> `docs/instructions/<layer>.md`. The repository's `AGENTS.md` becomes a **thin loader**.

### 18.1 Single source — `docs/instructions/<layer>.md`

Each application layer has its own file, `docs/instructions/<layer>.md` (`<layer>` = `fe`, `be`,
`api`). Owner: **Dev Lead** (L1, gated). Updated **at the end of every epic**
(the same cadence as `product.md`) as rules and patterns emerge. Seven sections:

```markdown
## Stack           # framework, language, versions, entry point, build/test
## Architecture    # patterns of this layer
## Conventions     # naming, file structure, imports — layer-specific, not general
## Domain rules    # rules generated code must NEVER violate (the most critical section)
## Patterns to use # approved patterns, with examples
## Anti-patterns   # recurring mistakes to avoid
## Cross-layer refs # pointers to @docs/.asf/architecture.json, ADRs, related repositories
```

Rules are not re-argued: when one comes from an ADR, state it imperatively with the reference
(e.g. "NEVER a raw socket — only through socket-proxy, see ADR-XXX").

### 18.2 Thin loader — `<layer>/AGENTS.md`

Every application repository (`fe/`, `be/`, `api/`) carries an `AGENTS.md` that the agent loads
automatically when working there. **It holds no rules: it points.** Template:

```markdown
# AGENTS.md — <layer> (L0.5 loader)
> Authority: @docs/AGENTS.md (L0) · @docs/instructions.md + @docs/instructions/<layer>.md (layer rules).
> Load these before operating on <layer>/. This file does not duplicate them: it points to the single source.
```

**Why:** one governed source of rules (in `docs`, L1), no duplication, isolation per layer, and a
repository file that stays a stable pointer.
