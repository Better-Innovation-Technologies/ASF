# product.md — {project_name}

> **ASF v8.5** · 2026-10-17 · _Attachments on every artifact_ · Francesco Bellifemine

> **Layer L1 · Owner: PM (Dev Lead gate)**
> The product identity document — the first source of truth for AI agents and the ASF™ team.
> Changes require a PM signature and a Dev Lead gate before any agent proceeds.
> **The history of the product is the history of the commits on this file.**
>
> **RF resolution rule (agents — mandatory):**
> 1. Load `docs/requirements/RF-XX.md` (the individual file, with full AC — v0.4+).
> 2. If not found → fall back to the entry in `docs/product.md` (this file).
> 3. If neither source holds the RF → raise an explicit error. Never proceed on incomplete context.
>
> The status and the priority of an RF are only in `docs/.asf/state.json` (§12.1): the files hold its text.

**Project:** {project_name}
**Client:** {client}
**Owner:** {dev_lead} — Better Innovation Technologies S.r.l.
**Version:** 0.1 — Bootstrap
**Date:** {bootstrap_date}
**Status:** Being defined — Startup in progress

---

## Attachment index

| Folder | Contents |
|---|---|
| `docs/requirements/functional-analysis/` | User flows, per-module specifications |
| `docs/requirements/architecture/` | System diagrams — ADRs are not here: the ADR log is `adLog[]` in `docs/.asf/architecture.json`, with optional `docs/decisions/ADR-XXX.md` files |
| `docs/requirements/ux/` | Wireframes, HTML proofs of concept, Figma prototypes |

---

## 1. Product vision

*(to be completed with the PM during Startup — block ①)*

