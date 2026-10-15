**BETTER INNOVATION TECHNOLOGIES**

**ASF™**

Augmented Software Factory

Operating Model · System Design & Implementation Manual

bit-farm.it

Version 8.3 · 2026-10-03 · CONFIDENTIAL

---

> **This document is generated from the standard.** Where it disagrees with the files in this
> repository, **the files are right**, and the disagreement is a defect to be reported. The
> normative text lives in `AGENTS.md`, `asf-overview.md`, `product.md`, `architecture.json`,
> `instructions.md`, `deployment.md`, the JSON schemas in `.asf/schema/` and `agents/`; this
> document is how the model is explained to someone who is not going to read them.
>
> The previous edition was **v8.2**. It described a `state.json` that v8.3 replaced: a `gates`
> section, a root list of tasks, stored velocity history and milestones, statuses repeated in the
> Markdown files. It is kept in `official/old/`, with the v7.4 edition before it, because a project
> may still be running on either.

---

# 1. Executive Summary

ASF™ (Augmented Software Factory) is the proprietary operating model of Better Innovation
Technologies for building and running AI-augmented software development teams. It is a set of
roles, methods and tools directed at enterprise-grade software, built around collaboration
between human operators and AI agents, with responsibilities and governance defined explicitly
for each.

The model rests on four axes.

- **People and skills.** Mixed human+AI teams with roles that are not interchangeable. Humans
  hold domain control, the client relationship and accountability. Agents bring execution speed,
  consistency, and the ability to work in parallel.

- **Technology.** The platforms that make the factory possible and that automate it.

- **Method.** The instructions, procedures and processes that orchestrate the work. At the centre
  sit the multi-layer **Prompt Stack** — a context hierarchy that guides agents with increasing
  specificity, from company engineering practice down to a single atomic sprint task — and
  **SCRUM-AI™**, Scrum compressed by AI acceleration, with ceremonies partly or wholly automated
  and human decision gates left explicit.

- **Governance.** What an agent may propose, what it is measured against, and who signs. Since
  v8.0 this stopped being a sentence in a prompt and became a permission set, a closed catalogue
  of action codes, and a conformance check that runs on every push.

**What changed since the previous editions.** Five releases of the standard are folded into this
document. v7.6 brought requirement detail files and the Decision Record register. v8.0 brought
the **Commit Gate** (conformance judged at the commit, on every push), the **Action Catalogue**
(findings that can be dispatched, because they are codes and not prose), `AGENTS.md` as the entry
point of the Prompt Stack, and a single architectural artifact. v8.1 brought the **Pitch Agent**,
which gathers requirements as a conversation, and — after finding that nothing in the standard
told an instantiated project that anything had moved — the rule that every version states what it
costs. v8.2 brought this document: the model, current, in the language the standard is written in.
v8.3 — *one fact, one place* — rebuilt `state.json` on one rule: the state lives in it, the text
lives in the Markdown files, nothing is copied between them and nothing that can be derived is
stored; and it gave non-functional requirements, user stories and bugs a file and a form (§7.3,
§7.6).

# 2. The ASF™ Operating Model

## 2.1 Reading the diagram

This chapter describes the operating model through its reference diagram, the **ASF™ Operating
Model**. The diagram is meant to be read at two levels: as a whole, top to bottom and left to
right, and layer by layer — each horizontal band is a chapter of this document.

The symbols are consistent: the same symbol or colour always means the same thing, wherever it
appears.

### Badges

Badges mark the nature of a step. **✓ is a human gate**: a point where an artifact does not
proceed until a named person signs it. A badge is not decoration — every ✓ in the diagram
corresponds to an authority written down in `AGENTS.md` under *Document authority and agent commit
governance*, and to a person who can be asked why they signed.

### Chips

Chips are cross-references. A **prompt chip** names the Prompt Stack layer a step reads or writes;
a **GitLab chip** names the entity that mirrors it operationally. Together they answer, at a
glance, two questions that otherwise require reading three files: *what context does this step
need*, and *where does its result become visible to the team*.

### How to read it

Top to bottom the diagram goes from intent to running software: strategy, the people and agents
who do the work, the one-off startup, the operating cycle, and the tools underneath. Left to
right, inside each band, it goes from input to delivery.

Nothing in the diagram is sequential across bands. The strategic layer never stops; the operating
cycle repeats weekly; the startup happens once. The vertical order is dependency, not time.

## 2.2 Strategic layer — from stakeholders to backlog

The top band is where the system starts. On the left are the **Stakeholders** — clients, business
owners, end users — who express needs, constraints and priorities. Those needs are elicited and
formalised by the Product Owner / PM and become documented requirements.

The flow runs left to right: from needs to requirements, from requirements to the files that
hold them (`product.md`), to the product's view over time (`Roadmap.md`) and the ordering of what
gets built (`ProductLog.md`). The right edge is delivery: working, tested software the client
owns.

**Since v8.1 the left edge has an agent on it.** A pitch is a conversation that produces the
document while the interlocutor talks, and it is the first surface of the factory a client can
drive themselves. Chapter 4 describes it; Chapter 3 describes what it feeds.

The three KPI in the right corner — 30 days to first delivery, 1 week per sprint, 12 months
minimum engagement — are the parameters of the commercial model. Full treatment: Chapter 3.

## 2.3 Skills & Roles layer — who does what

The second band holds the people. A vertical line splits it: human roles on the left, AI agents
on the right. The split is functional, not hierarchical, and one criterion governs it — **wherever
a decision requires accountability toward the client, strategic authority, or judgement about the
project's domain, that decision belongs to a human.** Everything that can be specified precisely
enough to run reliably without contextual judgement is a candidate for an agent.

Human roles hold the decision gates, marked ✓. Agents work inside defined perimeters of autonomy
and produce output humans validate before it becomes final. Full treatment: Chapter 4.

## 2.4 Startup layer — from vision to first sprint

The third band is project start-up: a one-off, not a recurring cycle, that precedes entry into
SCRUM-AI™. Left to right: requirements gathered into `product.md`, roadmap and epics set up in
GitLab, the Prompt Stack initialised. Only when the three blocks are complete and every L0/L1 file
is signed — which is what passing **Quality Gate Layer 1** means — is the project ready for its
first sprint. Full treatment: Chapter 5.

## 2.5 SCRUM-AI™ layer — the operating cycle

The fourth band is the largest, in two columns: on the left the **Prompt Stack**, six levels of
context (**L0 → L1 → L1.5 → L2 → L3 → L4**); on the right the SCRUM-AI™ cycle with its sequential
phases. Each phase shows the badges, prompt chips and GitLab chips it involves. Below the phases,
the dashed box marks the **Change Request** as an asynchronous event with a mandatory top-down
cascade. Full treatment: Chapter 8.

## 2.6 Tech Stack layer — the tools

The bottom band maps the enabling technology. Each tool carries the chips that identify its role
in the bands above, which is what makes the diagram a cross-reference rather than a picture. The
GitLab repository structure, which physically enforces the separation between prompt stack and
code, is described here. Full treatment: Chapter 9.

# 3. Strategic Layer — From Stakeholders to Backlog

## 3.1 The PM as the interface between need and system

The strategic layer is the factory's entry point. Before an agent generates a line of code, before
a Dev Lead assesses whether an epic is feasible, there is a **need** — expressed by someone with a
problem to solve or an opportunity to take. That person, or that group, is the Stakeholder.

The Stakeholder does not interact with the factory directly. Their interface is the Product Owner
/ PM, the most strategically critical figure in the model — not because they manage the project,
but because they translate between two radically different languages. A need is often implicit,
contradictory, and liable to change. A requirement is explicit, structured, and actionable by the
factory. The PM stands between them.

We write *need* and not *requirement* for what arrives from stakeholders, and the distinction is
operational rather than semantic: a need is not yet an input the system can work on. It becomes
one only after the PM has understood it, put it in context, and turned it into structured
artifacts. That transformation is the first flow of the strategic layer: Stakeholder → Needs /
Vision → Requirements.

## 3.2 The flow: from need to backlog

The PM starts with elicitation: structured workshops, interviews, analysis of what already exists,
rapid prototyping sessions to surface what the client does not yet know they want. The result is
not a report — it is `product.md`, the document that describes the product from vision to
structured requirements.

**Since v8.1, elicitation has an agent.** A *pitch* is a conversation that produces the document
while it happens: the agent interviews, and the interlocutor watches the document fill in as they
answer. It does not replace the PM — it gives them a surface the client can sit in front of, and
it gives the factory something the PM's notes never had: **every value knows where it came from**,
including the case where nobody said it and the agent inferred it. The Pitch Agent is described in
§4.4; what it produces is a method-neutral package, and turning that package into `RF-XX.md` files
is a separate step.

