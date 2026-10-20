# ASF™ — standard changelog

> Decisions taken **about the standard itself**.

This is not `decisions/decision-log.json`, and the difference matters. That file is a
*template*: it ships empty, is instantiated into every project, and records the decisions a
project takes. The same is true of `.asf/architecture.json` — a template with no data in it,
because ASF is a standard and has no product and no architecture of its own to describe.

Decisions about the standard had nowhere to live until v8.0. They live here.

---

## How this standard is versioned

A version number here is not about the size of the change. It is about **what the change costs a
project that has already instantiated the stack** — because that project has its own copy of
these files under `docs/`, frozen at the version it was born with, and nothing tells it that the
standard has moved.

| | When to use it | What an already-instantiated project must do |
|---|---|---|
| **patch** `8.1.0 → 8.1.1` | Corrections. Wording, a typo in a schema description, a dead link. Nothing an agent or a project reads differently | **nothing**, and it does not even need to know |
| **minor** `8.1 → 8.2` | Additions. A new agent, a new schema, a new action code, a new optional field. **Nothing that exists changes shape** | **nothing is required.** It may adopt what was added, when it wants |
| **major** `8.x → 9.0` | Something that exists changes: a required field appears, an artifact moves or disappears, a contract moves, or a rule that was true stops being true | **a migration**, and the upgrade note says which steps and in what order |

**When in doubt between minor and major, choose major.** A minor that quietly needed manual
intervention is discovered by a project months later, by whoever inherits it, at the moment it
breaks — and by then nobody remembers that the standard moved.

Loosening an existing rule is a **minor**: nothing that was valid becomes invalid. Tightening one
is a **major**, however small, because something that passed yesterday fails today.

## Every version carries an upgrade note

The note is the only thing that survives the moment. It is written by whoever decides the
version, **when the decision is taken** — not reconstructed afterwards by whoever is paying for
it, which is the same thing as not having it.

Three lines, in this order, and any of them may be *nothing*:

1. **Must** — what a project already on the previous version has to do. For a minor this is
   `nothing`, and saying so explicitly is the point: silence reads as *I did not check*.
2. **May** — what becomes possible if the project chooses to adopt the addition, and what it costs
   to adopt it.
3. **Stops being true** — only for a major: what a project must stop relying on, named precisely
   enough that it can be searched for.

A note that says `nothing / nothing / —` is a good note. A version entry without a note is
incomplete, whatever its decisions say.

**Versions before v8.1 have no note**, and they are not backfilled here: a reconstruction written
by someone who did not take the decision is a guess wearing the clothes of a record. Where one is
needed — a project crossing v8.0 does need one — it is written as its own act, dated, and marked
as reconstructed.

## Cutting a release

1. **Decide the number** against the table above, before writing anything else.
2. **Write the changelog entry**: a one-line summary, the decisions as `D-<major>.<n>` continuing
   the series, and the upgrade note. The decision numbers never restart and are never reused —
   `D-8.7` means one thing forever, and other documents cite it by that name.
3. **Bump the header**, first five lines only, in `README.md`, `AGENTS.md`, `product.md`,
   `instructions.md`, `deployment.md`, `asf-overview.md` and `agents/README.md`. Occurrences of
   `vX.Y+` in the body stay as they are: they say when something started being true, and rewriting
   them rewrites history instead of versioning the present.
4. **Leave agent specifications at the version they were written against.** A specification that
   did not change does not gain a number it had nothing to do with.
5. **Tag** `v<major>.<minor>[.<patch>]`. The tag is what a project cites when it declares which
   version of the standard it conforms to.

A project declares **the version it conforms to**, never the latest one. A header that claims a
version the project has not adopted is worse than an old header, because it stops anyone from
looking.

---

## v8.6 — 2026-10-20

**Layers belong to the project**: ASF stops listing them. With it, the corrections to the validator
and to one catalog module that were circulating internally as 8.5.1.

This release also reconciles two lines of work. The public distribution published v8.5 on
2026-10-17 (attachments and links, empty collections: D-8.22 and D-8.23), while the internal source
had prepared a different v8.5 around project layers, numbered D-8.22 as well. A decision number is
never reused, and a version that is already public is not rewritten: v8.5 stays the public one, and
the layer decision ships here as **D-8.24**.

### D-8.24 — A layer is a node of the project tree, named by the project

**Context.** `frontmatter.schema.json` closed the layer to nine names (`fe`, `be`, `api`, `core`,
`worker`, `deployer`, `notify`, `infra`, `docs`), and `commit-gate` schemas to five. A project with
a desktop app, a mobile app or a CLI could not name it without changing the standard — KStudio
did, touching five files for one word (its DR-0155). Yet the standard already knew what a layer
is: what one agent can own while another works elsewhere, possibly on another machine. That is
the scope of `tasks[].files`, and `instructions.md` already reads the layer from it.

**Decision.** `$defs.layer` becomes a format, `^[a-z][a-z0-9-]*$`. The names are declared by the
project, in two places it already has: every repo of `state.json` project.repos is a layer, and
so is every `.asf/architecture.json` component that declares the new optional `path`
(`<repo>` or `<repo>/<dir>`, e.g. `core` → `api/core`). Components without code (a database, an
external service) have no path and are not layers. The commit gate's `layers` and `repo.layer`
become the same format. `tools/validate-stack.py` checks that a `path` starts with a repo and
that each layer name means one path, and **warns** when a bug `area` or an ADR `affects` cites
an undeclared layer.

**Consequences.** A bug `area`, an ADR `affects`, an `area::` label and a commit scope draw on one
vocabulary, the project's. Finer layers mean more tasks that can run in parallel; scheduling
them is the subject of a separate study.

### Corrections

