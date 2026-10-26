<!-- ASF method as installed by KStudio (state.json schema 1.x, ADR-020). Use it until KStudio adopts state.json 2.0.0. Sections keep their canonical numbers. -->

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
| **Startup** | PM, Dev Lead, Infrastructure Agent | Project bootstrapped, GitLab configured, `state.json` initialized, Quality Gate L1 signed |
| **Planning** | PM, Dev Lead, Epic & Task Agent | `EpicXXX.md`, `Task.EpicXX.N.md`, `state.json` updated, GitLab Issues created |
| **Sprint Execution** | Developer Senior, Code Gen Agent, Code Review Agent, Test Gen Agent, QA Lead | Code committed, MRs merged, `state.json` updated task by task |
| **Sprint Review** | PM, Dev Lead, Documentation Agent, cliente | Demo su staging, release notes, Roadmap.md aggiornato |
| **Retrospective** | Dev Lead, Developer Senior, QA Lead, Scrum Master Agent | Pattern promotion, Prompt Stack updated |
| **Release** | Documentation Agent, Dev Lead | Release notes, GitLab Release tag, `state.json.release` updated |

### 15.2 Startup phase

1. PM configures project in KStudio (GitLab URL, PAT, group, project name).
2. KStudio BE bootstraps `docs/` with all L1 template files, initializes `state.json`.
3. PM fills and signs `docs/product.md` (Block ①).
4. PM builds `Roadmap.md` and `ProductLog.md`. Epic & Task Agent supports first epic generation (Block ②).
5. Dev Lead initializes `architecture.json`, `deployment.md`, `instructions.md`, and AGENTS.md per layer (Block ③).
   It must include at least one completed ADR in `architecture.json → adLog[]` (not an empty
   placeholder) — a precondition for certifying point 1 of Quality Gate Layer 1.
6. Dev Lead signs **Quality Gate Layer 1** (see AGENTS.md §1).
7. PM commits `infra-bootstrap.json` to trigger Infrastructure Agent (v1.0+).

### 15.3 Planning — from RF to Epic to Task

**Pre-condition:** Quality Gate Layer 1 must be signed. `docs/product.md` must be PM-signed and complete for the sprint scope.

1. PM selects epic candidates from `docs/ProductLog.md`.
2. Dev Lead reviews technical feasibility against `docs/.asf/architecture.json`.
3. PM opens gate `epic-ready` → KStudio BE commits `docs/triggers/epic-ready.json`.
4. Epic & Task Agent reads L0 + L1, generates `EpicXXX.md` per approved epic.
5. Agent decomposes each epic into atomic tasks → generates `Task.EpicXX.N.md`.
6. Agent updates `state.json`: `epics[]`, `tasks[]`, `sprint.issues.todo[]`.
7. Agent commits: `[agent:epic-task] state.json + EpicXXX.md — Sprint Planning S[N]`.
8. Dev Lead reviews all files. Scrum Master Agent creates GitLab Issues from Task.md.
9. Approved → Sprint Execution starts.

**Task decomposition rules:**
- 1 task = 1 layer (fe OR be OR api OR docs)
- 1 task = 1 cohesive responsibility
- Story points: Fibonacci 1/2/3/5/8 — split if >8
- AC in BDD format — granular enough for Test Generation Agent

**Prompt for Epic & Task Agent (Sprint Planning):**
```
@docs/AGENTS.md @docs/.asf/architecture.json @docs/product.md @docs/ProductLog.md

Sprint Planning — [date].
Epic candidates: [list from ProductLog.md].
For each approved epic generate:
1. docs/epics/EpicXXX.md — complete with objective, scope, AC, dependencies
2. docs/tasks/Task.EpicXX.N.md — per atomic task with BDD AC and prompt seed

Do not commit. Output as proposal for Dev Lead review.
```

### 15.4 Developing an Epic