`product.md` is the factory's first artifact and its most durable. It is a **signed index** (L1):
the id and title of every functional requirement — exactly the RFs `state.json` lists — signed by
the PM. The full detail of each functional requirement lives in `docs/requirements/RF-XX.md`
(L1.5) — individual files with acceptance criteria in BDD form and technical notes; each
non-functional requirement has its own file beside them, `docs/requirements/RNF-XX.md`, with a
metric, a threshold and the way it is verified. Statuses and links live in `state.json`, never in
these files (§7.3). The decoupling lets agents load only the requirements the running task needs
instead of swallowing the whole document.

Once `product.md` has a solid initial structure, the PM builds the product's view over time in
`Roadmap.md` and the ordering of features in `ProductLog.md`. The two translate an ambition into a
plan: `Roadmap.md` speaks the stakeholders' language — quarters, milestones, strategic objectives;
`ProductLog.md` speaks the factory's — prioritised epics and references to the corresponding
`EpicXXX.md`, whose status is read from `state.json` and not written here.

The PM validates both before presenting them at Sprint Planning. The validation is not
bureaucratic: it is the moment the PM certifies that what is about to set the factory in motion is
really what the stakeholders expect. Without that certainty, Sprint Planning does not start.

## 3.3 The artifacts and their life cycles

The three artifacts have distinct life cycles and must not be confused with each other, nor with
the GitLab entities that mirror them operationally. **The MD file is the narrative specification;
the GitLab entity is the operational tracker.** They are two levels of one structure.

| Artifact | |
|---|---|
| **`product.md`** | Product identity (L1): vision, target user, look & feel, core flows, plus the RF index. Detail lives in `docs/requirements/RF-XX.md` and `RNF-XX.md` (L1.5). Updated on every approved Change Request and on every Sprint Review feedback. Owned and signed by the PM. **RF resolution rule, mandatory for agents:** load `RF-XX.md` → fall back to the `product.md` entry → explicit error if absent |
| **`Roadmap.md`** | Updated after every Sprint Review, without exception. It is the continuing proof, shown to stakeholders each cycle, that the factory is building what matters. Its relation to GitLab Milestones is narration to tracking: the file tells the direction, the milestones measure progress with automatic completion percentages. The delivery stages themselves, with the epics each one delivers, are the `roadmap[]` of `state.json`, where their progress is derived rather than stored |
| **`ProductLog.md`** | Every epic here references an `EpicXXX.md` in the docs repository and a corresponding Epic on the GitLab Epic Board. These are not three copies of one thing: `ProductLog.md` is the prioritised narrative source of truth, the Epic Board is the operational planning view. Keeping them aligned is the PM's responsibility |

## 3.4 The engagement KPI

Three parameters sit in the diagram's right corner. They are not aspirations: they are what the
model was designed around, and what the whole system is built to guarantee.

**30 days** is the maximum time before the client sees the first working delivery on staging. Not
a prototype, not a demo: real output, tested, deployed. It is possible because Startup initialises
the Prompt Stack before the first sprint begins, and code generation produces a first draft on the
second day of execution.

**1 week** is the length of a sprint. The compression against Scrum's customary two weeks follows
directly from AI acceleration on execution: the bottleneck is no longer writing code, it is human
validation. A one-week sprint is sustainable only if `product.md` and `architecture.json` are
solid before Sprint Planning — and if they are not, the Dev Lead stops the start.

**12 months** is the minimum engagement. This is not a commercial constraint: it is how long the
transfer takes. At the end of the twelfth month the client does not receive a finished project —
they receive the factory: documented method, trained developers, the agent configurations, all the
code and the intellectual property, and a governance framework that runs.

> **The strategic layer never closes.** Unlike the others, which run in defined cycles, it stays
> active for the whole engagement. The PM keeps intercepting new needs, handling Change Requests,
> updating `Roadmap.md` after every review. The system never stops to wait for new requirements:
> it absorbs them through the Change Request mechanism in Chapter 8.

# 4. Skills & Roles — Humans and AI Agents

## 4.1 Two halves and a precise border

One criterion governs the split: **wherever a decision requires accountability toward the client,
strategic authority, or judgement about the project's specific domain, that decision belongs to a
human.** Everything specifiable precisely enough to run reliably without contextual judgement is a
candidate for an agent.

That criterion changes what the human roles are. The Senior Developer is no longer the primary
producer of code: they are the validator of what the agent produced. The QA Lead does not write
tests: they define the acceptance criteria the test agent turns into Playwright/Pytest. Human
roles move from execution to qualified supervision, and that move is what makes a one-week sprint
sustainable.

> **Prompt Stack governance.** **L0** (`AGENTS.md`, company-wide) — the Dev Lead only, after an
> explicit deliberation. **L1** (`architecture.json`, `product.md`, `deployment.md`,
> `instructions.md`) — Dev Lead or PM, never agents on their own; each L0/L1 file is signed by a
> person, in its own `prompt_stack[]` entry of `state.json` — the Dev Lead signs `AGENTS.md`,
> `architecture.json`, `instructions.md` and `deployment.md`, the PM signs `product.md`,
> `Roadmap.md` and `ProductLog.md`. **L1.5** (`RF-XX.md`, and `RNF-XX.md` beside them) — one file
> per requirement; a functional requirement's file is created by the KStudio backend and updated
> by the Epic & Task Agent on an approved CR, with a Dev Lead gate. **L2** (`EpicXXX.md`) — the
> Epic & Task Agent on defined triggers, validated by the Dev Lead before commit. **L3**
> (`Task.md`) — the Epic & Task Agent autonomously after planning; manual edits during the sprint
> are allowed with a mandatory note in the Retrospective. **L4** (`triggers/*.json`) — CI
> activation files, written by whoever fires the trigger and **deleted by the pipeline that
> consumes them**. User stories (`stories/`) and bugs (`bugs/`) belong to no layer: they are read
> with the epic or task that cites them (§7.6).
>
> **`AGENTS.md`, not `CLAUDE.md`.** The entry point changed name in v8.0: the file is read by
> every agent, not by one vendor's. `CLAUDE.md` still exists and is a **pointer** to it, never a
> copy — two files holding the same content diverge, and nothing reveals the divergence until an
> agent acts on the stale one.

## 4.2 The human roles

Four figures hold the factory. Each has a perimeter defined by where in the cycle it is active and
which artifacts it owns.

| Role | Active in | |
|---|---|---|
| **Product Owner / PM** | Strategic layer · Sprint Planning · Sprint Review · Change Request | Holds the strategic layer and the SCRUM-AI™ cycle together. Point of contact with stakeholders and translator of their needs; owner and signer of `product.md`, `Roadmap.md`, `ProductLog.md`. At planning, presents candidate epics, confirms priorities with the Dev Lead, and validates the generated `Task.md` before they become GitLab issues. At review, presents results on staging and updates `Roadmap.md` — not optional: it is how the factory certifies the direction still matches the need. **Every Change Request needs their signature** before any agent touches the Prompt Stack |
| **Dev Lead / Tech Lead** | Architecture · Technical governance · Prompt Stack L0–L1 · MR gate · **Action Catalogue and commit gate checklist** | Guardian of the factory's technical coherence. Before planning, signs the L0/L1 files that are theirs — **Quality Gate Layer 1** is passed when every L0/L1 file is signed. During execution, signs every Merge Request before it reaches `main` — not delegable, no exceptions. In Retrospective, decides which emerged patterns rise into the Prompt Stack: project-wide into `architecture.json`, company-wide into `AGENTS.md` by explicit deliberation. **Sole owner of L0 and of the technical L1 files.** In their absence no MR merges and no structural change propagates to the agents |
| **Senior Developer** | Execution · Validating agent output · Owner of the layer's `AGENTS.md` | Works in the factory's fastest loop: opens a `Task.md`, starts a coding session with the whole Prompt Stack as context, validates and refines the first draft, handles the edge cases the agent got wrong, opens the MR. Their distinctive skill is not typing speed — it is recognising when the output is **syntactically correct and semantically wrong**: when the code does what was asked and not what is needed. That distinction takes domain knowledge the agent does not have. Exists per layer — `fe`, `be`, `api` — and each owns their layer's context file |
| **QA Lead** | Test strategy · Acceptance criteria · Pre-review gate | Works on two horizons. Upstream, while epics and tasks are written, defines acceptance criteria granular enough for the test agent to turn into executable tests. Downstream, validates that the coverage produced is strategically adequate — not that the tests pass, but that they cover what matters. Signs acceptance before the client review. **The quality of the criteria determines the quality of the generated tests**: vague criteria produce shallow tests; precise ones produce a suite that finds bugs before the client does |