- **The validator no longer checks cited paths inside catalog modules.** An `instructions.md`
  composed from the catalog (D-8.21) carries the text of each module between
  `<!-- asf:module … -->` and `<!-- /asf:module -->`; the paths cited there are the standard's
  examples (`docs/ProductLog.md`, `triggers/epic-ready.json`), not the project's files, and the
  validator reported each of them as missing. The project's own text — every line outside a module,
  and the **Project rules** section — is checked as before.
- **`NNN` is an example form**, like `XX` and `.N.md`: `docs/bugs/BUG-NNN.md` is not a path that
  should exist.
- **`asf-method-kstudio` cited `docs/nfr/RNF-NNN.md`** in three places, against D-8.18 (RNF live in
  `requirements/`, next to the RF). Now `docs/requirements/RNF-NNN.md`.

### Upgrade note — v8.6

- **Must** — nothing. Every name valid before is still valid; an undeclared one is a warning.
- **May** — give `path` to the architecture.json components that hold code, so that the warnings
  go and sub-repo layers (`core`, `worker`) mean a place in the tree.
- **Stops being true** — —
- **May** — also copy `tools/validate-stack.py` into the project and recompose `instructions.md`
  to pick up the corrected `asf-method-kstudio` module.

---

## v8.5 — 2026-10-17

Every artifact may carry **attachments and links**, and a project may start with empty collections.

### D-8.22 — An artifact may point at a file, and at something that lives outside

**Context.** An RF is agreed on a mockup, a task is implemented against a design, a bug is reported
with a screenshot. Until 8.4 the standard had nowhere to put them. The `.md` could name a path in
prose, which no field declares and no check reads as evidence, and `state.json` deliberately stopped
carrying `attachments` and `links` in 8.3 — correctly, because a reference to material belongs where
the text is, not in the state. So the material stayed in a chat thread, and whoever wrote the code
worked without it.

**Decision.** Two optional fields on all seven artifact `$defs` of `frontmatter.schema.json` — `rf`,
`rnf`, `epic`, `task`, `bug`, `us` and `adr`, the last for symmetry, since it is the one definition
without `additionalProperties: false`.

`attachments` holds files committed with the repository, in one flat folder, `docs/attachments/`.
Flat, because the same attachment may be cited by several artifacts and there is no folder that
belongs to all of them. An entry is a pointer and nothing else: no size and no media type, because
both are known at the moment the file is served, and written in an artifact they would age. The name
is lower case and without spaces (`^[a-z0-9][a-z0-9._-]*$`), because the validator's cited-path
check stops at a space and would report a name holding one as a truncated path that does not exist.
Allowed extensions, a closed list: `md` `txt` `csv` `json` `yaml` `yml` `html` `css` `js` `pdf`
`docx` `xlsx` `png` `jpg` `jpeg` `webp` `gif` `svg` `fig`. Archives (`zip`, `tar`, `gz`) are
excluded because they hide their contents from every check that reads the repository; media (`mp4`,
`mp3`, `wav`, `webm`) are the object-storage class and do not belong in git. No git-LFS either: a
mirror read gets the pointer instead of the file. Over 5 MB in one file is an error, about 50 MB in
the folder a warning, and a file in the folder that no artifact cites a warning — an orphan.

`links` holds http(s) URLs of material that lives outside: a Figma project, a Miro board. **No tool
ever reaches the network to check them** — not in CI, not anywhere; only their shape is validated. A
downloaded `.fig` is an ordinary attachment, while the URL of the Figma project is a `links` entry.

**Consequences.** A mockup attached to a task is evidence for whoever writes the code, declared like
the files in `reads:`; a coding agent opens png, jpg, webp and pdf natively, so an attachment is not
decoration for humans. `tools/validate-stack.py` gains one check, 4b, which adds only what the
cited-path check cannot know: that the entry is under `docs/attachments/`, that the name is usable,
the 5 MB error, the folder warning, the orphan warning, and the shape of a link. Both fields live in
the artifact frontmatter and **nowhere else: they are not in `state.json`**, and `state.schema.json`
gains nothing — the names `attachments` and `links` that 8.3 removed from the state stay removed,
and this decision does not reverse that one. `instructions.md` §16, `product.md` §12.3 and the
`asf-method` instructions module carry the two fields; the legacy module
`instructions/modules/method/asf-method-kstudio.md`, which the catalog still ships as the default,
describes projects whose `state.json` is 1.x and stays at 8.3, templates included.

### D-8.23 — A project may be born with nothing in it

**Context.** A project created from the standard gets a `state.json` whose `epics` and
`requirements.functional` are empty — there is nothing else it could get — and, in the same commit,
a schema that rejects it: both carried `minItems: 1`. The first consolidation, the only act that
would create the first epic and the first requirement, is blocked by the emptiness it exists to
fill. Found on a live project on 2026-10-17.

**Decision.** `minItems: 1` is removed from `properties.epics` and from
`properties.requirements.properties.functional` in `.asf/schema/state.schema.json`. Both keys stay
`required`: the collection must be present, and may be empty. Nothing else moves — every other
`minItems` in the schema stands, and so does the rule that an optional array is absent rather than
empty. These two are not optional: they are the spine of the project, and an empty spine is a stage
of its life, not an omission.

**Consequences.** A new project validates from its first commit, so the validator is usable while
the stack is being filled instead of only after it is full. Nothing that validated before stops
validating: this is a loosening. An empty `epics[]` is now a legal state, so whatever reads
`state.json` — a report, a dashboard, a derived count — handles zero epics and zero functional
requirements rather than assuming one.

### Upgrade note — v8.5

