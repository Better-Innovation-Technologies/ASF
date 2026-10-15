# ASF™ Prompt Stack — standard

> **ASF v8.4** · Instructions from a catalog · Francesco Bellifemine · Better Innovation Technologies

## About this repository

This is the **public distribution** of the ASF™ standard, published by Better Innovation
Technologies. It carries the Prompt Stack templates, the JSON contracts and the validators — what
you need to adopt ASF in your own projects — and it is **tagged per release** (`v8.4`, …): a tool
that instantiates a project reads a tag, never the head of `main`.

Two things are deliberately **not** here: the agent definitions and hosts, which are products of
their own, and the superseded operating models. What you find is the standard, not our factory.

Licensed under Apache-2.0 — see `LICENSE`. Issues and pull requests are welcome. The canonical
source lives inside BIT and is exported here at every release tag.

This repository holds the **ASF™ (Augmented Software Factory) standard**: the *Prompt Stack*
files every ASF project instantiates under `docs/`, the L0/L1 templates, and the JSON schemas
that keep the artifacts agents produce concordant with one another.

**The ASF™ model** is a compressed Scrum cycle in which human operators and AI agents work in
parallel — humans sign decisions and gates, agents execute and synchronise state. Context is
organised in a strict layer hierarchy, the **Prompt Stack**: `AGENTS.md` L0 → L1 → L1.5 → L2 →
L3 → L4.

## What is in this directory

| Path | Layer | Contents |
|---|---|---|
| `AGENTS.md` | L0 | Universal context for every AI agent — the entry point, read first |
| `CLAUDE.md` | — | A pointer to `AGENTS.md`, for tools that look for that name. Never a copy |
| `asf-overview.md` | reference | The factory model: agent catalogue, human roles, KPI, Quality Gate L1, repository layout, v8.0 vocabulary. Load on demand |
| `product.md` | L1 | Product identity, ASF™ process model, RF index |
| `deployment.md` | L1 | K8s runbook, triggers, pipelines, GitLab integration |
| `instructions.md` | L1 | Dev rules, sprint execution, artifact formats, testing, label system — composable from `instructions/` (v8.4) |
| `CHANGELOG.md` | — | Decisions taken about **the standard itself** — not a project template. Also **how the standard is versioned**: what a number costs a project already instantiated, the upgrade note every version carries, and how a release is cut |
| `operating-mode/` | reference | The Operating Mode presentation of the standard (`index.html`, self-contained). Versioned here so it cannot drift silently |
| `agents/` | reference | **Agent specifications**, one directory per agent: what it is for (`.md`), how to install it (`.import.yaml`), and — where the agent's contract asks a caller to do half the work — a reference `host/`. Conventions in `agents/README.md` |
| `decisions/decision-log.json` | — | Decision Record register (**template**, ships empty); schema in `decision-log.schema.json` |
| `triggers/schema/` | L4 | JSON schemas for CI agent activation files and reports |
| `.asf/architecture.json` | L1 | The architectural artifact (KArchitecture): tech stack, repo layout, components, integrations, patterns, domain rules, and the ADR log with its rationale |
| `.asf/action-catalog.json` | — | The Action Catalogue: the closed set of remediation action codes and their primitives |
| `.asf/pitch-checklists/` | — | The coverage profiles a pitch is opened with: what that kind of conversation must touch. Installation configuration, not prompt content (D-8.9) |
| `.asf/schema/` | — | Schemas for `state.json` (single source of truth), the frontmatter of the artifact `.md` files (`frontmatter.schema.json`, one `$def` per folder), `llm-config.json`, the Action Catalogue, the Commit Gate checklist, the **pitch package** (the contract between a pitch and whatever translates it) and the pitch coverage profiles |
| `tools/` | — | `validate-stack.py`, the Prompt Stack validator: both schemas plus the cross-file rules they cannot express. **Projects copy it to `docs/tools/` and run it in CI.** `migrate-to-8.3.py` converts a v8.2 `docs/` tree once; it is run from here, never copied |
| `official/` | — | The **Operating Model**: the standard described in full — the manual and the diagram — as documents rather than as files. What circulates outside the team |
| `official/old/` | — | Superseded editions, kept because a project may still be running on one |


**Templates and standard, told apart.** `.asf/architecture.json` and
`decisions/decision-log.json` ship empty on purpose: they are instantiated into a project and
filled there. ASF is a standard — it has no product and no architecture of its own — so nothing
in them describes this repository. Decisions about the standard go in `CHANGELOG.md`.

**A project declares the version it conforms to, never the latest one.** These files are copied into a project and frozen there; nothing tells that copy when the standard moves. A header claiming a version the project has not adopted is worse than an old header, because it stops anyone from looking. What moving costs is written in the upgrade note of each version, by whoever decided it.

## Use

Instantiate the stack on a new project: copy these files under `docs/`, `tools/validate-stack.py`
under `docs/tools/`, resolve the L1 `{placeholder}` values, then have the Dev Lead and the PM sign
the L0/L1 files in `state.json` `prompt_stack[]` — **Quality Gate Layer 1** — before the first
sprint. The full model, the agent catalogue and the standard repository layout are in
`asf-overview.md`. A project on v8.2 moves with `tools/migrate-to-8.3.py`; the upgrade note is in
`CHANGELOG.md`.

To install the agents themselves on an agentic platform, see `agents/README.md`: each agent
directory carries an importable configuration alongside its specification.