> In ASF™ the PM also absorbs the Scrum Master role. Routine ceremonies are automated by the
> Scrum Master Agent; the PM handles the exceptions, the blocks the agent cannot resolve, and the
> decisions that require authority toward the client.

## 4.3 The AI agents

Agents have structured roles, with defined inputs, outputs, activation triggers and perimeters of
autonomy. Each works inside a precise boundary: past that boundary, its output must be validated
by a human before it has any effect on the system. This is not a technical limitation — it is a
deliberate governance choice that keeps human responsibility over every artifact that reaches
production.

**Since v8.0 the boundary is not a sentence in a prompt.** It is a permission set. A *reading*
agent holds no tool that can write; an *acting* agent holds no tool that can publish. The rule
therefore holds even when an instruction is ignored, which a sentence in a prompt cannot promise.

**Three kinds.** The distinction is structural and it is what the catalogue is sorted by.

- **Reading agents** analyse and report. They cannot repair what they find, and that is the point:
  a finding and its remedy must come from different actors, or the record of the finding does not
  survive the remedy. An agent that both judges and repairs cannot be audited.
- **Acting agents** change things, inside a sandbox, and answer for what they changed against the
  diff rather than against their own account of it.
- **Conversational agents** (v8.1) hold no tool at all — they touch no repository, to read or to
  write. Their whole surface is one validated envelope per turn. Nothing they produce reaches a
  repository without a host that applies it and a human who signs.

**Reading agents emit action codes, not prose.** A finding that says *"link this commit to its
epic"* can be read by a person and by an agent, and dispatched by neither. The **Action Catalogue**
(`.asf/action-catalog.json`) defines a closed set of codes — `DOMAIN.PRIMITIVE.OBJECT` — each with
an executor, a target, an idempotency flag and a schema for its parameters. **An agent selects a
code and never invents one**: a situation the catalogue does not cover is reported as a finding
with no action, and the catalogue gains an entry. Adding one is a Dev Lead act, because the
catalogue defines what agents may propose at all.

### The catalogue

| Agent | Kind | Activated by | Produces | Cannot do |
|---|---|---|---|---|
| **Commit Gate Agent** | reads | Any push on any branch, and MR events | Per-check verdict, navigable findings, ranked actions as catalogue codes | Write to any repo, block a merge, execute what it emits |
| **ASF Compliance Agent** | reads | On demand, before a gate review or on taking over a project | Conformance report: phase, Quality Gate L1 status, `state.json` health, per-area verdict | Write, create missing artifacts, sign the gate |
| **ASF Area Agent** | reads · delegate | Another agent, sharing its workspace | One area verdict with counts, and what it could not read | Judge an area it was not asked about |
| **ASF Dev Agent** | **acts** | A bounded implementation objective, or a dispatched `CODE.GENERATE.CHANGE` | Modified files in the workspace, and a report compiled from the diff | Commit, push, open or approve an MR, modify L0/L1, plan its own work |
| **Pitch Agent** | **converses** | A person, through a host that owns the conversation | A method-neutral requirements package with provenance per field | Hold any tool, touch a repository, assign an identifier, sign |
| **Epic & Task Agent** | acts | `epic-ready.json` or `cr-approved.json` | `EpicXXX.md`, `Task.EpicXX.N.md`, and in `state.json` the epic with its tasks | Modify L0/L1, approve epics on its own |
| **Task Generation Agent** | acts | `epic-tasks-gen-<epic_id>.json` | `Task.EpicXX.N.md` and the epic's tasks in `state.json` | Generate production code |
| **Test Generation Agent** | acts | Commit on a feature branch (CI) | Playwright/Pytest tests from the acceptance criteria | Define the test strategy — that is the QA Lead's |
| **Scrum Master Agent** | acts | GitLab events, sprint end, commits | Issues from approved tasks, velocity readings (derived, never stored), the sprint-close commit, retrospective synthesis | Change backlog priority, approve a CR, split epics |
| **Documentation Agent** | acts | A change that invalidates a page; release readiness | Updated pages, release notes | Decide what is worth documenting |
| **Infrastructure Agent** | acts | Infra bootstrap, and infra changes behind a gate | Provisioned and changed infrastructure | Anything without a Dev Lead gate |
| **Pitch Translation Agent** | *to be implemented* | A pitch package marked ready | ASF artifacts from a package, with the identifiers the pitch does not assign | Sign the gate, or invent what the package does not say |
| **Code Generation Agent** | interactive | A Senior Developer, in their editor | A first draft, in session | Merge |
| **Code Review Agent** | reads | Merge request | Review comments | Approve |
| **RIB Delta Engine** | computes | An approved Change Request | The impact delta across the stack | Decide whether the change is worth it |

**Eight of the codes in the Action Catalogue name an executor that does not exist yet**, and those
codes say so: they carry `executor_implemented: false`. Saying it is the point — an action code
that resolves to nobody is worse than an absent one, because it looks dispatchable.

## 4.4 The Pitch Agent — requirements as a conversation

Requirements do not arrive written. They arrive as a person describing a problem, usually someone
who has never written a requirement and should not have to learn. The Pitch Agent interviews that
person and **writes the document while they talk**, so the interlocutor sees the effect of every
answer instead of answering into a void.

Four things make it work, and each of them is a rule rather than a feature.

**Every value says where it came from.** The person said it, a material carried it, or **the agent
inferred it and nobody said it**. The three look different, always. A document that presents an
inference with the authority of an answer lies by omission to whoever signs it.

**A requirement is never inferred.** Inference is legitimate for the glossary, for assumptions, for
context, for the intent of a diagram. Where an inference would land among the requirements, the
agent asks instead.

**The checklist is declared when the pitch opens**, every entry open — thirty-one of them for a
new product, architecture included. A checklist that appears in pieces never says what is missing,
and an agent with no finish line asks questions until the person gives up. An **open** entry
blocks delivery; a **deferred** one does not, which is the difference between not having asked and
having decided not to ask.

**Diagrams are questions.** When something is easier seen than said, the agent draws the process
*as it understood it* and asks whether that is right. Nobody recites their exception cases out
loud; everybody sees them missing in a flowchart.

What comes out is a **package that knows nothing about ASF**: no `RF-XX`, no `EpicNNN`, no path.
An elicitation agent that knows its target format writes toward it, and the first thing lost is
the question nobody asked because the template had no field for it. Turning a package into ASF
artifacts is a separate agent — in the catalogue, not yet built.

The agent needs a **host** to be useful at all: something that composes the turn's context,
applies its patches, validates them, and hands the rejections back. Without one it is a chat that
proposes edits nobody applies. The standard ships a reference host in `agents/pitch/host/`.

# 5. Startup — From Idea to First Sprint

## 5.1 The one phase that does not repeat

Startup is the only phase of ASF™ that happens once. Everything else is cyclical: sprint after
sprint the cycle begins again, artifacts update, the factory gathers speed. Startup happens once —
and what it produces determines the quality of every sprint after it.

Its job is precise: turn the stakeholders' vision — still fluid, still partial, still open to
revision — into structures the system can process. Concretely, three families of artifacts in the
right order: first `product.md` with its specifications, then `Roadmap.md` and `ProductLog.md`
with the first epics sketched, finally the Prompt Stack files that turn project context into
instructions agents can act on.

**The order is binding.** The Prompt Stack can only be initialised when requirements are stable
enough to give coherent context. The first epics can only be generated when the roadmap has a
direction. The first Sprint Planning can only be called when Quality Gate Layer 1 is passed. Each
block opens the next; none can be skipped.

> **Quality Gate Layer 1** — the condition that governs all of Startup. Five checks:
> (1) `architecture.json` initialised with components, tech stack, integrations and the first ADRs
> in the `adLog`; (2) `product.md` complete with vision, target user, look & feel, linked designs
> and sketched acceptance criteria for the candidate epics; (3) `deployment.md` aligned to the
> pipeline in `infra/`; (4) `AGENTS.md` initialised for every layer repository with context,
> conventions and domain rules; (5) the Epic Board populated with at least three sprints of
> backlog.
>
> **The gate is passed when every L0/L1 file is signed** — one `prompt_stack[]` entry per file in
> `state.json`, a person and a date — and the five checks are what those signatures certify. A
> signature has to be renewed when its file changes after it was given; git history shows which.
> There is no separate gate record: since v8.3 `state.json` has no `gates` section.
>
> **If one point is missing, Startup extends. Never the sprint.**

## 5.2 The three blocks

### Block 1 · Requirements