- **Must** — nothing.
- **May** — attach material to any artifact: take the new `.asf/schema/frontmatter.schema.json` and
  `tools/validate-stack.py`, create `docs/attachments/`, and cite a file as
  `docs/attachments/<name>` in the artifact's `attachments`, a URL in its `links`. Also take the new
  `.asf/schema/state.schema.json` if the project wants an empty `epics[]` or
  `requirements.functional[]` to validate — a project whose collections are already populated needs
  nothing.
- **Stops being true** — nothing. In particular the v8.3 decision stands: `attachments` and `links`
  are not keys of `state.json`, and nothing here adds them back to `state.schema.json` — they are
  artifact frontmatter, which is text, and the state knows nothing about them.

---

## v8.4 — 2026-10-05

`instructions.md` can be **composed from a catalog of modules** instead of being filled in by hand.

### D-8.21 — Instructions are chosen, not written

**Context.** The `instructions.md` template carries sixteen `{fe_framework}`-style holes. Nobody
fills them at the right moment, and an agent that reads the file with the holes still in it does not
know what to build with. Writing them through a conversation would cost long cycles of questions
about things that, for a kind of project, are always the same.

**Decision.** The standard ships `instructions/`: a catalog of **43 modules in 17 categories** —
language, localization, principles, topology, internal structure, communication between services,
frontend, backend, database, code style, comments, testing, observability, errors, security, git,
ASF method — each module a self-contained section with `{{placeholders}}`, `requires` and
`excludes`. A host composes `instructions.md` from a choice of modules (made with the
`pico-instructions` agent of PICO, contract in the PICO repository), writes the choice to
`.asf/instructions.json`, and keeps a final **Project rules** section that is never recomposed.
`tools/validate-instructions-catalog.py` checks the catalog. Topology and internal structure are
two categories: microservices whose services are hexagonal is a normal combination.

**Consequences.** Two projects that make the same choices get the same rules, word for word. A
rule improved in the standard reaches a project at its next recomposition, as a merge request the
Dev Lead signs. The hand-written template stays valid.

### Upgrade note — v8.4

- **Must** — nothing.
- **May** — compose `instructions.md` from the catalog; move the project-specific rules of the
  current file into **Project rules** first.
- **Stops being true** — —

---

## v8.3 — 2026-10-03

`state.json` becomes a strict contract with one place for every fact, and bugs, user stories and
non-functional requirements become artifacts of the standard.

### D-8.13 — `state.json` is a contract written in the standard, and the tools follow it

**Context.** Until v8.2 `state.schema.json` was **generated from the KStudio backend models**, by
structural inference from real `state.json` files, and it was lenient: `additionalProperties` was
allowed everywhere. `AGENTS.md` said so — *if reality and schema disagree, the backend model wins*.
A contract inferred from its readers describes whatever they happen to write, so it describes the
bugs as faithfully as the design: two keys for one fact (`status` and `state`, `points`, `pts` and
`story_points`), counters nobody recomputed, and a file every tool could read differently and none
could reject.

**Decision.** `.asf/schema/state.schema.json` is written in the standard, at `schema_version`
**2.0.0**, and it is **strict**: an unknown key is an error, and an optional array is absent rather
than empty. Backend models, TypeScript types and Pydantic models follow it. **If a tool and the
schema disagree, the tool is wrong.** `meta` carries two versions: `schema_version`, the schema's
own semver (an addition bumps the minor, a breaking change the major and ships a migration), and
`asf_version`, the version of the standard the project follows, which changes only with an
adoption. The artifact frontmatter gets the same treatment in `.asf/schema/frontmatter.schema.json`.

**Consequences.** This reverses the v8.2 rule in `AGENTS.md`. What stays is the gate: no top-level
key is added or dropped without a schema change, signed by the Dev Lead, and `meta.schema_version`
must match the version the schema accepts. A tool that shows or edits the state — KStudio — keeps
at most an exact cache of `state.json` and writes only through commits to it; operational data
that is not state (who is working on an epic) stays in the tool. The shape is in `product.md` §12.

### D-8.14 — One fact, one place

**Context.** Until v8.2 a task closing in `state.json` had to close in four more places: the
`**Status**` line of its `Task.md`, the epic's `tasks_done`, the milestone's `epics_done`, a ✅ in
the `product.md` RF index. `instructions.md` §15.6 listed eight targets to keep aligned, and then
a **conflict resolution priority** — `state.json` > `product.md` > `RF-XX.md` > `EpicXXX.md` —
which exists only because copies of one fact disagree.

**Decision.** **The state lives in `state.json`; the text lives in the `.md`** — titles,
descriptions, acceptance criteria. Nothing is copied from one to the other. The frontmatter of an
artifact keeps exactly the keys of its definition (an `RF` keeps `id`, `title`, `owner`) and any
other key is an error; the first H1 is exactly `# <id> — <title>`; no `.md` carries a status line,
a header line repeating references, a status column or a ✅. AC checkboxes stay: they are AC text.
The `product.md` RF index lists **exactly** the RFs of `state.json`, id and title, and the PM signs
it.

**Consequences.** Closing a task is one commit: its `status` → `done` in `state.json` and its AC
checked in the `Task.md`, nothing else. The conflict-resolution priority is gone for statuses,
because there is one source; text conflicts still follow the layer hierarchy. The rules and the
frontmatter of each artifact are in `product.md` §12, the templates in `instructions.md`, the
closure steps in `instructions.md` §15.

### D-8.15 — A reference is stored once, by the side that receives it

**Context.** v8.2 stored most links twice: an RF had `epic_ref` and the epic `rf_refs`; a task
had `epic_ref` and sat in a root `tasks[]`; a milestone listed `epic_refs` and the epic named its
`milestone`; `traceability[]` repeated all of it once more. A link stored twice is two facts, and
the second one is wrong the first time somebody forgets it.