Work task by task, in dependency order. **Use the "Develop EpicXXX" command (AGENTS.md §4) as the mandatory entry point.**

**Before starting any task:**
1. Leggi `state.json` → estrai RF collegati all'epica.
2. Resolve every RF: `docs/requirements/RF-XX.md` (fallback: `docs/product.md`). A missing RF is a blocking error.
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

**Every task completion requires these updates in the same commit — never deferred:**

1. `state.json → tasks[]`: set `status: "done"`.
2. `state.json → epics[]`: increment `tasks_done`. If `tasks_done == tasks_total` → **do not set `state: "done"` yet** — see epic validation gate below.
3. `state.json → milestones[]`: recalculate `epics_done`.
4. `state.json → meta`: update `updated_at` (ISO) and `updated_by`.
5. `docs/tasks/Task.EpicXX.N.md`: mark AC as `[x]`, set `**Status**` to `✅ done`.

**Epic validation gate — mandatory before setting `epics[].state: "done"`:**

When `tasks_done == tasks_total`:
1. Developer Senior verifies all epic-level AC satisfied.
2. Developer Senior confirms all tests pass.
3. Developer Senior confirms last task MR has Dev Lead approval.
4. Only then: set `epics[].state = "done"`, `validated_by = "<human name>"`, `validated_at = "<ISO>"`.

`validated_by` must be a human name — never `"agent:*"`.

### 15.6 MD ↔ state.json alignment — invariants

| Target | What to update |
|---|---|
| `state.json → requirements.sections[].requirements[]` | `status: "done"` for every implemented RF |
| `state.json → epics[]` | `tasks_done` incremented; `state: "done"` if complete |
| `state.json → milestones[]` | `epics_done` recalculated |
| `state.json → meta` | `updated_at`, `updated_by` |
| `docs/requirements/RF-XX.md` | `**Status:** done`, AC marked `[x]` |
| `docs/product.md` | RF status updated (add `✅`) |
| `docs/epics/EpicXXX.md` | `**Status:** done`, AC marked `[x]` when epic complete |
| `docs/tasks/Task.EpicXX.N.md` | AC marked `[x]`, `**Status**` → `✅ done` |
| `state.json → bugs.items[]` (v8.3) | `status` moved, `resolved_at` set, `task_refs[]` naming the task that fixed it |
| `state.json → user_stories.items[]` (v8.3) | `status` recomputed from the RF it points to — derived, never typed in |
| `state.json → nfrs.items[]` (v8.3) | `status`, `verified_at`, `verified_by` after a verification run. Never `done` |
| `docs/bugs/BUG-NNN.md` (v8.3) | `status: done` only with the regression test named in the file |
| `docs/requirements/RNF-NNN.md` (v8.3) | `status` and `verified_at` after each verification — including back to `violated` |

**Conflict resolution priority:** `state.json` > `product.md` > `RF-XX.md` > `EpicXXX.md`.

> **v8.3 — why that order is not a convention.** `state.json` is the **source of truth** for the state of the workspace, not a projection of the markdown (`@docs/product.md §12.1`, D-8.16). The markdown is where an artifact is authored and argued; the state file is where its status lives. Where they disagree the markdown is what gets corrected, and an agent reading a status anywhere else is reading a copy.

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
1. Generates `docs/retro/YYYY-WW.md`.
2. Updates `state.json`: closes sprint, records velocity, rolls over incomplete issues.
3. Commits: `[agent:scrum-master] state.json — sprint [N] closed`.

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
5. Updates `state.json.release`.
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

### 15.11 Bugs, stories and non-functional requirements — where they enter the cycle (v8.3)

> Definitions and the rules that govern them → `@docs/product.md §12.2bis–§12.2quater`.
> Templates → §16.5, §16.6, §16.7 below.

**A bug, from report to closed.**