*PM / Product Owner · Stakeholders — and, since v8.1, a pitch*

The PM runs structured elicitation: workshops, interviews, analysis of existing documentation,
rapid prototyping where it helps surface what the client has not yet articulated. Where a pitch is
used, the same work happens as a conversation and produces a package that is then translated into
requirement files — with the advantage that every value carries its origin, and what was never
asked is recorded as deferred rather than forgotten.

Everything converges into `product.md` — not a report, not a presentation, but the artifact agents
will read as Layer 1 for the life of the project. Every functional requirement is indexed there;
its detail, and every non-functional requirement with its metric and threshold, sits in a file
under `docs/requirements/`. Where the project writes user stories, they go in `docs/stories/`,
each citing the functional requirements that realise it. Designs, system specifications,
third-party APIs: everything that defines the perimeter is referenced from that index.

The Dev Lead reads `product.md` already at this stage, because this is the cheapest moment to
catch an ambiguity or a gap — long before it propagates to the agents.

**GitLab:** first issues opened for high-priority requirements; the label system configured at
group level so it cascades to every repository.
**Gate:** the Dev Lead certifies that `product.md` can support generating the first epics. If it
cannot, Block 1 is not closed.

### Block 2 · Roadmap and epics

*PM / Product Owner · Epic & Task Agent*

With `product.md` stable, the PM builds the product's view over time and the initial ordering of
features. The first agent of Startup enters here: the Epic & Task Agent reads `product.md` and
supports generating the first `EpicXXX.md`, each with objective, scope and sketched acceptance
criteria. The PM brings the strategic view; the agent brings the ability to turn it into
structures coherent with the Prompt Stack. Everything that is not text — the epic's dependencies
and priority, the requirements its tasks cite — goes into `state.json`, and an epic enters it
together with its tasks, at least one, in the same commit as its file.

Every generated epic is validated by the Dev Lead before it enters `ProductLog.md` and the Epic
Board. The validation is not formal: the Dev Lead checks that the sketched criteria are
implementable with the chosen stack and that the estimated complexity is realistic for the size of
a sprint.

**GitLab:** Epic Board with Now/Next/Later; milestones created and linked; iteration cadence set
to one week.
**Gate:** the PM approves the roadmap with the client. The Dev Lead validates the epics before
they are committed to `docs/`.

### Block 3 · Prompt Stack initialisation

*Dev Lead*

Block 3 belongs to the Dev Lead alone and is the most critical of the whole Startup: the quality of
what is written here determines the quality of every agent's output for the life of the project.

**`AGENTS.md`** is initialised separately for each layer repository — `fe/`, `be/`, `api/` — with
that layer's technical context: stack, naming conventions, approved patterns, anti-patterns,
domain rules the generated code must respect.

**`architecture.json`** is the project's structured architectural artifact, conforming to the
KArchitecture standard: logical components with their stack, integration contracts between them,
and the **Architecture Decision Log** — a structured index of every architectural decision taken.
The narrative of each ADR lives in the file its `docRef` points to, the same pattern the functional
requirements use. *Since v8.0 this is the only architectural artifact:* the Markdown that used to
sit beside it was absorbed, because two files describing one architecture disagree and the
disagreement is found by whoever trusted the wrong one.

**`deployment.md`** is aligned to the pipeline configured in `infra/`: environments, release
procedures, configuration variables, rollback instructions.

**`instructions.md`** holds the project's operating instructions that belong to neither
architecture nor deployment: testing conventions, non-standard naming rules, local process
decisions.

These four, with `product.md` from Block 1, are **Layer 1** of the Prompt Stack — the context every
agent loads at every session.

**GitLab:** repository structure created (`docs/`, `fe/`, `be/`, `api/`, `infra/`); CI/CD
initialised; branch protection on `main`.
**Gate:** every L0/L1 file is signed — the Dev Lead's four, the PM's `product.md`, `Roadmap.md`
and `ProductLog.md` — and Quality Gate Layer 1 is passed. Only then can the first Sprint Planning
be called.

## 5.3 Why compressing Startup costs more than it saves

Startup takes time — typically one or two weeks depending on the complexity of the project and the
maturity of the documentation available. That time is an investment with a direct return on the
speed of every sprint after it.

A precisely initialised Prompt Stack sharply reduces how much the Senior Developer has to correct.
A complete `product.md` removes ambiguities that would otherwise surface during execution as
unplanned Change Requests. A passed Quality Gate — every L0/L1 file signed — is the guarantee that
the first sprint starts from solid ground and that thirty days to first delivery is reachable.

The temptation to compress Startup to reach the first sprint sooner produces the opposite: agents
generating code coherent with incomplete instructions, Senior Developers correcting structurally
instead of marginally, sprints that slow down instead of accelerating. The rule is simple —
**Startup extends until the gate is passed. Never the sprint before the gate.**

# 6. Infra Bootstrap — Infrastructure Automation

## 6.1 A dedicated agent for a critical moment

Before the first sprint, the infrastructure has to exist — not as a technical prerequisite but as
a complete operating structure: a Kubernetes cluster with separated environments, CI/CD pipelines
configured and working on every repository, the GitLab project structure with its boards, labels,
runners and protected variables. All of it ready, documented and validated by the Dev Lead before
a single issue is opened.

The **Infrastructure Agent** does this work in the Infra Bootstrap phase, between Startup and the
operating cycle. It produces three families of artifacts in sequence, separated by non-negotiable
human gates: `deployment.md` as the shared specification, the Pulumi/Terraform code as declarative
infrastructure, and the GitLab structure as the team's operating environment.

It does not only work at the start. Through the DevSecOps cycle, whenever the system needs an
infrastructure change — a new application layer, node pools to scale, a Kubernetes upgrade, a new
pipeline stage — the agent proposes a plan the Dev Lead / Architect approves before the apply.
The infrastructure lives, evolves, and stays aligned to the document that describes it.

## 6.2 The three blocks

**Block 1 · Generate `deployment.md`.** The agent gathers the project's parameters from
`architecture.json` and from what was agreed with the Dev Lead: cloud provider, cluster type,
node pools, environments, data residency constraints, availability requirements. From those it
produces `deployment.md` in operational form: cluster topology, namespaces per environment, deploy
and rollback procedures, configuration variables, CI/CD runner access. The document goes to the
Dev Lead for review — **it is the specification that governs everything after it, and no infra
code is written until it is approved.**
*Gate: the Dev Lead signs `deployment.md`. If it is incomplete or incoherent with the
architecture, Block 1 repeats.*

**Block 2 · Kubernetes provisioning.** With the specification approved, the agent generates the
Pulumi (Python) or Terraform (HCL) code in `infra/`. Before the apply it runs the plan: the Dev
Lead reads the human-readable output and approves explicitly. **No cloud resource is created
without that approval.** After the apply: the cluster is live with separated dev/staging/prod
namespaces, Argo CD installed as the GitOps controller, cert-manager handling TLS, Ingress NGINX
handling routing. The kubeconfig is stored as a protected GitLab variable for the runners.
*Gate: the plan is approved before the apply, per environment — dev first, then staging, then
prod.*

**Block 3 · GitLab project bootstrap.** With the cluster live, the agent builds the project's
organisational structure through the GitLab API or the Terraform provider: the group, the standard
repositories (`docs/`, `fe/`, `be/`, `api/`, `infra/`), the group-level label system that cascades
to every child repository, branch protection on `main`, initial milestones aligned to the roadmap,
the four group boards (§10.3), protected CI/CD variables per environment, runner registration, and
a `.gitlab-ci.yml` template per repository with the full set of stages.
*Gate: the Dev Lead runs a smoke test on every repository — a test MR with a green pipeline. Only
then can the first Sprint Planning be called.*

## 6.3 The tools

One criterion governs the selection: every tool must be drivable programmatically by the agent,
must produce artifacts traceable in Git, and must integrate natively with the GitOps cycle Argo CD
runs on the cluster.

| Tool | Role |
|---|---|
| **Pulumi (Python) / Terraform** | Infrastructure as code: cluster, node pools, networking, storage, load balancer, DNS. Pulumi is preferred for conditional logic and because Python is what the agents are fluent in |
| **Helm** | Kubernetes package manager. Each application is a chart with per-environment values, covering Deployment, Service, Ingress, ConfigMap, Secret |
| **Argo CD** | GitOps controller: keeps the cluster synchronised with what `infra/` declares. Every merge propagates; drift is detected and rollback is a `git revert` |
| **cert-manager** | Automatic TLS through Let's Encrypt, installed in Block 2 |
| **Ingress NGINX** | HTTP/S routing to the services: virtual hosts, path routing, rate limiting |
| **GitLab API + Terraform provider** | Builds the whole project structure programmatically |
| **gitlab-runner (kubernetes executor)** | Runs CI jobs as pods in the cluster's `ci/` namespace: automatic scaling, isolation per job, native access to registry and kubeconfig |