**Decision.** Each reference is stored once, **by the side that receives it**, and **what exists
only inside something lives inside it**. Tasks live in their epic (`epics[].tasks[]`). Sprints and
roadmap stages list their epics (`epic_refs`): an epic is in at most one of each, and an epic in no
sprint is in the backlog. The epic lists its stories (`user_story_refs`) and its RNFs
(`rnf_refs`). The task cites its RFs (`rf_refs`) and the bugs it fixes (`bug_refs`). The bug cites
what it breaks (`rf_refs`, `rnf_refs`), set when it is reported. The story cites its RFs
(`rf_refs`, at least one).

**Consequences.** The inverse of every link is computed, never written: the RFs of an epic are the
ones its tasks cite, the epics of an RF or of a bug are the epics of the tasks that cite it. An
epic enters `state.json` together with its tasks, at least one, in the same commit — so an epic
with no tasks cannot be migrated until it is decomposed.

### D-8.16 — What can be derived is not stored

**Context.** v8.2 stored velocity four ways (`sprint.velocity_pts`, `sprints[].velocity_pts`,
`velocity_history[]`, `velocity_periods[]`), plus `tasks_total`, `tasks_done`, `epics_done`,
`progress_pct`, a `file_path` per entity and `meta.updated_at`/`updated_by` on every write. Every
stored derivation is a value that can be stale, and an agent that reads it has no way to know.

**Decision.** Nothing that can be computed from the file or from git is stored. **Velocity**:
current = points of the `done` tasks of the active sprint; target today = points of all its tasks
× elapsed days / total days; burndown = done points per day, dated from git; final = points of the
closed sprint's `done` tasks — not frozen, it rises if a task completes later; average = the mean
of the final velocities of the last three closed sprints, which is the planning capacity. Epic
points = the sum of its tasks; bug points = the sum of the tasks that fix it; a story's status
comes from its RFs; a roadmap stage's progress from its epics; file paths from the id; who changed
what and when from git.

**Consequences.** Points live on tasks only. A tool that shows a counter computes it. The
definitions are in `product.md` §12.

### D-8.17 — A signature lives on what it signs

**Context.** v8.2 recorded approvals in a `gates` section, apart from the things approved, and
Quality Gate Layer 1 was a separate act of the Dev Lead. `prompt_stack[]` recorded an `author` and
a `status` but no signature. A gate that says "closed by the Dev Lead" does not say which version
of which file the Dev Lead read.

**Decision.** The `gates` section is removed. **An epic** is signed by `validated_by` +
`validated_at`, a person, written in the same commit as `done`; the Developer Senior verification
that precedes it is unchanged. **Each L0/L1 file** has one `prompt_stack[]` entry —
`filename`, `validated_by`, `validated_at`; who signs which file stays in `AGENTS.md`, and a role
is not a signature. **Quality Gate L1 is passed when every L0/L1 file is signed**, and the first
sprint does not open before. A signature must be renewed when its file changed after
`validated_at`, which git tells. **An RNF** is verified by `verified_by` + `verified_at`. Human
gates — approvals, trigger files under `docs/triggers/` — are unchanged.

**Consequences.** Quality Gate L1 and the signatures to renew are derived from `prompt_stack[]` and
git, never stored. ADRs are not in `prompt_stack[]`: they have `accepted`. A persona is
`Name <email>`, never `agent:…`.

### D-8.18 — Bugs, user stories and non-functional requirements are artifacts of the standard

**Context.** v8.2 recorded, as an open issue, that **a non-functional requirement has a name and no
form** (D-8.12). Bugs and user stories were in the same position: the v8.2 schema had a lenient
`bugs` block and no stories at all, so each project and each tool invented its own.

**Decision.** Three artifacts join RF, Epic and Task, each with a folder, an id, a status set and a
strict frontmatter. **RNF** `RNF-NN` in `docs/requirements/RNF-NN.md` — no `nfr/` folder — status
`unverified|satisfied|at_risk|violated|waived`: it is never `done`, it is satisfied at a date.
**Bug** `BUG-NNN` in `docs/bugs/`, with a `severity`, the work statuses plus
`triage|not_reproducible|wont_fix|duplicate`, and `duplicate_of` exactly when `duplicate`.
**User story** `US-NNN` in `docs/stories/`, whose status is derived from its RFs. An epic of
`kind: container` collects the tasks that fix a sprint's bugs. RFs, epics and tasks share one
status set, `todo|in_progress|review|done|blocked`, where `review` means delivered, awaiting the
signature.

**Consequences.** The open issue of D-8.12 about RNFs is closed. A bug enters an epic only through
the task that fixes it. Folders, ids, frontmatter and lifecycle are in `product.md` §12; the
templates in `instructions.md`; the layout in `asf-overview.md`.

### D-8.19 — The standard ships its validator and its migration

**Context.** A strict contract that nobody runs is a lenient one with better documentation. And a
breaking change without a migration is paid by whoever inherits the project.

**Decision.** The standard gains `tools/`. `tools/validate-stack.py` validates both schemas and the
cross-file rules: unique ids, resolvable references, task ids prefixed by their epic, an epic in at
most one sprint and one stage, a story in at most one epic, no dependency cycles, repo names and
`files` globs, `prompt_stack[]` files that exist, an artifact for every file and a file for every
artifact, frontmatter id = file name, H1 = `# <id> — <title>`, `product.md` index = state RFs. It
exits 0 with `Prompt Stack valid.`, or 1 with `N ERRORS:` and one `docs/<path>: …` line each.
`tools/migrate-to-8.3.py` converts a v8.2 docs tree once, reports blockers and every value it
cannot carry, and installs the schemas and the validator in the tree.