**Problem:** [what problem the product solves — one or two sentences, from the user's point of view]

**Solution:** [how the product solves it — what the system does, for whom, why now]

**Value proposition:** [the main benefit that sets this product apart from the alternatives]

---

## 2. Target user

*(to be completed with the PM during Startup — block ①)*

### Primary user

| Field | Value |
|---|---|
| **Role** | [e.g. Operations Manager, Campaign Manager, Respondent] |
| **Primary need** | [the action they want to complete] |
| **Context of use** | [where and how they use the product] |
| **Main pain point** | [what slows them down today, without the product] |

### Secondary stakeholders

| Stakeholder | Role | Primary need |
|---|---|---|
| | | |

---

## 3. Look & feel

*(to be completed with the PM / UX during Startup, before Quality Gate Layer 1)*

**Tone:** [e.g. professional and direct / friendly and simple / technical and precise]

**Visual references:** [products or brands to draw on — e.g. "Notion for simplicity, Linear for information density"]

**Brand constraints:** [colours, typefaces, logo — whether inherited from the client or from the BIT brand]

**Priority devices:** [Desktop first / Mobile first / equally responsive]

**Accessibility:** [target WCAG level: AA / AAA]

---

## 4. Core flows

*(to be completed with the PM during Startup — describe the 3 to 5 most critical user flows)*

### Flow 1 — [name of the main flow]

1. [step 1]
2. [step 2]
3. [step 3]

### Flow 2 — [name]

1. [step 1]
2. [step 2]

*(add a Flow N section for each critical flow)*

---

## 5. Context and purpose

*(to be completed with the PM during Startup — block ①)*

Describe: what the system does, for whom, which problem it solves, and why now.

---

## 6. Stakeholder needs

*(to be completed with the PM during Startup — block ①)*

| Stakeholder | Role | Primary need |
|---|---|---|
| | | |

---

## 7. Functional requirements

*(to be completed with the PM — section by section, iterating with the stakeholders)*

This section is the **RF index**, signed by the PM: it lists exactly the RFs of `docs/.asf/state.json` `requirements.functional[]` — one row each, with id and title, nothing else (no status, no priority). Description and AC are in `docs/requirements/RF-XX.md`; an RF without a file has only its row here (§12.4). Group the rows by module, one subsection each.

### 7.1 [Module / functional area]

| RF | Title |
|---|---|
| RF-XX | [requirement title — the behaviour, in a few words] |

---

## 8. Non-functional requirements

*(to be completed before Quality Gate Layer 1)*

Each non-functional requirement stated here becomes an `RNF-NN`, with its file in `docs/requirements/` (category, metric, threshold, verification) and its status in `state.json` `requirements.non_functional[]` (§12.4).

**Performance:** [expected response times, throughput, SLA]

**Security:** [authentication, authorisation, data residency]

**Scalability:** [concurrent users, data volumes, peaks]

**Availability:** [uptime target, RTO, RPO]

---

## 9. Technical constraints

*(to be completed with the Dev Lead during Startup)*

- Technology stack: {tech_stack}
- Cloud provider: {cloud_provider}
- Environments: {namespaces}
- Integration constraints: [existing systems to interface with]
- Regulatory / compliance constraints: [GDPR, NIS2, sector-specific]

---

## 10. Out of scope

*(state explicitly what is NOT in scope for this version)*

- [excluded capability 1]
- [excluded capability 2]

---

## 11. Open issues

| ID | Priority | Question | Owner |
|---|---|---|---|
| OI-001 | HIGH | Requirements gathering to be completed with stakeholders | PM |

---

## 12. ASF™ Process Model — Concepts

> This section defines the vocabulary and the rules of the ASF™ process model.
> Every agent that operates on requirements, epics, tasks, bugs, stories, sprints or releases must know these concepts.
> For the detailed operational workflow → `@docs/instructions.md §15. Sprint Execution`; for the templates of the artifact files → `@docs/instructions.md §16`.

### 12.1 state.json — single source of truth

`docs/.asf/state.json` is the **single source of the project state** and the contract between KStudio and all CI agents. It holds statuses, planning decisions, references and signatures; the `.md` artifacts hold only text (titles, descriptions, AC).

- **One fact, one place.** Nothing is copied between `state.json` and the `.md` files: a status, a reference or a priority exists only in `state.json`; a title, a description or an AC only in the `.md`. There are no precedence rules about statuses between `state.json`, `product.md`, `RF-XX.md` and `EpicXXX.md`: there is one source (conflicts of text still follow the layer hierarchy).
- **What can be derived is not stored** (§12.2) — counters, totals, velocities, progress, dates of changes, file paths.
- **Each reference is stored once, by the side that receives it:** the sprint lists its epics, the roadmap stage its epics, the epic its stories and RNFs, the task its RFs and bugs, the story its RFs, the bug the RFs and RNFs it breaks. What exists only inside something lives inside it: tasks live inside their epic.
- **Who changed what and when is git.** The file has no timestamps or authors other than signatures (§12.13).
- **Agents write it** — each agent writes only its own section. All writes use read-SHA → mutate → commit-with-SHA-verify (**Double Bifurcation**) to prevent race conditions.
- **Tools that show or edit the state (KStudio)** keep at most an exact cache of `state.json` and write only through commits to it. Operational data that is not part of the state (e.g. who works on an epic) stays in the tool, never in `state.json`.

**Schema and versioning.** `.asf/schema/state.schema.json` is the contract, written in the standard: backend models, TypeScript types and Pydantic models follow it, and if a tool and the schema disagree, the tool is wrong. `state.json` declares `"$schema": "schema/state.schema.json"`; `meta.schema_version` must be a version the schema accepts — current **2.0.0** (ASF 8.3). The schema version is semver: an addition bumps the minor, a breaking change bumps the major and ships a migration script. No top-level key is added or dropped without a schema change (Dev Lead gate). The schema is **strict**: a key it does not list is an error, and an optional array is absent rather than empty (every array, when present, has at least one item). The rules across entries and files that the schema cannot express are checked by `tools/validate-stack.py` (§12.3); the validation rule for agents is in `AGENTS.md` (JSON contracts & validation).

**Sections** (`*` = required):

| Section | Fields | Rules |
|---|---|---|
| `meta`* | `schema_version`*, `asf_version`* | `schema_version`: the schema's own version (`2.0.0`). `asf_version`: the ASF version the project follows (`8.3`); it changes only with an adoption. |
| `project`* | `name`*, `repos` | `repos`: clonable git URLs (`https://host/path[.git]` or `git@host:path[.git]`), never with credentials; the repo name is the last URL segment without `.git`, unique. Environments are not here: they live in `infra/environments/<env>/` (`deployment.md`). |
| `prompt_stack[]` | `filename`*, `validated_by`, `validated_at` | One entry per L0/L1 file, path relative to the docs repo root (no leading `/`, no `..`), file must exist; signature fields always together (§12.13). ADRs are never here. |
| `sprints[]` | `id`*, `status`*, `start_date`, `end_date`, `closed_on`, `goal`, `epic_refs` | §12.10. |
| `roadmap[]` | `id`*, `title`*, `start_date`, `end_date`, `epic_refs` | §12.11. |
| `epics[]`* | `id`*, `status`*, `product_priority`, `kind`, `depends_on`, `user_story_refs`, `rnf_refs`, `validated_by`, `validated_at`, `tasks`* | At least one epic. §12.6. |
| `epics[].tasks[]` | `id`*, `status`*, `points`, `rf_refs`, `bug_refs`, `depends_on`, `files` | At least one per epic. §12.7. |
| `requirements`* | `functional`*`[]` `{id*, status*, priority}`, `non_functional[]` `{id*, status*, verified_at, verified_by, priority}` | At least one RF. §12.4. |
| `user_stories[]` | `id`*, `rf_refs`*, `priority` | §12.9. |
| `bugs[]` | `id`*, `status`*, `severity`*, `rf_refs`, `rnf_refs`, `duplicate_of` | §12.8. |
| `pipeline`, `product_log`, `alerts`, `releases`, `inbox` | as in v8.2 | Dashboard sections, optional, unchanged from v8.2; they will be revisited together with the dashboard. `pipeline.agents[]` replaces the legacy megalog MD. |

Outside the dashboard sections, no other key exists at any level.

**Values:**

| Type | Values |
|---|---|
| work_status (RF, epics, tasks) | `todo` · `in_progress` · `review` (delivered, awaiting the signature) · `done` · `blocked` |
| bug_status | every work_status, plus `triage` · `not_reproducible` · `wont_fix` · `duplicate` |
| rnf_status | `unverified` · `satisfied` · `at_risk` · `violated` · `waived` — never `done` |
| sprint_status | `planned` · `active` · `closed` |
| priority (RF, RNF, stories) | `low` · `medium` · `high` · `critical`, decided by the PM |
| `product_priority` (epics) | integer ≥ 1, decided by the PM |
| severity (bugs) | `blocker` · `critical` · `high` · `low` · `trivial` |
| points (tasks) | `1` · `2` · `3` · `5` · `8` |
| ids | `RF-NN`, `RNF-NN`, `BUG-NNN`, `US-NNN` (2–3 digits) · `EpicNNN` (3 digits) · `Task.EpicNNN.N` · sprint: integer ≥ 1 · roadmap stage: free string (e.g. `R1`) |
| dates | `YYYY-MM-DD` |
| persona (`validated_by`, `verified_by`) | `Name <email>`, as a commit author; never an agent (`agent:…`) |

### 12.2 Derived values — never stored

Computed from `state.json` and git, never written anywhere:

- **Velocity — current:** points of the `done` tasks of the active sprint's epics.
- **Velocity — target today:** points of all the tasks of the active sprint × days elapsed since `start_date` / days from `start_date` to `end_date`.
- **Burndown:** for each day of the active sprint, the points of the tasks `done` by that day, next to the target line; the day a task became `done` comes from git history.
- **Velocity — final:** points of the `done` tasks of a `closed` sprint. It is not frozen: if one of its tasks completes later, it rises. Divided by the days from `start_date` to `closed_on` it gives points per day.
- **Velocity — average:** mean of the final velocities of the **last 3 closed sprints** — this is the **planning capacity**.
- **Epic:** its points = sum of its tasks' points; its RFs = those its tasks cite (`rf_refs`); its bugs = those its tasks fix (`bug_refs`); its sprint and roadmap stage = those that list it; in no sprint = in the backlog.
- **RF and bug:** their epics = the epics of the tasks citing them; bug points = sum of the points of the tasks that fix it; when it was resolved = git.
- **User story:** its status, from its RFs.
- **Roadmap stage:** status and progress, from its dates and its epics.
- **Quality Gate L1 and signatures to renew:** from `prompt_stack[]` and git (§12.13).
- **File paths:** from the id (§12.3). **Who changed what, and when:** git.

### 12.3 Artifacts — files, frontmatter, validation

Each artifact tracked in `state.json` has one `.md` file, in one folder per kind under the docs repo root, with no subfolders: the path follows from the id.

| Artifact | File | Frontmatter (`*` = required) | Body |
|---|---|---|---|
| RF | `docs/requirements/RF-XX.md` — or only its row in the RF index (§7) | `id`*, `title`*, `owner`, `attachments`, `links` | description, BDD AC |
| RNF | `docs/requirements/RNF-XX.md` (RNF live next to the RF; there is no `nfr/` folder) | `id`*, `title`*, `category`, `metric`, `threshold`, `verification`*, `owner`, `attachments`, `links` | the requirement, how it is measured, its scope |
| Epic | `docs/epics/EpicXXX.md` | `id`*, `title`*, `attachments`, `links` | objective, scope, epic AC |
| Task | `docs/tasks/Task.EpicXXX.N.md` | `id`*, `title`*, `adr`*, `rules`*, `reads`* (lists, possibly empty), `attachments`, `links` | context, BDD AC, prompt seed |
| Bug | `docs/bugs/BUG-XXX.md` | `id`*, `title`*, `area`, `found_in`, `reported_by`, `reported_at`, `regression_test`, `attachments`, `links` | symptom, cause, expected behaviour, regression test |
| User story | `docs/stories/US-XXX.md` | `id`*, `title`*, `actor`, `owner`, `attachments`, `links` | "As a … I want … so that …" |

- RNF `category`: `performance` · `security` · `reliability` · `usability` · `maintainability` · `compliance` · `observability` · `portability` · `cost`. Bug `area`: a list of layers (`fe` · `be` · `api` · `core` · `worker` · `deployer` · `notify` · `infra` · `docs`); `reported_at` is a date. Story `actor`: a role, not a person.
- **`attachments` and `links`** (both optional, since 8.5): `attachments` cites files committed in the flat folder `docs/attachments/` — flat because one file may be cited by several artifacts — as pointers in the form `docs/attachments/<name>`, the name lower case and without spaces (the cited-path check stops at a space and would read the path truncated). No size and no media type: both are known when the file is served, and written in an artifact they would age. A mockup attached to a task is evidence for whoever writes the code, declared like the files in `reads` — an agent opens png, jpg, webp and pdf natively. Allowed extensions, a closed list: `md` `txt` `csv` `json` `yaml` `yml` `html` `css` `js` `pdf` `docx` `xlsx` `png` `jpg` `jpeg` `webp` `gif` `svg` `fig`; not archives (`zip`, `tar`, `gz`: they hide their contents from every check), not media (`mp4`, `mp3`, `wav`, `webm`: that is the object-storage class), and never git-LFS (a mirror read gets the pointer, not the file). Over 5 MB in one file is an error, about 50 MB in the folder a warning, a file nobody cites a warning (orphan). `links` holds http(s) URLs of material that lives outside — a Figma project, a Miro board — and no tool ever reaches the network to check them; a downloaded `.fig` is an ordinary attachment, while the URL of the Figma project is a `links` entry. **Neither field is in `state.json`:** both are artifact text, like the title.
- **Frontmatter is strict**, like `state.json`: any other key (a `status`, an `epic`, a `priority`…) is an error. The frontmatter `id` equals the file name; the first H1 is exactly `# <id> — <title>` (em dash).
- **No `.md` repeats state or references:** no `**Status**` or `**Layer**` lines, no `Validated by` / `Area` / `RF covered` / `Dependencies` header lines, no "RF in scope" tables, no lists of a story's requirements, no ✅ or status columns. KStudio renders the cross-references in both directions.
- **AC:** RF and Task files have at least one AC, numbered `**AC-01**`, `**AC-02**`… (unique, progressive), as checkbox lines in BDD form. The checkboxes stay: they are AC text. A task AC that implements an RF AC cites it as `` `RF-XX/AC-NN` ``, and that RF must be in the task's `rf_refs`.
- ADR and planning-archive frontmatter is otherwise unchanged: they are not in `state.json` and keep their own status. An ADR too may carry `attachments` and `links`; the planning archive may not.
- Every artifact in `state.json` has its file and every artifact file has its `state.json` entry (an RF may have only its index row).

**Validation.** `tools/validate-stack.py` (each project copies it into the `tools/` folder of its docs repo and runs it in CI) validates `state.json` and every frontmatter against their schemas, plus the cross-file rules: unique ids; every reference resolves; a task id starts with its epic id; an epic in at most one sprint and one roadmap stage; a story in at most one epic; no dependency cycles between epics or between tasks; repo names unique and every `files` glob starting with one; `prompt_stack` files exist; artifact files ↔ `state.json` entries; frontmatter `id` = file name; H1 = `# <id> — <title>`; the RF index of `product.md` = the RFs of `state.json`; every `attachments` entry flat, named and under 5 MB, with a warning for a file in `docs/attachments/` that no artifact cites, and every `links` entry an http(s) URL in shape — never opened. Usage and exit codes: `AGENTS.md` (JSON contracts & validation).

### 12.4 Requirements — RF and RNF

Functional requirements are `RF-XX`. Non-functional requirements are `RNF-XX`. Both have their files in `docs/requirements/` and their state in `state.json` `requirements`. A requirement exists even without an epic.

**RF — two-level structure:**
- `docs/product.md` §7 — the **signed index** (L1): it lists exactly the RFs of `requirements.functional[]`, id and title. PM signature required for any change (§12.13). Agents must not overwrite it. RF groups are its subsections.
- `docs/requirements/RF-XX.md` — **individual detail files** (L1.5, v0.4+): description and AC. Created by KStudio BE on RF save; updated by Epic & Task Agent on CR. An RF without a file has only its index row, which is the fallback of the RF resolution rule at the top of this file.

**RF state:** `status` (work_status) — `done` only when all its AC are implemented and tested; `priority`.

**AC format:** BDD — "Given [context], when [action], then [expected outcome]". Granular enough to generate automated tests.

**RNF:** the requirement, its metric and threshold, and how it is verified live in `docs/requirements/RNF-XX.md`; `verification` is required, because an unverifiable non-functional requirement is a wish. In `state.json` an RNF is never `done`: it is satisfied at a date. `status` (rnf_status); `verified_by` + `verified_at` (a person and the day of the last measurement, always together) are required with `satisfied`, `at_risk` and `violated`, forbidden with `unverified`, optional with `waived`; `priority`. An epic lists the RNFs all its tasks must respect in `rnf_refs`; an RNF may be in several epics or in none.

### 12.5 Change Requests (CR) — with RIB Delta Engine

A CR is a stakeholder-requested modification after planning has started. A CR is not an entry of `state.json`: its outcome is. The epics and tasks it creates or changes enter `epics[]` like any others (§12.6).

**CR flow — mandatory order (v7.0+):**
1. PM describes the change in KStudio.
2. **RIB Delta Engine** reads `product.md` (index) + impacted `RF-XX.md` files, analyzes the delta vs. current baseline, produces a **structured impact report**: impacted RF, epics to regenerate, tasks to invalidate, effort estimate in story points, architectural risks.
3. PM + Dev Lead read the RIB report and **both sign** the CR before any agent proceeds.
4. Only after double approval: Epic & Task Agent receives trigger `cr-approved.json` and propagates cascade top-down:
   `product.md` (PM signs) → impacted `RF-XX.md` → impacted `EpicXXX.md` → impacted `Task.EpicXXX.N.md` → `state.json`.
5. Dev Lead validates every updated file before commit.

**RIB Delta Engine perimeter:** read-only analysis. Never modifies Prompt Stack directly. Output is exclusively analytical — never a direct commit.

### 12.6 Epics — planning unit

An Epic is a coherent feature scope implementing one or more RFs, deliverable in a single sprint. Its text (objective, scope, epic AC) lives in `docs/epics/EpicXXX.md`; its state in `state.json` `epics[]`.

**RFs of an epic:** those its tasks cite in `rf_refs` — derived, never listed in the `.md`. Every task of an epic cites at least one RF or bug, unless the epic has `rnf_refs`.

**Fields:** `status` (work_status); `product_priority` (PM); `kind` — `feature`, or `container` for the epic that collects the tasks fixing the sprint's bugs; `depends_on` (epics to close first); `user_story_refs` (the stories it delivers; a story is in at most one epic); `rnf_refs`; `validated_by` + `validated_at`; `tasks` (§12.7).

**Status:** `todo` → `in_progress` → `review` → `done` (or `blocked`). `done` if and only if the epic is signed: `validated_by` (a person) + `validated_at`, written in the same commit as `done`, after the Developer Senior verification; neither is present before.

**Entering the plan:** an epic enters `state.json` together with its tasks (at least one), in the same commit; if it is planned in a sprint, the same commit adds its id to that sprint's `epic_refs`. An epic in no sprint is in the backlog. An epic cannot enter Sprint Execution until its tasks are generated and Dev Lead-approved.

**"Develop EpicXXX"** loads the RFs cited by the epic's tasks, its `rnf_refs`, its `user_story_refs` and the bugs in its tasks' `bug_refs`.

### 12.7 Tasks — atomic execution unit

A Task is the smallest schedulable unit. It exists only inside its epic (`epics[].tasks[]`, in number order); its text (context, BDD AC, prompt seed) lives in `docs/tasks/Task.EpicXXX.N.md`. Each task maps to exactly one layer (fe OR be OR api OR docs — never mixed).

**Task ID format:** `Task.<EpicID>.<N>` (e.g. `Task.EpicXXX.N`): it starts with the id of the epic that contains it.

**Fields:** `status` (work_status); `points`; `rf_refs` (the RFs whose AC it implements, possibly of another epic); `bug_refs` (the bugs it fixes); `depends_on` (tasks to close first); `files`.

**`files`:** the files the task expects to touch, as globs relative to the folder that holds the repos, whose first segment is the repo name (`api/core/app/**`); no leading `/`, no `..`. Two tasks with no file in common and no `depends_on` between them may run in parallel. It is a forecast: once the task is closed, its commits are the truth.

**Story points:** Fibonacci only — 1 · 2 · 3 · 5 · 8. Never other values. Split if >8.

**Split signals:** >4 distinct AC, touches >1 layer, >8 pts, prompt seed describes >1 responsibility.

**Closing a task:** in one commit, its `status` → `done` in `state.json` and its AC checked in the Task.md; nothing else (no counters: the epic's points and task counts are derived). Steps and DoD → `@docs/instructions.md §15`.

### 12.8 Bugs — defects found in use

A bug is a defect found in use, `BUG-NNN`. Its report lives in `docs/bugs/BUG-XXX.md` (symptom, cause, expected behaviour, regression test); its state in `state.json` `bugs[]`: `status` (bug_status), `severity`, `rf_refs` (the RFs it breaks), `rnf_refs` (the RNFs it violates), `duplicate_of`.

**Lifecycle:**
- **Reported:** the bug enters `bugs[]` in `triage`; the RFs and RNFs it breaks are set when it is reported, before any task exists.
- **Triage:** the severity is confirmed. The bug is then accepted (`todo`), or closed as `not_reproducible`, `wont_fix` or `duplicate` — `duplicate` if and only if `duplicate_of` names the earlier bug it duplicates.
- **Fix:** a bug exists even without an epic; it enters an epic through the task that fixes it (that task's `bug_refs`), usually in the sprint's `container` epic. It then follows the work statuses `in_progress` → `review` → `done` (or `blocked`).
- **Closure:** `done` with its regression test — the test that fails before the fix and passes after it, named in `regression_test`; a bug closed without one is closed on trust. Its points (sum of the fixing tasks) and the day it was resolved (git) are derived.

### 12.9 User stories — the need as the user tells it

A user story, `US-NNN`, is the need told by the user: "As a … I want … so that …", in `docs/stories/US-XXX.md` (with its `actor`, a role). In `state.json` `user_stories[]`: `rf_refs` — the RFs that satisfy it, at least one — and `priority`. The story has no AC of its own: they are those of its RFs.

**Lifecycle:** a story is assigned to at most one epic, which lists it in `user_story_refs`. Its status is **derived from its RFs** and never stored: it moves as its RFs move through their work statuses.

### 12.10 Sprint — time-boxed iteration

1-week sprint (compressed via AI acceleration — see ASF™ Operating Model §8.3). A sprint exists because it is declared in `state.json` `sprints[]`, and is called "Sprint <id>":

- `id` (integer ≥ 1), `status` (`planned` → `active` → `closed`), `start_date`, `end_date` (planned last day), `closed_on` (actual closing day), `goal`, `epic_refs` (its epics; an epic is in at most one sprint).
- **At most one sprint is `active`**; none is valid (before the first sprint, between a close and the next start). `active` requires `start_date` and `end_date`.
- **Closure = `closed_on`:** a sprint is `closed` if and only if it has `closed_on`. Closing is one commit: `status: closed` and `closed_on`, normally moving the unfinished epics to the next sprint's `epic_refs`; the next sprint becomes `active`, with its dates, when it starts. Nothing else is written. Steps → `@docs/instructions.md §15`.
- **Velocity and capacity** are derived (§12.2): the planning capacity is the average final velocity of the last 3 closed sprints.

The GitLab iteration configuration that mirrors the sprints is in `@docs/instructions.md §17.3`.

### 12.11 Roadmap and milestones — delivery stages

Milestones are not a section of `state.json`: the delivery stages are the entries of `state.json` `roadmap[]`, in order — `id` (e.g. `R1`), `title`, `start_date`, `end_date` (planned delivery day), `epic_refs` (its epics; an epic is in at most one stage). A stage has no `.md` of its own; its status and progress are derived from its dates and its epics — never from issue counts.

The narrative for the stakeholders is `Roadmap.md` (L1, PM-signed), which does not repeat these data. PM-owned: agents do not write the roadmap directly. Updated **obbligatoriamente** after every Sprint Review.

### 12.12 Release — versioned deliverable

In `state.json` `releases[]` (dashboard section, optional, unchanged from v8.2): `id`, `version`, `description`, `date`, `environment`, `mrs_merged`, `story_points`, `staging_url`, `gitlab_release_url`, `epics`. Created by Documentation Agent on trigger `release-ready.json`.

### 12.13 Signatures and gates

A signature lives on what it signs; there is no gates section in `state.json`. A signer is always a person (`Name <email>`); a role is not a signature.

- **Epic:** `validated_by` + `validated_at`, in the same commit as `done` (§12.6).
- **L0/L1 files:** one `prompt_stack[]` entry each, signed with `validated_by` + `validated_at`. Who signs which file → `AGENTS.md` (Prompt Stack signatures). A signature must be renewed when its file changed after `validated_at` (git history). ADRs are not in `prompt_stack`: they have their `accepted` status.
- **RNF:** `verified_by` + `verified_at` (§12.4).
- **Quality Gate L1** is passed when every L0/L1 file is signed; the first sprint does not open before. Checklist → `asf-overview.md`.
- **Human gates** — approvals and the trigger files under `triggers/` in the docs repo — are unchanged: no agent may proceed past a gate autonomously.

### 12.14 Traceability chain

Traceability is not stored: it is derived from the tasks. RF → the tasks citing it (`rf_refs`) → their epics; bug → the tasks fixing it (`bug_refs`) → their epics; story → its RFs (`rf_refs`) and its epic (`user_story_refs`); RNF → the epics citing it (`rnf_refs`); task → its commits (git). Used for CR impact analysis (RIB Delta Engine) and agent verification before implementation.

### 12.15 Retrospectives & Pattern Promotion

At sprint closure, Scrum Master Agent generates `docs/retro/<YYYY-WW>.md`. Committed autonomously. The retrospective lives only in that file: `state.json` holds no retrospective data.

**Pattern promotion rule (from Retrospective):**
- Pattern valid for current project → enters `architecture.json` or layer `AGENTS.md`
- Pattern valid for all BIT projects → candidate for AGENTS.md aziendale (L0) — requires explicit Dev Lead BIT deliberation
- Anti-pattern → enters Anti-patterns section of appropriate AGENTS.md

Agents propose, humans decide. Never autonomous promotion to L0/L1.

---

*product.md inizializzato da KStudio Bootstrap · {bootstrap_date}*
*ASF™ v8.0 scaffold — complete it during Startup, block ①*