## 6.4 The DevSecOps pipeline

Once the cluster is live, CI/CD runs entirely on Kubernetes: every job is scheduled as a pod, with
automatic scaling and complete isolation between concurrent jobs. This removes the need for
dedicated runner machines and aligns testing and building with the environment the code will
actually run in.

The stages are standard: **build** produces the image and publishes it; **test** runs the generated
suite on a dedicated pod; **security scan** applies GitLab's SAST and DAST; **deploy staging** is
automatic on merge to `main`; **deploy prod** requires the Dev Lead's manual approval — the last
human gate before production.

> **Security is part of the cycle, not a final audit.** SAST and DAST in the pipeline mean every
> merge request is analysed for vulnerabilities before the merge. The Dev Lead reads the security
> report alongside the review before approving. Security is an automatic artifact of every merge
> request, not a separate process at the end of the sprint.

**Since v8.0 the pipeline carries one more reader.** The **Commit Gate Agent** runs on every push,
on any branch, including the first push of a new branch — before a merge request exists. It judges
one commit against a configurable checklist: is it attached to its epic and task, did the change
need tests, were they run, does it warrant static analysis, does it invalidate documentation. Its
verdict is **advisory**: whether a `block` stops a merge is a CI or MR rule the project owns. An
agent that both judged and enforced would leave no independent record of what it found.

Five outcomes, not two: `pass`, `warn`, `fail`, `not_applicable`, and `not_verifiable` — evidence
the agent could not read. Collapsing the last into a failure accuses people of what the agent could
not see.

## 6.5 Infra changes during the operating cycle

Infrastructure is not static. Across twelve months the need to change it comes up regularly: a new
service needs a namespace, load grows and node pools must scale, a Kubernetes version needs an
upgrade, the pipeline needs a compliance stage. Every change follows the same path: the agent
proposes a plan, the Dev Lead approves, the agent applies, and `deployment.md` is updated to
reflect the new state.

Infra changes are tracked as merge requests on `infra/` with an `~infra-change` label, which gives
a complete audit trail: who proposed it, who approved it, when it was applied, what the state was
before and after. Argo CD detects any drift between what `infra/` declares and what the cluster
actually is, and notifies the Dev Lead.

> **The infrastructure gate.** No change to the cluster happens without the Dev Lead / Architect's
> gate — not in Startup, not during the cycle. The Infrastructure Agent proposes, plans, generates
> the code and documents it. **The decision to apply a change to a production environment always
> belongs to a human with full technical view of the system.**

# 7. KStudio — The Operating Surface

> **The product was called CronStudio until v8.0.** The v7.4 edition of this document names it
> that twenty-nine times, and its state file as `docs/.cronstudio/state.json`. It is **KStudio**,
> and the file is `docs/.asf/state.json`.

## 7.1 Role and architectural philosophy

KStudio is the application that makes ASF™ deliverable as an industrialised service. Its job is to
remove the manual glue between parts that already exist and already work — GitLab, the LLM
providers, Pulumi, the Prompt Stack files — and replace it with a structured surface and CI
pipelines that activate agents deterministically.

**KStudio is not a custom orchestrator and does not introduce a state database of its own.** GitLab
is the system of record: every datum of a project's state lives there, as files under `docs/`, as
issues, merge requests, pipeline logs and protected variables. KStudio reads and writes through the
API, keeps at most an exact cache of `state.json`, and changes the state only by committing to
it; operational data that is not part of the state — who is working on an epic right now — stays
in KStudio and never enters the file. **A team that stopped using KStudio tomorrow would find its
project intact in GitLab**, with no dependency on BIT infrastructure. That property is the point,
not a side effect.

## 7.2 The three modules

**Project Bootstrap** activates the Infrastructure Agent for a new project through a guided
four-step wizard: project parameters; GitLab setup; cloud and infrastructure; bootstrap. Progress
is shown live by polling the CI API. **The gates between blocks are GitLab CI environment
approvals**: the Dev Lead is notified, reads the plan the agent proposed, and approves or rejects
in the interface. No apply happens without an explicit gate. As the wizard's last step, KStudio
creates `docs/.asf/state.json` with the project structure prefilled.

**Requirements and Prompt Stack.** The structured editor for Layer 1, where the PM works for the
whole engagement: meeting notes, thematic summaries, functional analysis, linked designs and
prototypes. These are presented as guided sections rather than a free editor, because each section
maps to a specific place under `docs/requirements/` and a specific field of `product.md`. **Every
save is a commit. The history of the requirements is the history of the commits on `docs/`.**

When the PM marks a section ready, KStudio commits a trigger under `docs/triggers/` and the Epic &
Task Agent pipeline starts, reads the stack from the root down, generates the epic and task files
and commits them for the Dev Lead to validate. A Change Request follows the same path with one step
first: the **RIB Delta Engine** computes the impact — which requirements, epics and tasks are
touched, and the effort estimate. Only after PM and Dev Lead approve does the cascade propagate
top-down: `product.md` → the affected `RF-XX.md` → `EpicXXX.md` → `Task.md`.

**Project dashboard.** The aggregate view of every active project. It does not duplicate GitLab —
it reads it and translates it into the language of ASF™: the current sprint with its velocity and
burndown — computed from `state.json` and git history, never stored — and detected blocks; the
state of each Prompt Stack artifact with its last update, whether its signature is still current,
and any divergence from the last agent generation; the agent pipeline with its runs and logs; the
current release with its merge requests and notes.

## 7.3 `docs/.asf/state.json` — the project contract

**KStudio has no database for the project's state.** A project's whole state lives in GitLab as
committed files, and the central contract is `docs/.asf/state.json` — a typed, versioned JSON
file whose presence, with a valid `meta.schema_version`, is what makes a repository a
recognisable ASF™ project.

**Since v8.3 it holds the state and nothing else.** Statuses, planning decisions and references
live in `state.json`; titles, descriptions and acceptance criteria live in the Markdown files;
nothing is copied from one to the other, and nothing that can be computed is stored. Its sections:
`meta` (the schema version, and the ASF version the project follows), `project` (its name and its
repositories), `prompt_stack[]` (one signature per L0/L1 file), `sprints[]`, `roadmap[]` (the
delivery stages), `epics[]` with their `tasks[]` inside them, `requirements` (functional and
non-functional), `user_stories[]` and `bugs[]`; the dashboard sections — the agent pipeline log
among them — are optional. **A key the schema does not list is an error.** Each section, with its
rules, is described in `product.md` §12; the exact contract is `.asf/schema/state.schema.json`.

**What can be derived is not stored.** Velocity — the current one, the final one of a closed
sprint, and the average of the last three closed sprints that is the planning capacity — the
burndown, an epic's points, the epics a requirement or a bug belongs to, a story's status, who
changed what and when, and whether Quality Gate Layer 1 is passed are all computed from
`state.json` and git history. The v8.2 sections that held them — `gates`, `milestones`,
`velocity_history`, `traceability`, the root list of tasks — are gone.

**A signature lives on what it signs.** An epic is `done` exactly when it carries `validated_by`
and `validated_at` — a person, written in the same commit as the status; each L0/L1 file is
signed by its `prompt_stack[]` entry; a non-functional requirement is verified by `verified_by`
and `verified_at`. A person is written as `Name <email>`; a role is not a signature, and an agent
never signs. Human gates — approvals, trigger files — are unchanged.

Writes go through **double bifurcation**: read the file and keep its commit SHA; mutate in memory;
commit specifying the SHA that was read. If another writer got there first, GitLab answers 409 and
the backend starts again. This gives atomicity without explicit locks, using GitLab's own
mechanism.

> **The schema is the contract, and the tools follow it.** `state.schema.json` is written in the
> standard; backend models, TypeScript types and Pydantic models are made to match it, and where a
> tool and the schema disagree, the tool is wrong. `meta.schema_version` is the schema's own
> version: an addition raises the minor; a breaking change raises the major and needs a migration
> script.
>
> **`meta.schema_version` must match the schema you validate against**, and no top-level key is
> added or dropped without a matching schema update behind a Dev Lead gate. An agent that writes
> `state.json` **commits immediately, in the same CI job**: a write without a commit is an
> inconsistent state, and KStudio would be showing data GitLab has not received.
>
> **Checked, not trusted.** `tools/validate-stack.py` validates `state.json` and the frontmatter of
> every artifact against their schemas, then the rules that cross files: unique ids, references
> that resolve, an epic in at most one sprint, no dependency cycles, a file for every artifact and
> an artifact for every file, the `product.md` index equal to the RFs in `state.json`. A project
> copies it to `docs/tools/` and runs it in CI. A v8.2 project is converted once, by
> `tools/migrate-to-8.3.py`: the v8.2 names are not read. The upgrade path is in the CHANGELOG.