**Consequences.** A project keeps its copy in `docs/tools/` and runs it in CI. The v8.2 names are
not read by any 8.3 tool: a project migrates once, and does not run on both.

### D-8.20 — This release is numbered 8.3, and it carries a migration

**Context.** By the table at the top of this file a change of this shape is a **major**: required
fields appear, artifacts move, rules that were true stop being true. But KStudio already ships the
BUG/US/RNF artifact contract to projects under the name «ASF 8.3», before the standard had an 8.3.

**Decision.** The Dev Lead numbers the release **8.3**.

**Consequences.** The table does not change; 8.3 is the recorded exception. Its upgrade note
carries a **Must**, as a major's does — a project must not read *nothing is required* from the
number.

### The dashboard sections keep their v8.2 shape

`pipeline`, `product_log`, `alerts`, `releases` and `inbox` are carried as they were in v8.2,
optional. They will be revisited together with the dashboard; until then the strict schema does
not reach inside them.

### The agents and the catalogue follow the state

**`ASF.UPDATE.VELOCITY` is removed** from the Action Catalogue, which now reads 8.3 and holds
fifteen actions: velocity is derived from the task statuses (D-8.16), so there is nothing to
record. The code is never reused. `commit-gate.md` reads v8.3 because `asf.linkage` no longer says
that released story points are recorded against the sprint; its checklist, the commit format and
its import are unchanged. `asf-compliance.md` reads v8.3 because Quality Gate L1 is now passed
when every L0/L1 file is signed in `prompt_stack[]`, the five points being what the signers
certify (D-8.17); renewals need the git history, and a shallow clone reports them as not
verifiable. Its import gains a new prompt and a `state.summary` that samples the 8.3 sections and
the whole `prompt_stack[]`. `deployment.md` gains a CI job on the `docs` repository that runs
`tools/validate-stack.py` (§8.4). `asf-dev`, `asf-area`, `pitch`, the trigger schemas and the
other schemas and checklists are unchanged.

### Upgrade note — v8.3

- **Must** — in this order:
  1. Upgrade the tools that read or write the state — KStudio — to 8.3 **first**, and remove any
     merge driver or git hook that regenerates `state.json` from frontmatter: under 8.3 it would
     write the facts back into the wrong place.
  2. Stop every script the project wrote itself that writes `state.json`, GitLab synchronisation
     included: under 8.3 `gitlab-state-sync` reads `state.json` and never writes it
     (`deployment.md` §8.3), and nothing but a commit of the state changes the state.
  3. Re-import `asf-compliance` if it is installed, and drop the mapping of `ASF.UPDATE.VELOCITY`
     from every caller of the Action Catalogue.
  4. Decompose into tasks every epic that has none: an epic enters `state.json` with its tasks.
  5. Run `python3 tools/migrate-to-8.3.py --docs docs --out <dir>` (options `--repos-root`,
     `--repo URL`, `--closed-on N=YYYY-MM-DD`, `--sprint-dates N=YYYY-MM-DD..YYYY-MM-DD`,
     `--report FILE.json`), fix the blockers it reports, repeat until there are none, then run it
     with `--write`. `--write` refuses while there are blockers.
  6. Keep the installed `.asf/schema/state.schema.json`, `.asf/schema/frontmatter.schema.json` and
     `tools/validate-stack.py`, and run the validator in CI (`deployment.md` §8.4).
  7. Sign again: every L0/L1 file in `prompt_stack[]` — a v8.2 gate that names only a role gives
     no signature — and every epic the migration returns from `done` to `review` because it found
     no signature for it.
  8. Fix what the report lists: the `product.md` RF index (the PM signs it again), prose that cites
     removed files, sprint goals.
  9. Rebuild what the report lists as lost — `milestones[]`, `attachments[]` and every key the
     migration does not read, each reported with its value — where it still matters, as roadmap
     stages, artifact text or files in the repository; or record that it is gone.
  10. Declare 8.3 in the headers.
- **May** — adopt the BUG, US and RNF artifacts; give tasks `files` (globs, first segment the repo
  name) to plan parallel work — two tasks with no file in common and no `depends_on` between them
  may run in parallel; group epics into `roadmap[]` stages.