1. **Report.** Anyone using the product reports a defect. It is written as `docs/bugs/BUG-NNN.md` with `status: triage`, a severity proposed by the reporter, and `found_in` — the release, environment or commit where it was seen. Without that field nobody else can reproduce it.
2. **Triage** (Dev Lead, at the latest at the next planning). Reproduce it. Confirm or change the severity. Then one of four outcomes: it enters the **container epic of the current sprint** with points and `status: todo`; or it closes as `not_reproducible`, `wont_fix` or `duplicate` — each of those is an outcome, written down with its reason, not a bug left open forever.
3. **The container epic.** One per sprint, `kind: container`, opened at Sprint Planning and closed at Sprint Closure like any other. It collects the bugs found in that sprint and **no functional requirement**. The bug is never attached to the epic that introduced it: that epic is delivered, and rewriting it hides the delivery that happened.
4. **Fix.** A task in the container epic, with `bugs: [BUG-NNN]` in its frontmatter and no requirement. Its first acceptance criterion is the **regression test**: it fails before the fix and passes after it.
5. **Close.** `status: done` only when the regression test is named in the bug file and green. Points count in the sprint velocity — see the note below.

**Bugs and velocity.** Bug points are counted in `velocity_history[]` like every other point. A team that excludes them reports a velocity that does not match the week it spent, and plans the next sprint against a number that was never real. Reporting them separately from feature points is fine and useful; not counting them is not.

**A user story.** The PM writes `docs/stories/US-NNN.md` before or during Planning, and it must point at **at least one** `RF-XX` — that is what turns a need into something the factory can build and test. The epic's «User story» section then lists references (`→ US-001, US-002`), and the story text lives in one place only.

**A non-functional requirement.** Declared once, in `docs/requirements/RNF-NNN.md`. It is system-wide unless an epic claims it in its `rnf_refs` — scope is that reference, not a frontmatter field. It is **verified, not completed**: every verification run writes `status` and `verified_at` (in `state.json`), and a run that finds it `violated` opens a `BUG-NNN` — it does not reopen the epic delivered under it and does not change the requirement. A system-wide RNF is part of the DoD of every task that could break it, which is why §15.4bis lists it below.

**DoD additions (v8.3), on top of §15.4bis:**

- [ ] If the task fixes a bug: the regression test exists, is named in `BUG-NNN.md`, and fails without the fix
- [ ] No system-scope `RNF` moved to `violated` by this change — and if one did, the bug is open before the MR

---

## 16. Artifact Formats — Templates

> **Two template styles, told apart (v8.3).** The artifacts introduced in v8.3 — `BUG-NNN.md`,
> `US-NNN.md`, `RNF-NNN.md` — are authored with **YAML frontmatter**, validated against
> `.asf/schema/frontmatter.schema.json`, because that frontmatter is what the projector reads into
> `state.json`. The older header-block templates below are unchanged and stay valid: a project
> writes epics and tasks the way it already writes them. Where a project has adopted frontmatter
> for those too, the schema has a `$def` for each.

### 16.1 EpicXXX.md

```markdown
# Epic[NNN] — [Epic Title]

**ID**: Epic[NNN]
**Milestone**: [vX.Y] — [Milestone title]
**Sprint**: [N] (planned)
**Status**: 🟡 planned
**Validated by**: —
**Area**: [fe · be · docs · infra]
**RF covered**: [RF-XX, RF-YY]
**Dependencies**: [Epic001, Epic002 or "none"]

---

## Objective

[2-4 sentences: what the user can do after this epic]

## User story

<!-- v8.3: references, never copies. The story lives in docs/stories/US-NNN.md. -->
- US-001 — [story title] → RF-XX, RF-YY
- US-002 — [story title] → RF-ZZ

## Scope

**In scope:**
- RF-XX — [titolo requirement]
- RF-YY — [titolo requirement]

**Non-functional (v8.3):**
- RNF-NNN — [title] (claimed in this epic's `rnf_refs`) · system-wide RNF apply here too and are not listed epic by epic

**Out of scope:**
- [explicitly excluded features]

<!-- v8.3, container epic only (kind: container, one per sprint): replaces the sections above.
## Bugs collected
| Bug | Severity | Status | Pts | Fixed by |
|---|---|---|---|---|
| BUG-001 | critical | done | 3 | Task.EpicNNN.2 |
-->


## Acceptance Criteria

- AC-01: [Given X, when Y, then Z — BDD format]
- AC-02: ...

## Technical Notes

[Patterns from architecture.json, integration constraints, ADR references.]

## Task Breakdown

| Task | File | Estimate (pts) |
|---|---|---|
| Task.EpicNNN.1 | docs/tasks/Task.EpicNNN.1.md | [pts] |
```