## 7.4 How agents are activated

Two patterns. A **trigger file** is a JSON file committed under `docs/triggers/` — **Layer 4 of the
Prompt Stack**; the pipeline fires on the path change, reads the stack from L0 down, calls the
provider configured in `llm-config.json`, commits the output and **deletes the trigger it
consumed**. A **trigger event** fires on a change to a specific file, with no intermediate file —
more direct, and right for reactive pipelines. Every agent updates the pipeline section of
`state.json` as the last step of its job.

| Trigger | Agent | Output |
|---|---|---|
| `epic-ready.json` | Epic & Task Agent | `docs/epics/EpicXXX.md` + `docs/tasks/Task.*.md` |
| `cr-approved.json` | Epic & Task Agent (CR cascade) | Epics and tasks updated top-down |
| `epic-tasks-gen-<epic_id>.json` | Task Generation Agent | `Task.EpicXX.N.md` + the epic's tasks in `state.json` |
| `sprint-close.json` | Scrum Master Agent | Retrospective synthesis in `docs/retro/` |
| `infra-bootstrap.json` | Infrastructure Agent | `deployment.md` + the Pulumi code |
| `release-ready.json` | Documentation Agent | Release notes on the GitLab Release |
| *any push, any branch* | **Commit Gate Agent** | A verdict, findings, and ranked action codes |

The payload and report schemas live in `triggers/schema/`. The Scrum Master Agent is not triggered
by KStudio but by scheduled pipelines and GitLab webhooks on issue and merge request events;
KStudio shows its output without activating it.

## 7.5 Stack and deployment

A React frontend and a FastAPI backend. **The backend is the only component holding the GitLab
token**; the frontend never calls GitLab directly, and every call to an LLM provider is made by the
backend — in CI jobs and at runtime — never by the browser. What it persists is a short-lived
cache of recent API calls, at most an exact copy of `state.json`, and the operational data that is
not part of a project's state (§7.1).

Deployment happens as the last step of Infra Bootstrap Block 3: when the client's GitLab group is
ready, KStudio is deployed into the project's cluster and configured with the group's credentials.
One BIT instance can run every active project: isolation is at the level of the GitLab group and
the Kubernetes namespace. The project list shows only what the user can see in GitLab, and
**permissions mirror GitLab roles** — maintainers see the gates, developers see the dashboard,
guests see the release. Authentication is GitLab OAuth, and there is no parallel credential system.

## 7.6 The artifacts — one file, one entry

Since v8.3 every artifact of a project has a file for its text and an entry in `state.json` for
its state, and neither repeats the other. Three of them are new as files.

| Artifact | File | The file holds |
|---|---|---|
| Functional requirement | `requirements/RF-XX.md`, or only its row in the `product.md` index | Description, acceptance criteria |
| Non-functional requirement | `requirements/RNF-XX.md` | The requirement, its metric and threshold, how it is verified, its scope |
| Epic | `epics/EpicXXX.md` | Objective, scope, epic acceptance criteria |
| Task | `tasks/Task.EpicXXX.N.md` | Context, BDD acceptance criteria, prompt seed |
| Bug | `bugs/BUG-XXX.md` | Symptom, cause, expected behaviour, regression test |
| User story | `stories/US-XXX.md` | "As a … I want … so that …" |

The frontmatter of each file keeps its id, its title and a few descriptive fields, and nothing
else: a `status` or an `epic` key is an error, and so is a status line, a ✅ or a table of covered
requirements in the body. The first heading is exactly `# <id> — <title>`. Acceptance-criteria
checkboxes stay, because they are text.

**Bugs.** A bug is reported with its severity and the functional or non-functional requirements it
breaks; besides the work statuses it can be in `triage`, `not_reproducible`, `wont_fix` or
`duplicate`. It enters an epic through the task that fixes it; the tasks that fix a sprint's bugs
can be collected in an epic of kind `container`. **User stories** cite at least
one functional requirement, and their status is derived from those requirements. When an agent is
asked to develop an epic, it reads the requirements its tasks cite, the epic's non-functional
requirements and stories, and the bugs its tasks fix.

The full rules — ids, frontmatter fields, lifecycles — are in `product.md` §12; the templates are
in `instructions.md`.

# 8. SCRUM-AI™ — The Operating Cycle

## 8.1 The Prompt Stack: six levels of context

The Prompt Stack is what makes ASF™ agents coherent, predictable and improvable over time. Before
generating anything, an agent loads an ordered sequence of files — from the company root down to
the current atomic task. That composed context determines the quality of the output: the more
precise, complete and current it is, the more the generated code agrees with the project's
architecture, its domain rules and the client's expectations.

**The hierarchy is strict: every upper layer has priority over the ones below.** If
`architecture.json` defines a pattern, no epic and no task may contradict it. If `AGENTS.md` sets a
naming convention, it holds for all generated code. The rigidity is not a limitation — it is the
condition that lets the factory produce coherent code while several agents work in parallel on
different parts of one system.

| Layer | Files | Contents | Owner |
|---|---|---|---|
| **L0** | `AGENTS.md` | Universal context: the founding rules, the identity model, the gate, the agent catalogue, authority over documents | Dev Lead, by explicit deliberation |
| **L1** | `product.md` · `architecture.json` · `deployment.md` · `instructions.md` · `Roadmap.md` · `ProductLog.md` | Product, architecture, deployment, the project's operating instructions, the roadmap and the prioritised backlog | Dev Lead or PM — never an agent alone; `Roadmap.md` and `ProductLog.md` are the PM's |
| **L1.5** | `requirements/RF-XX.md` · `requirements/RNF-XX.md` | One file per functional requirement, with acceptance criteria in BDD; one per non-functional requirement, with its metric, threshold and verification | RF: KStudio backend and the Epic & Task Agent, behind a Dev Lead gate · RNF: after PM approval |
| **L2** | `epics/EpicXXX.md` | Objective, scope, epic acceptance criteria | Epic & Task Agent, validated before commit |
| **L3** | `tasks/Task.EpicXX.N.md` | The atomic unit of work, with its prompt seed | Epic & Task Agent, autonomously after planning |
| **L4** | `triggers/*.json` | CI activation files | Whoever fires the trigger — **deleted by the pipeline that consumes them** |

> **`AGENTS.md` is L0 since v8.0.** The entry point used to be `CLAUDE.md`, and the rename is not
> cosmetic: the file is read by every agent, not by one vendor's. `CLAUDE.md` remains as a pointer
> to it and never as a copy.
>
> **L4 is a layer, not a detail.** A trigger file is context: it carries the parameters of the
> activation. It is the only layer that is deleted by the thing that reads it, which is what stops
> a pipeline firing twice on one event.

**The RF resolution rule, mandatory for every agent:** look for `requirements/RF-XX.md` → fall back
to the `product.md` entry → **raise an explicit error if neither exists.** A missing requirement is
a blocking error, never something to infer.

**Conflicts.** Since v8.3 every status, link and planning decision has one source, `state.json`,
so no precedence between files applies to them: the v8.2 rule `state.json` > `product.md` >
`RF-XX.md` > `EpicXXX.md` is gone. A conflict of text follows the layer hierarchy above.

## 8.2 How the factory learns

A pattern that emerges during a sprint does not stay in the sprint. In Retrospective, the Dev Lead
applies the **promotion rule**: if the pattern holds for the current project, it goes into
`architecture.json` or the affected layer's `AGENTS.md`; if it holds for every BIT project, it goes
into the company-wide L0 **by explicit deliberation**, never by accumulation.

This is what makes the stack an asset rather than documentation. Each sprint leaves the next one a
slightly better context, and the improvement is written down in a file an agent reads rather than
in a habit a person has.

## 8.3 Why a sprint is one week

A traditional Scrum sprint runs two weeks because the human cognitive cycle — understanding the
requirement, designing, implementing, testing, reviewing — needs that long to produce something
verifiable. In SCRUM-AI™ the implementation phase is accelerated non-linearly: the Senior Developer
no longer writes code from nothing, they validate and refine what the agent produced. **The
bottleneck moves from execution to validation, and validation is much faster than production.**

The compression is conditional. `architecture.json` and `product.md` must be current and complete
before planning starts. **If Layer 1 is incomplete, agent speed amplifies the ambiguity instead of
reducing it** — producing code quickly in the wrong direction. Before every sprint the Dev Lead
checks that Layer 1 is ready, and a Layer 1 file changed since it was signed is signed again: if it
is not ready, refinement extends. Never the sprint.