- **Stops being true** —
  - top-level `version`, `sprint` (the active-sprint block and its `issues`, `burndown`,
    `velocity_pts`, `velocity_target`, `velocity_history`, `goal_status`), root `tasks[]`, `gates`,
    `milestones`, `velocity_history`, `velocity_periods`, `retro`, `retrospectives`,
    `traceability`; `meta.updated_at`, `meta.updated_by`;
  - epic `title`, `sprint`, `sprint_id`, `rf_refs`, `pts`, `story_points`, `file_path`,
    `tasks_total`, `tasks_done`, `state` (→ `status`), `type`, `milestone`, `milestone_ref`,
    `description`, `area`, `links`, `attachments`, `cr_status`, `generated_at`, `gitlab_epic_id`,
    `gitlab_url`, `issues_open`, `issues_total`;
  - task `title`, `layer` (→ `files`), `assignee`, `epic_ref`, `sprint`, `sprint_id`, `file_path`,
    `issue_ref`, `rf_ref` (→ `rf_refs`), `pts` and `story_points` (→ `points`);
  - every `file_path`; the `epic_ref` of RFs and bugs; bug `title`, `description`, `created_at`,
    `updated_at`, `attachments`; sprint `label`, `goal_status`, `milestone`, `retro`,
    `velocity_pts`, `velocity_target`, `epic_velocity`;
  - `requirements.sections`, `requirements.epics_last_generated`,
    `requirements.last_epic_trigger_at` (→ `requirements.functional[]` and `non_functional[]`);
    every `items` wrapper (`bugs.items` → `bugs[]`); `roadmap.sections` (→ `roadmap[]` stages, by
    the migration); `project.repos` as an object keyed by role (→ an array of git URLs) and every
    other `project` key but `name`; `prompt_stack[]` `author`, `last_updated`, `layer`, `status`,
    `warn_message`;
  - keys some projects carried under the lenient v8.2 schema, which the strict schema now rejects:
    `nfrs`, `open_questions`, `meta.generated_at`, `meta.generated_by`, `meta.notice`, epic
    `points` and `slice`, bug `task_refs`, `points` and `resolved_at`, sprint `declared` and `next`,
    the `epic_ref` of RNFs and stories;
  - in frontmatter: `status`, `epic`, `requirements`, `points`, `sprint`, `slice`, `priority` and
    any other key outside the artifact's definition;
  - in the `.md`: `**Status**`, `**Validated by**`, `**RF covered**`, `**Dependencies**`,
    `**Area**` lines, "RF in scope" tables, ✅ marks and status columns in `product.md`;
  - an `nfr/` folder for RNFs;
  - the action code `ASF.UPDATE.VELOCITY`, and "released story points are recorded against the
    sprint" in the Commit Gate's `asf.linkage`; `ASF.LINK.COMMIT_TO_EPIC` and
    `ASF.LINK.COMMIT_TO_TASK` targeting `state.json` (they target the commit);
  - `gitlab-state-sync` filling `issue_ref` and recomputing issue counts, and "leave `issue_ref`
    untouched": the job never writes `state.json`;
  - `official/ASF_Operating_Model_v8.2.md` and `official/ASF_Operating_Model_v8.2_diagram.html`
    at those paths: they are in `official/old/`, unchanged, and the v8.3 editions in `official/`
    replace them — the v8.2 entry below names the edition that was current then;
  - the rules: "`state.schema.json` is generated from the backend models", "the backend model
    wins", the conflict resolution priority `state.json` > `product.md` > `RF-XX.md` >
    `EpicXXX.md` for statuses, the `tasks_total` invariant, the counters and timestamps written
    when a task closes, Quality Gate L1 as a separate signature, the epic statuses `planned` →
    `in-progress` → `done`, the rule that an epic's In Scope section must list its RFs and that an
    epic without explicit in-scope RFs blocks task generation (the RFs of an epic come from its
    tasks), CRs captured as epics with `type: "cr"`, RF `attachments[]` and "Agents MUST preserve
    `attachments[]`", the `## DoD` checklist in the `Task.md` template (the DoD is
    `instructions.md` §15), velocity written as a stored figure in retrospectives and release
    notes.

---

## v8.2 — 2026-09-15

The Operating Model document is part of the standard, and it is realigned rather than reprinted.

### D-8.12 — The document that circulates is versioned with the files it describes

**Context.** The official Operating Model — the manual that goes to clients and to new teams — was
at **v7.4, in Italian**, and had drifted four releases. It named six agents where the catalogue
held fifteen. It called the operating surface CronStudio and its state file
`docs/.cronstudio/state.json`. It made `CLAUDE.md` the entry point of the Prompt Stack, which
stopped being true in v8.0. It described a stack of five layers; there are six, and `L4` did not
appear in it once. None of those disagreements announced itself.

This is the same failure v8.0 fixed for the presentation deck, found again one layer out. The deck
was moved into the repository *so that it could not drift silently*; the document it was made from
was left outside, and drifted.

**Decision.** `official/` holds the Operating Model, versioned here with everything else, and
`official/old/` holds superseded editions — kept, because a project may still be running on one.
The document is **realigned, not translated**: where it disagreed with the standard the standard
won, and where the standard had moved on the document gained a chapter. It is in English, like
every other normative text since v8.0.

**Consequences.** The repository gains a location and a rule, which is what makes this a minor
rather than a patch — translating a document on its own would have been neither. The document
carries, at the top, the statement that **where it disagrees with the files, the files are right**,
and the disagreement is a defect to be reported. That sentence was already in the deck; it needed
to be in the manual too.

Four open issues that v8.0 and v8.1 created are now written down where someone will read them:
nine action codes still name an executor that does not exist; a pitch package does not become ASF
artifacts until the translation agent is built; **a non-functional requirement has a name and no
form** — the standard says `RNF-XX` and stops, while a functional requirement has a file
convention, a format and a rule about its acceptance criteria; and nothing propagates a version
into instantiated projects.

### `asf-dev` clones by name, and a mandate can span three repositories

`git.clone` took no arguments and cloned the single URL the caller had put in `repoUrl`, into a
fixed path — one session, one repository, structurally, and in practice always the documentation
repository, since that is what the caller resolved. But a mandate comes from an epic, a
requirement or a task, and those routinely span `api`, `be` and `fe` together.

`git.clone.repo` takes the repository's **name** and clones it under that name, so the agent calls
it once per repository it needs and they sit side by side. `git.diff` and `git.status` take the
same name, because a diff of one repository out of three is not a diff.

**A new tool id rather than a changed one.** `git.clone` is declared by `asf-compliance` as well,
and the tool catalogue is shared: repointing it would have left two imports overwriting each
other's configuration, and whichever ran last would decide whether `asf-compliance` still worked.
Additive, therefore, which is why it belongs in a minor — and why `asf-dev.md` now reads v8.2:
a specification that changed carries the version it changed in.

**Which repositories exist is not in the prompt.** `repoNames` reaches the agent from the session,
so it changes per project without releasing a version of the agent. The prompt says where to look,
not what is there.

### Upgrade note — v8.2