### 16.2 Task.EpicXX.N.md

```markdown
# Task.Epic[NNN].[N] — [Task Title]

**ID**: Task.Epic[NNN].[N]
**Epic**: Epic[NNN] — [epic title]
**Sprint**: [N]
**Pts**: [1 / 2 / 3 / 5 / 8]
**Status**: 🔲 todo
**Assignee**: —
**Issue GitLab**: —

---

## Description

[1-2 sentences: what is implemented in this atomic task]

## Acceptance Criteria

- AC-01: [Given X, when Y, then Z]
- AC-02: ...

## Technical Notes

[Patterns to use, function/module to create, edge cases.]

## Dependencies

- Blocks: [Task.EpicNNN.M]
- Blocked by: [Task.EpicNNN.K]

## Prompt Seed

[1. Exact context: "Implement service X that does Y"]
[2. Explicit constraints: "Use Repository pattern."]
[3. Expected output: "Produces: file be/app/services/X.py"]
[4. Expected tests: "Tests in be/tests/unit/test_X.py — coverage of 3 AC"]

## DoD (Definition of Done)

- [ ] Code implemented and buildable
- [ ] Tests written and green (AC coverage)
- [ ] TypeScript typecheck / mypy clean
- [ ] SAST/DAST clean
- [ ] MR opened with description
- [ ] Code Review Agent comments resolved
- [ ] Dev Lead approve
```

### 16.3 Release Notes (Documentation Agent)

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
- Story points completed: [N] / [target]
- MRs merged: [N]
- Velocity: [N] pts

## Links
- Staging: [URL]
- GitLab Release: [URL]
```

### 16.4 Retrospective Summary (Scrum Master Agent)

```markdown
# Retrospective — Sprint [N] · [YYYY-WW]

**Sprint closed:** [YYYY-MM-DD]
**Actual velocity:** [N] pts / [N] target
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

### 16.5 BUG-NNN.md (v8.3)

`docs/bugs/BUG-NNN.md` · frontmatter `$defs/bug` · id `^BUG-[0-9]{2,3}$`. `status`, `severity`, `points`, `rf_refs` and the container epic live in `state.json` → `bugs[]`, not in the frontmatter.

````markdown
---
id: BUG-NNN
title: "[what fails, from the user's side — not the cause]"
area: [be]
found_in: "v0.4.2 · staging · commit a1b2c3d"
reported_by: "[name or role]"
reported_at: YYYY-MM-DD
regression_test: "[path::test name — fill it when the fix is written]"
---

# BUG-NNN — [title]

## Symptom

[What the user sees. Observable facts: what was done, what happened, what was expected.
Screenshots and logs go here. No hypotheses — they belong in Cause.]

## Reproduction

1. [step]
2. [step]
3. **Observed:** [wrong behaviour] · **Expected:** [correct behaviour]

**Frequency:** always / intermittent (N times out of M) / once

## Cause

[Filled at triage or at the fix, not at the report. If it is still unknown, say so —
an empty section is honest, a guessed cause sends the fix to the wrong place.]

## Acceptance criteria

- **AC-01** — Given [context], when [action], then [correct behaviour]
- **AC-02** — The regression test `[name]` fails on the commit before the fix and passes on it