## 8.4 The phases

Four phases and one asynchronous event. The phases are sequential; the Change Request can
interrupt the cycle at any moment and triggers a cascade through the stack.

### Sprint Planning — day 1, ~2 hours

*PM + Dev Lead + Epic & Task Agent*

Two movements in parallel. The PM brings the candidate epics and presents them with their full
specifications. The Dev Lead assesses technical feasibility, checks that `architecture.json`
supports them, and approves what enters the sprint. Meanwhile the Epic & Task Agent generates the
task files for each approved epic — granular criteria, technical notes, the prompt seed. The Dev
Lead reviews those before the Scrum Master Agent turns them into issues on the current iteration.
Planning an epic is one commit: the epic with all its tasks enters `epics[]` of `state.json`, and
its id enters the sprint's `epic_refs` — an epic is in at most one sprint, and one in none is in the
backlog. Capacity is the average velocity of the last three closed sprints, computed, not stored.
**The sprint is formally open only when the issues exist and are assigned**; in `state.json` it
becomes `active`, with its start and end dates, and at most one sprint is active at a time.

*Reads: `architecture.json`, `product.md`. Writes: `EpicXXX.md`, `Task.EpicXX.N.md`,
`ProductLog.md`, `state.json`.*
*Gate: the Dev Lead approves every task before commit; the PM confirms the scope.*

### Sprint Execution — days 2–5

*Asynchronous. The board is the source of truth, not the standup.*

The Senior Developer opens a task, starts a session, and the coding agent loads the whole Prompt
Stack as context — from L0 down to the current task. The first draft is generated; the developer
validates and refines it, handles the edge cases that need domain judgement, and opens the merge
request. The Code Review Agent analyses the diff and produces structured comments. The Test
Generation Agent turns the task's acceptance criteria into tests, and CI runs them on every push.
**The Dev Lead reads the reports and makes the final review: theirs is the only signature that
opens a merge to `main`.** The Scrum Master Agent updates issue states as commits land and raises a
notification when an issue sits still for more than twenty-four hours.

**Since v8.0 the Commit Gate runs alongside**, on every push, before the merge request exists — so
a commit that is not attached to its epic is known at the commit and not at the review.

**Closing a task is one commit:** its `status` in `state.json` becomes `done` and its acceptance
criteria are checked in the task file — nothing else, no counter and no timestamp. A functional
requirement becomes `done` when all its acceptance criteria are implemented and tested. An epic
becomes `done` only when a person signs it, `validated_by` and `validated_at` in the same commit,
after the Senior Developer's verification. The Definition of Done and every closing step are in
`instructions.md` §15.

*Reads: the layer's `AGENTS.md`, `architecture.json`, `product.md`, the epic, the task — every
session. Writes: the task's status in `state.json` and its checked criteria at closure; the task
file's text only where unforeseen complexity emerges, with a note in the Retrospective.*
*Gate: approve or reject on every merge request. **Not delegable.***

### Sprint Review — day 5, with the client, on staging, one hour

The PM presents the results on staging — not slides, not screenshots: working software. The Dev
Lead brings the technical numbers. The Documentation Agent has already generated the release notes
from the iteration's merge requests. The client accepts or gives feedback; **if the feedback
changes the specification, the PM updates `product.md` before the Retrospective**, so the change is
recorded in the source of truth before it propagates to the backlog. `Roadmap.md` is updated
without exception: it is the document that certifies, sprint after sprint, that the factory is
building in the right direction.

*Gate: the client accepts or gives feedback; the PM updates the roadmap before closing; the Dev
Lead gives go/no-go for production.*

### Retrospective — same day, internal, 45 minutes

The Scrum Master Agent prepares the objective part: velocity (computed from the tasks that are
`done`, never stored), cycle time, the merge requests with the most comments — a signal of
underestimated complexity — and the pipeline failure rate. From those numbers the team identifies
the patterns that emerged: a better way to structure a prompt seed, an anti-pattern in generated
code, a domain rule missing from the stack. For each, the Dev Lead applies the promotion rule of
§8.2. **Every decision taken in Retrospective becomes a change to the Prompt Stack before the next
cycle starts** — otherwise it was not a decision, it was a conversation.

**Closing the sprint is one commit:** the sprint's `status` becomes `closed` with its `closed_on`
date, and its unfinished epics normally move to the next sprint's `epic_refs`; nothing else is
written. Its final velocity is the points of its `done` tasks — not frozen: it rises if one of
them completes later. The retrospective summary goes to `docs/retro/`, not to `state.json`. The
steps are in `instructions.md` §15.

## 8.5 Change Request — the asynchronous event

A Change Request is a stakeholder-requested modification after planning has started. It is the one
event that can interrupt the cycle, and it has a mandatory shape.

The PM opens it. The **RIB Delta Engine** computes the impact before anyone decides anything:
which requirements, epics and tasks are touched, and what it costs. **PM and Dev Lead both sign.**
Only then does the Epic & Task Agent propagate the cascade **top-down**: `product.md` → the
affected `RF-XX.md` → `EpicXXX.md` → `Task.md` → `state.json`.

The direction is not negotiable. A change applied bottom-up — patching a task because it is the
fastest place to patch — leaves the requirement saying one thing and the code doing another, and
nothing detects it until the next review.

# 9. Tech Stack — Tools and Repositories

## 9.1 The tools

Every tool occupies a precise role in the cycle and is chosen for the function it performs, not
for preference.

| Tool | Role | Used by |
|---|---|---|
| **Editor + coding agent** | Where the Senior Developer works with code generation, with the whole Prompt Stack loaded as persistent context | Senior Developers, Dev Lead |
| **GitLab Premium** | The factory's nervous system: source control, CI/CD and all the Scrum machinery — iterations, epic board, milestones — in one environment, which removes the split between the planning tool and the development tool | Everyone |
| **GitLab CI/CD** | Automatic pipeline on every push: test, lint, security scan, staging deploy — and, since v8.0, the Commit Gate | Agents + infrastructure |
| **GitLab Duo** | The Code Review Agent: analyses every merge request before the Dev Lead's review | Code Review Agent |
| **LLM provider** | The cognitive engine of every automated agent, configured per project in `llm-config.json`: Anthropic, OpenAI-compatible, or a local endpoint | Agents |
| **Playwright / Pytest** | The frameworks the generated tests are written in | Test Generation Agent, QA Lead |
| **Slack** | Asynchronous team communication; where the Scrum Master Agent raises blocks and ceremonies | Team + Scrum Master Agent |

> **Since v8.0 the agents run on a control plane, not on scattered scripts.** An agent is a stored
> definition — prompt, permissions, budgets, tool grants — versioned where it is installed, and the
> repository ships each one as an importable configuration under `agents/<agent>/`. A prompt is
> configuration of an installation, not source code of a product: the same agent deployed for two
> clients has two different prompts, and the model catalogue moves without a release.

## 9.2 The repository structure

Every client project lives in a **GitLab Group**. The group is the fundamental organisational
unit: boards, labels, iterations and epics are defined there and cascade to every child
repository. This is not a convention — it is what lets the Scrum Master Agent watch velocity
across every repository at once, and the Dev Lead apply labels and branch protection once for the
whole project.

**The physical separation between prompt stack and code is deliberate.** `docs/` holds everything
that guides the agents; the technical repositories hold what the agents produce; `infra/` holds the
executable automation that `deployment.md` describes in words.

| | |
|---|---|
| **`docs/`** | The whole Prompt Stack: `AGENTS.md`, `architecture.json`, `product.md`, `deployment.md`, `instructions.md`, `Roadmap.md`, `ProductLog.md`, `requirements/` (RF and RNF files), `epics/`, `tasks/`, `triggers/`, `.asf/` (with `state.json` and its schemas) — and beside it, since v8.3, `stories/`, `bugs/` and `tools/` (the validator the project runs in CI). The factory's brain, and the single source of truth for every agent |
| **`fe/`** | Frontend code, with the layer's own `AGENTS.md`. Owner: the FE Senior Developer |
| **`be/`** | Backend code, with the layer's own `AGENTS.md`. Owner: the BE Senior Developer |
| **`api/`** | API contracts and OpenAPI specifications, with the layer's `AGENTS.md`. Owner: Dev Lead |
| **`infra/`** | Infrastructure as code, pipelines, environment configuration. The executable complement of `deployment.md`. Owner: Dev Lead |

## 9.3 The mapping between files and GitLab entities