- **Must** — nothing. No artifact changes shape, no schema moves, no agent contract changes.
- **May** — re-import `asf-dev` if it is installed: it gains `git.clone.repo` and keeps
  `git.clone` untouched for `asf-compliance`. And read the manual: a team taking over a project,
  or a client being shown the model, should be
  given `official/ASF_Operating_Model_v8.2.md` and not the edition they were given before, which
  is wrong in six specific ways listed at the top of the new one.
- **Stops being true** — nothing in the standard. Plenty in the **previous edition of the
  document**, and that is the point: anyone still working from v7.4 is working from CronStudio,
  six agents, `CLAUDE.md` as L0, and a five-layer stack.

---

## v8.1 — 2026-09-15

The pitch: requirements gathered as a conversation, and an agent that holds no tools.

### D-8.7 — A conversational agent is a third kind, and it holds nothing

**Context.** D-8.2 tells reading agents from acting agents by permission: a reading agent holds
no tool that can write, and no instruction can supply one. The Pitch Agent fits neither side. It
never touches a repository — not to read it, not to write it. It has no workspace, no MCP server,
no declared tool and no delegate it may call.

**Decision.** The catalogue gains a third kind, **conversational**. Its entire surface is one
validated envelope per turn, and it is defined by what it cannot reach rather than by what it may
write.

**Consequences.** It cannot be dispatched an Action Catalogue code, and emits none: nothing it
produces reaches a repository without a host that applies its patches and a human who signs. The
reading/acting distinction is unchanged — a third kind does not blur a line, it says the line was
never about this agent.

### D-8.8 — The pitch produces a method-neutral package; translating it is another agent

**Context.** An elicitation agent that knows its target format writes toward it. The first thing
lost is the question nobody asked because the template had no field for it; the second is every
other target, because the same conversation has to serve a team on ASF, a team on an issue
tracker, and a customer who wants a document.

**Decision.** The pitch produces a **package** — a JSON artifact with local keys, carrying no
`RF-XX`, no `EpicNNN`, no `docs/` path and no ASF vocabulary. Its contract is
`.asf/schema/pitch-package.schema.json`. Turning a package into ASF artifacts is a **separate
agent**, downstream, which may be called by something else entirely.

**Consequences.** The standard gains an exchange schema it did not have, and the catalogue gains
an unimplemented executor — named, so that nobody mistakes the gap for an oversight (D-8.6). The
Action Catalogue gains no code in this version: a translator that does not exist cannot be
dispatched.

### D-8.9 — The coverage checklist is installation configuration, declared at the opening

**Context.** The same reasoning as D-8.3, arrived at from the other end and the hard way. The
first implementation had the agent record only what changed state — an economy that cost the
feature its point: a checklist that appears in pieces never says what is missing, and without a
finish line the agent asks questions until the person gives up.

**Decision.** The checklist ships as configuration (`.asf/pitch-checklists/`, schema in
`.asf/schema/`), is **seeded whole** when the pitch opens with every entry `open`, and the agent
only changes state. Profiles are **nested**, so a pitch can be opened before anyone knows what it
is about: seed the nucleus, let the agent declare the profile, add what is missing. Nothing is
ever removed.

**Consequences.** Completeness becomes computable — covered over relevant — and therefore stops
being something the agent declares about itself. An **`open` entry blocks delivery; a `deferred`
one does not**, which is the difference between not having asked and having decided not to ask.
Adding a profile is a Dev Lead act, because the profile decides what gets asked at all.

### D-8.10 — An agent that talks to a person is prompted in that person's language

**Context.** `agents/README.md` requires every shipped prompt to be English, and the requirement
is right for agents whose reader is another agent. The Pitch Agent is the first whose reader is a
person who is not technical, and whose prompt carries the phrasings it reuses — how a question is
put, how a reason is given.

**Decision.** The prompt of a conversational agent is written in the language of the conversation
it conducts. `pitch.import.yaml` ships an Italian prompt. **The specification stays English**, as
all specifications do: it is read by whoever installs and reviews the agent, not by the
interlocutor.

**Consequences.** Localising the agent means a new prompt and a new validation, not a
translation — the qualities this prompt is judged on are not covered by any test and are measured
on real pitches. The rule in `agents/README.md` is narrowed to say what it always meant: prompts
addressed to machines are English.

### D-8.11 — Every version says what it costs, at the moment it is decided

**Context.** The standard reached v8.1 with no way to tell an instantiated project that anything
had moved. A project instantiated at v7.6 stayed at v7.6 for two versions, and nobody noticed
until someone went looking — which is how the cost of a standard's motion ends up being paid by
whoever inherits the project rather than by whoever decided the change.

**Decision.** The number is chosen by **what the change costs a project already on the previous
version**, not by the size of the change, and every version entry carries an **upgrade note**:
*must* / *may* / *stops being true*. Written when the decision is taken. The rules are at the top
of this file, and so is how a release is cut.

**Consequences.** ASF still has no mechanism to propagate a version into projects — this does not
create one, and pretending otherwise would be worse than the gap. What it creates is the thing a
project needs when it decides to move: a written statement of what moving costs, from the person
who knew. Versions before v8.1 have none and are not backfilled; where one is needed it is
written as its own dated act, marked as reconstructed.

### Upgrade note — v8.1

- **Must** — nothing. No artifact changes shape, no schema gains a required field, no existing
  agent's contract moves, and the one rule that changed (D-8.10, prompt language) loosens rather
  than tightens.
- **May** — adopt the Pitch Agent: install `agents/pitch/pitch.import.yaml`, seed a coverage
  profile from `.asf/pitch-checklists/`, and implement the host contract in
  [`agents/pitch/pitch.md`](agents/pitch/pitch.md) §5 — the field map, the projector, and the
  rejection that goes back to the agent. **Without the host the agent is a chat that proposes
  edits nobody applies**, so adopting it is a piece of work and not an import. A pitch package
  does not become ASF artifacts until the translation agent exists (D-8.8).