## Impact

[Who is affected and how much. This is what severity is argued from.]

## Notes

<!-- For not_reproducible: what was tried, in what environment, and for how long.
     For wont_fix: the Dev Lead decision, its date and its reason.
     For duplicate: duplicate_of, and nothing else. -->
````

### 16.6 US-NNN.md (v8.3)

`docs/stories/US-NNN.md` · frontmatter `$defs/us` · id `^US-[0-9]{2,3}$`. `status` (derived from its RFs), `rf_refs` (at least one) and `priority` live in `state.json` → `user_stories[]`, not in the frontmatter.

````markdown
---
id: US-NNN
title: "[the need in one line]"
actor: "[role — who has the need]"
owner: "[PM]"
---

# US-NNN — [title]

**As** [actor] **I want** [what] **so that** [why].

## Context

[Where the need comes from: the pitch, the review, the support call. Keep the words the
person used — that is the part a requirement cannot carry.]

## Satisfied by

| RF | Title | Status |
|---|---|---|
| RF-XX | [title] | todo |
| RF-YY | [title] | todo |

> The story is the need; the requirement is the verifiable behaviour. Acceptance criteria live
> in the RF, not here — a story with its own AC is a requirement wearing a story's clothes.

## Out of this story

- [what the person asked for that is a different story, named]
````

### 16.7 RNF-NNN.md (v8.3)

`docs/requirements/RNF-NNN.md` · frontmatter `$defs/rnf` · id `^RNF-[0-9]{2,3}$`. `status`, `priority`, `verified_by`/`verified_at` live in `state.json` → `requirements.non_functional[]`; scope is which epics cite it in `epics[].rnf_refs`, not a field.

````markdown
---
id: RNF-NNN
title: "[the quality, stated as a constraint]"
category: security
metric: "[what is measured]"
threshold: "[the value that separates satisfied from violated]"
verification: "[the test, scan, check or measurement that establishes it]"
owner: "[Dev Lead]"
---

# RNF-NNN — [title]

## Requirement

[One paragraph. What must hold, always, for it to be satisfied.]

## Why

[What breaks, and for whom, if it does not hold. A non-functional requirement without this
is a preference, and it will lose every argument against a deadline.]

## Verification

**How:** [the check, by name and location — a pipeline job, a test, a scan, a measurement]
**When:** [on every commit · nightly · per release · on demand]
**Evidence:** [where the result is read]

## Verification log

| Date | Status | Measured | By | Note |
|---|---|---|---|---|
| YYYY-MM-DD | satisfied | [value] | [who] | — |

> A requirement that was satisfied and is now violated is not a mistake in the requirement.
> Record the change here, open a `BUG-NNN`, and leave this file's text alone.

## Waiver

<!-- Only for status: waived. Dev Lead, date, reason, and what would make it satisfied again. -->
````

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

#### severity:: (scoped — mutually exclusive · v8.3, on bug issues only)

| Label | Color HEX | Use |
|---|---|---|
| `severity::blocker` | `#8C0019` | The product is unusable, or data is lost |
| `severity::critical` | `#BF0025` | A main flow is broken, with no workaround |
| `severity::major` | `#B85C00` | An important function is degraded; a workaround exists |
| `severity::minor` | `#BFBF09` | Limited defect, the user carries on |
| `severity::trivial` | `#6B6B6B` | Cosmetic |

> `severity::` says **how much it costs**, `priority::` says **when it is corrected**: two
> different scales, and a bug issue carries both. A bug issue links its `BUG-NNN.md` in the
> description, exactly as a task issue links its `Task.EpicXX.N.md`.

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

Each application layer has its own file: `docs/instructions/fe.md`, `docs/instructions/be.md`,
`docs/instructions/api.md`. Owner: **Dev Lead** (L1, gated). Updated **at the end of every epic**
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
(e.g. "NEVER a raw socket — only through socket-proxy, see ADR-001").

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