Every file in `docs/` has a counterpart in GitLab, and the relation is not duplication: **the file
is the narrative and technical specification, the GitLab entity is the operational tracker.** The
Dev Lead is responsible for keeping the two aligned.

| | |
|---|---|
| `Roadmap.md` ↔ **Milestones** | The file tells the direction in strategic language; the milestones measure operational progress with automatic completion. Both are updated after every review |
| `ProductLog.md` ↔ **Epic Board** | The file is the prioritised narrative source of truth; the board is the operational planning view |
| `EpicXXX.md` ↔ **Epic** | The file holds the specification — objective, scope, acceptance criteria; its dependencies and status are in `state.json`; the GitLab epic is the tracker with its child issues |
| `Task.EpicXX.N.md` ↔ **Issue** | The file holds the technical context for the agent, including the prompt seed; the issue is the operational workflow with assignee, labels and iteration |
| `AGENTS.md` ↔ **(nothing)** | It has no GitLab equivalent. It is pure cognitive context, not a tracking artifact |
| `deployment.md` ↔ **`infra/`** | The human-readable runbook and the executable automation. They must stay aligned; the Documentation Agent propagates changes from one to the other |

## 9.4 Why GitLab Premium is a functional requirement

Iterations, the Epic Board, Milestones with automatic completion, and Duo review are not
conveniences the team happens to like: they are the entities the model's artifacts map onto.
Without them the mapping in §9.3 has no right-hand column, and the Scrum Master Agent has nothing
to update. It is a functional requirement of the operating model, not a licensing preference.

# 10. Detail

## 10.1 `AGENTS.md` — the anatomy of the entry point

L0 is the first file every agent loads before any operation, and its accuracy is not a matter of
tidiness: **outdated instructions here corrupt every downstream run.** It carries the founding
rules, the identity model, the gate, the agent catalogue, the label system, and — the part that is
easy to skip and expensive to skip — **authority over documents**.

That table says, for each artifact, who may change it and whether an agent may ever commit it. It
holds one invariant:

> **Nothing an agent may do is decided by an agent.** The Action Catalogue and the commit gate
> checklist define, respectively, what an agent may propose and what it is measured against. Both
> are Dev Lead territory. An agent that could edit either would be setting its own exam.

The same invariant reaches the pitch: the coverage profiles in `.asf/pitch-checklists/` decide what
gets asked at all, so adding one is a Dev Lead act.

**Commits made by agents are labelled**, in a fixed form, so that the history says which agent
acted and why — and so that an agent's work can be found, reviewed and reverted as a class rather
than one commit at a time.

## 10.2 GitLab as Scrum infrastructure

The four boards are created at group level during Infra Bootstrap and cascade to every child
repository.

| Board | What it is | Who uses it |
|---|---|---|
| **Release Planning** | Epic board: `priority::later → next → now` | The PM, for drag-and-drop prioritisation during refinement. The Epic & Task Agent reads it to find the candidates for the next planning |
| **Sprint Board** | Issues for the current iteration: `to-do → in-progress → in-review → acceptance → done \| blocked` | The team's daily view. The Scrum Master Agent moves cards as commits and merge requests land, and `blocked` fills itself when an issue sits still for more than twenty-four hours |
| **Sprint Planning** | Issues with no iteration: `later → next → now` | Dev Lead and PM, to assign issues to iterations |
| **Agent Monitor** | Grouped by `agent::` label, no iteration filter | An audit view: the Dev Lead uses it for spot checks and for debugging when an agent produces something unexpected |

**Iteration cadence:** one week — a deliberate deviation from GitLab's recommended two, made
possible by AI acceleration. Automatic rollover on; four iterations created ahead; four to ten
stories per sprint, with capacity from the last three sprints' velocity.

## 10.3 The label system

Created at group level during bootstrap through the API, cascading to every child repository.
**Scoped labels** (`::`) are mutually exclusive within their scope: an issue cannot be both
`status::in-progress` and `status::done`. `area::` and `agent::` are deliberately **not** scoped,
because one issue can touch several components and several agents.

| Scope | Labels |
|---|---|
| `status::` | `to-do` · `in-progress` · `in-review` · `acceptance` · `done` · `blocked` · `triage` |
| `priority::` | `now` · `next` · `later` |
| `type::` | `feature` · `bug` · `maintenance` · `research` |
| `area::` | `fe` · `be` · `api` · `infra` · `docs` |
| `agent::` | one per agent — **applied by the agent at intervention time, never set by hand** |

**Mandatory on every issue:** a `status::`, a `priority::`, a `type::` and at least one `area::`.

## 10.4 The paved road

In the engineering culture of organisations like Netflix, a *paved road* is a standard path built
so well that following it is easier than deviating. ASF™ is a paved road for organisations that
have never built software in-house: **every element of the system is designed to make the correct
path the easy one.**

`AGENTS.md` is the plant manual: it steers every agent toward settled patterns without a Senior
Developer re-explaining them each session. GitLab is the assembly line: every push runs tests,
review and deploy, and nobody drives the process by hand. SCRUM-AI™ is the rhythm: cadenced
ceremonies, explicit gates, no ambiguity about who decides what and when. The agents are the
robots — fast and consistent. The Senior Developers are the engineers who govern them, check the
output, and sign what goes to production.

**The system reinforces itself because every Retrospective improves it.** The patterns that
emerged update the Prompt Stack, which improves the sprints that follow. At month twelve the
client does not receive a finished project. They receive a working factory, with current manuals,
trained operators, and a production line that has been run.

# 11. Open Issues

Questions that need a decision before they bite. Each has an owner.

| | Question | Owner |
|---|---|---|
| **OI-01** | **Name of the methodology.** SCRUM-AI™ positions the method as derived from Scrum. A fully proprietary name would underline its originality and its patentability. To decide before the first public presentation | Francesco Bellifemine |
| **OI-02** | **Escalation when a sprint blocks.** The agent detects an issue stuck beyond twenty-four hours and raises it; the escalation workflow is not defined. The PM can resolve organisational dependencies, the Dev Lead technical ones — an SLA is needed | Dev Lead |
| **OI-04** | **When a sprint goes back to two weeks.** One-week compression is validated by reasoning, not yet on a real engagement. The conditions for reverting — uncontrollable external dependencies, high initial technical debt, the first weeks of onboarding — need to be written down and then measured | Dev Lead + PM |
| **OI-06** | **How autonomous the Scrum Master Agent should be** on issue states and sprint closure | Dev Lead |
| **OI-07** | **Agent API cost and the pricing model** | Francesco Bellifemine |
| **OI-08** | **A shared knowledge base as an extended Layer 0** | Dev Lead |
| **OI-09** | **Patentability of the model** | Francesco Bellifemine |

## Opened by v8.0 and v8.1

| | Question | Owner |
|---|---|---|
| **OI-10** | **Eight action codes name an executor that does not exist.** They declare it, which is the honest thing; what they do not have is a date. Which of the unimplemented agents is built first is a roadmap decision, not a catalogue one | Dev Lead |
| **OI-11** | **A pitch package does not become ASF artifacts** until the translation agent exists. Until then, a pitch ends in a signed package that somebody copies by hand — which is exactly the manual glue the model exists to remove | Dev Lead |
| **OI-13** | **Nothing propagates a version into instantiated projects.** v8.1 wrote down what a version costs and how a release is cut, and deliberately did not invent a mechanism. v8.3 records in `state.json` the ASF version a project follows (`meta.asf_version`) and ships a one-time migration from v8.2, but still propagates nothing: a project stays on the version it was born with until someone looks | Dev Lead |

## Closed since v7.4

**OI-03 — Quality Gate Layer 1 criteria.** Closed: the five checks are written into the standard
and into Chapter 5 of this document. Since v8.3 the gate is passed when every L0/L1 file is signed
in `prompt_stack[]`, and the checks are what those signatures certify — not an opinion.

**OI-05 — Standard templates.** Closed: the repository ships the L0 and L1 templates,
`.asf/architecture.json` and `decisions/decision-log.json` as empty instantiable files, and the
JSON schemas that keep what agents produce concordant — since v8.3 with the validator that checks
them across files.

**OI-12 — Where a non-functional requirement lives.** Closed by v8.3: in
`requirements/RNF-XX.md`, beside the functional requirements, with a category, a metric, a
threshold and a way to verify it. In `state.json` it is never `done`: it is `unverified`,
`satisfied`, `at_risk`, `violated` or `waived`, and the three verified statuses carry who
verified it and when. A pitch's non-functional requirements now have somewhere to land (§7.6).

---

*ASF™ Augmented Software Factory · Better Innovation Technologies · bit-farm.it · v8.3 ·
Confidential © 2026*