- **Stops being true** — nothing.

---

## v8.0 — 2026-09-04

Commit-level conformance, dispatchable remediation, and two artifacts fewer.

### D-8.1 — Remediation actions are codes, not prose

**Context.** An analysis agent that reports `"action": "link this commit to its epic"` has
produced something a human can read and an agent can read, and that no caller can dispatch.
Hooking a finding to an API function requires a stable identifier and typed parameters.

**Decision.** The **ASF Action Catalogue** (`.asf/action-catalog.json`) defines a closed set
of action codes — `DOMAIN.PRIMITIVE.OBJECT` — each with an executor, a target, an
idempotency flag and a JSON Schema for its parameters. Eight primitives (`LINK`, `CREATE`,
`UPDATE`, `RUN`, `GENERATE`, `REQUEST`, `ESCALATE`, `NONE`) are the closed vocabulary from
which codes are built; a caller that implements the primitives can dispatch codes added
later without new integration work.

**An agent selects a code and never invents one.** A situation the catalogue does not cover
is reported as a finding with no action, and the catalogue gains an entry. An improvised code
silently breaks every caller that mapped the catalogue.

**Consequences.** Human-readable labels remain, but derived from the code rather than in
place of it. Adding an action is a Dev Lead act, because the catalogue defines what agents
may propose at all.

### D-8.2 — Reading agents and acting agents are separated by permissions

**Context.** An agent that both judges and repairs cannot be audited: no independent record
survives of what it found before it acted.

**Decision.** Agents are either **reading** or **acting**, and the boundary is enforced by
the permission set rather than by instruction. A reading agent holds no tool that can write —
not a tool it is told not to use, but no such tool at all. An acting agent holds no tool that
can publish: it changes files, and whether those changes become a commit, a branch or a merge
request is decided by its caller.

**Consequences.** This is the ASF rule that agents have no autonomous merge authority,
expressed as a capability rather than as a sentence in a prompt. It also gives the Action
Catalogue its purpose: a reading agent emits `CODE.GENERATE.CHANGE`, and something else
carries it out.

### D-8.3 — The commit gate checklist is installation policy, not prompt content

**Context.** What a commit is judged against changes per organisation, and sometimes per
quarter. Encoding it in a prompt makes every change a release.

**Decision.** The checklist is versioned configuration
(`.asf/schema/commit-gate-checklist.schema.json`), edited from an administration surface, and
passed to the agent per run. Every report carries the `checklist_version` it was judged
against, so a verdict stays interpretable after the policy has moved on.

**Consequences.** Each entry carries `applies_to` (layers, paths, branches, events). Without
scoping, a test verification fails on a commit that touches only a README — and a gate that
raises false alarms is switched off within a week, after which it protects nothing.

### D-8.4 — L0 is `AGENTS.md`

**Context.** The Prompt Stack entry point was named `CLAUDE.md`, binding a methodology to one
vendor's tool. ASF is neither a tool nor a framework.

**Decision.** L0 is **`AGENTS.md`**, in the standard and in every layer repository. A
five-line `CLAUDE.md` remains as a pointer for tools that look for that name — **a pointer,
never a copy**: two files holding the same content diverge, and nothing reveals the divergence
until an agent acts on the stale one.

**Consequences.** Quality Gate L1 point 4 changes text: it certifies `AGENTS.md` for every
layer repository. 61 references were updated across the stack.

### D-8.5 — One architectural artifact, not two

**Context.** `architecture.json` held the state, `architecture.md` held the rationale, and the
standard carried a rule for deciding which won when they disagreed. That rule is only needed
because two files can disagree at all — and the schema said as much, delegating ADR narrative
to "the MD referenced by `docRef`".

**Decision.** `architecture.md` is removed. The `adLog` carries `context`, `options`,
`rationale` and `consequences` itself, typed as long-form Markdown. `docRef` is deprecated
rather than deleted, so archives written before v8 stay readable. KArchitecture gains
`techStack`, `repoLayout`, `patterns`, `domainRules` and `llmPolicy` — the five sections that
would otherwise have been orphaned — and `context_for_agents`, which every instance had
carried since the first template while the schema never defined it, and therefore never
validated it.

**Consequences.** A risk worth naming: prose is less comfortable in a JSON field than in a
Markdown document, and the temptation is to write two-line ADRs. The schema states that a
short `rationale` is a defect rather than brevity. If `adLog` degrades into a list of titles,
that is the decision to revisit.

### D-8.6 — An unimplemented executor says so in the catalogue

**Context.** v8.0 defined sixteen actions and four agents. Nine of those actions name an
executor — `epic-task-agent`, `task-generation-agent`, `test-generation-agent`,
`scrum-master-agent`, `documentation-agent` — that exists only as a row in the factory
catalogue: no specification, no importable definition. An analysis agent would emit a
correctly formed code addressed to nobody, and the caller would discover this at dispatch.

**Decision.** Each action carries `executor_implemented`. The factory catalogue gains a
**Status** column with three values: *implemented* (a specification and an import exist under
`agents/`), *to be implemented*, and *external* — for capabilities another product provides
and that will not gain an ASF specification.

**Consequences.** An action code that resolves to nobody is worse than an absent code,
because it looks dispatchable. Stating the gap in the machine-readable file is what lets an
integrator plan around it instead of finding out at runtime.

Also fixed here: the catalogue had never validated against its own schema. The `code` pattern
forbade digits, so `TEST.GENERATE.E2E` was invalid from the day it was written — and nothing
said so, because the validation had never been run.

---

## v7.6 — 2026-07-26

Baseline formalised. Recorded here for continuity; the decisions predate this changelog.
