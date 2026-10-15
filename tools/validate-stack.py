#!/usr/bin/env python3
"""The documentation test of an ASF 8.3 project. It runs in CI like any other test.

Checks:
  1. every JSON parses; `.asf/state.json` declares a `meta.schema_version` accepted by
     `.asf/schema/state.schema.json` and validates against it; the other known JSON files
     validate against their schema;
  2. every artifact frontmatter validates against `frontmatter.schema.json` (`$defs` by folder);
  3. every cited id (R-, ADR-, DR-, RF-, RNF-, BUG-, US-, Epic, Task) is defined;
  4. every path cited in a .md exists;
  5. every `file` -> *Title* reference points to a heading that exists;
  6. the cross-file rules of state.json that the schema cannot express: unique ids, resolving
     references, task id prefixes, sprint/roadmap/epic membership, dependency graphs, repos and
     `files` globs, Prompt Stack files, artifact files <-> state.json entries, frontmatter id and
     H1, the RF index of product.md;
  7. ACs have unique, progressive ids, and `RF-XX/AC-NN` references resolve;
  8. ADR supersession is reciprocal; RF statuses agree with the tasks citing them (warnings).

Usage:  python3 tools/validate-stack.py [-v] [--docs DIR]
Exit 0 when the Prompt Stack is valid, 1 otherwise. Every error line starts with `docs/<path>: `.
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import re
import sys

try:
    import yaml
    from jsonschema import Draft202012Validator
    from jsonschema.exceptions import best_match
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
except ImportError as e:  # noqa: BLE001
    sys.exit(f"missing dependency: {e.name} (pip install pyyaml 'jsonschema>=4.18,<5')")

L0_FILES = ("AGENTS.md", "CLAUDE.md")  # CLAUDE.md is the L0 of older projects

# Folder pattern -> frontmatter `$defs` name. Selection is by folder; the schema root is a pure
# `$defs` container. RNF live only in `requirements/`, next to the RF.
ARTIFACTS: dict[str, str] = {
    "requirements/RF-*.md": "rf",
    "requirements/RNF-*.md": "rnf",
    "epics/Epic*.md": "epic",
    "tasks/Task.*.md": "task",
    "bugs/BUG-*.md": "bug",
    "stories/US-*.md": "us",
    "decisions/ADR-*.md": "adr",
}
# Artifact kinds that state.json tracks, with the folder of their file.
STATE_KINDS: dict[str, str] = {
    "rf": "requirements", "rnf": "requirements", "epic": "epics", "task": "tasks",
    "bug": "bugs", "us": "stories",
}
KIND_LABEL = {"rf": "requirements.functional", "rnf": "requirements.non_functional",
              "epic": "epics", "task": "epics[].tasks", "bug": "bugs", "us": "user_stories"}

ID_RE = re.compile(r"\b(Task\.Epic\d{3}\.\d+|ADR-\d{3}|DR-\d{4}|RNF-\d{2,3}|RF-\d{2,3}"
                   r"|BUG-\d{2,3}|US-\d{2,3}|Epic\d{3}|R-\d{2})\b")
PLACEHOLDER = re.compile(r"RF-XX|Epic(XXX|XX)|Task\.Epic(XXX|XX)\.N|ADR-XXX|R-XX|DR-000N")
PATH_RE = re.compile(r"(?<![\w/])((?:docs|tools)/(?:\{[^{}\s]*\}|[\w./<>*-])+)")
TEMPLATE_TOKEN_RE = re.compile(r"YYYY|(?<![A-Za-z])WW(?![A-Za-z])")
SEC_RE = re.compile(r"`?([\w./-]+\.md)`?\s*(?:→|->)\s*\*([^*]+)\*")
INDEX_ROW_RE = re.compile(r"^\|\s*(RF-\d{2,3})\s*\|", re.M)
EM_DASH = "\u2014"


# ---------------------------------------------------------------- setup

def find_docs_root(override: str | None, parser: argparse.ArgumentParser) -> pathlib.Path:
    """The `docs/` tree is the repo; the script lives in `docs/tools/`.

    It works both from the `docs` repo (`python3 tools/validate-stack.py`) and from the workspace
    root (`python3 docs/tools/validate-stack.py`): the anchor is the file, not the cwd.
    """
    if override:
        root = pathlib.Path(override).resolve()
        if not (root / ".asf").is_dir():
            parser.error(f"--docs {override}: no .asf/ directory there")
        return root
    here = pathlib.Path(__file__).resolve().parent
    for candidate in (here.parent, here.parent / "docs", here.parent.parent / "docs"):
        if (candidate / ".asf").is_dir() and any((candidate / f).is_file() for f in L0_FILES):
            return candidate
    sys.exit("cannot find the docs/ tree starting from " + str(here)
             + "\n  action: keep the script in docs/tools/ or pass --docs DIR")


parser = argparse.ArgumentParser(description="Validate the ASF 8.3 Prompt Stack of a docs tree.")
parser.add_argument("-v", "--verbose", action="store_true", help="print every passed check")
parser.add_argument("--docs", metavar="DIR", help="docs root (default: parent of tools/)")
args = parser.parse_args()

DOCS = find_docs_root(args.docs, parser)
ASF = DOCS / ".asf"
SCHEMAS = ASF / "schema"
STATE_PATH = ASF / "state.json"
STATE_REL = "docs/.asf/state.json"
ARCHIVE = DOCS / "decisions/planning-archive.md"
VERBOSE = args.verbose

# Documents cite paths as the workspace sees them (`docs/...`, `tools/...`), but CI runs inside
# the `docs` repo, where `docs/` does not exist: the translation lives in one place only.
CITED_PREFIXES = {"docs": DOCS, "tools": DOCS / "tools"}

errors: list[str] = []
warnings: list[str] = []
CREDENTIALS_RE = re.compile(r"(://)[^/\s@'\"]+@")  # never echo `://user:pass@` into a CI log


def err(where: str, msg: str) -> None:
    """One error = one line starting with `docs/`: PICO and the ERRORS count rely on it."""
    msg = " ".join(msg.splitlines())
    errors.append(where + ": " + CREDENTIALS_RE.sub(r"\1***@", msg))


def warn(where: str, msg: str) -> None:
    warnings.append(f"{where}: {msg}")


def ok(msg: str) -> None:
    if VERBOSE:
        print(f"  ok  {msg}")


def rel(p: pathlib.Path) -> str:
    """Always `docs/...`, so messages do not depend on the layout."""
    return "docs/" + p.relative_to(DOCS).as_posix()


def report_and_exit(md_count: int, artifact_count: int, json_count: int, id_count: int) -> None:
    print(f"checked .md files: {md_count} · artifacts with frontmatter: {artifact_count} · "
          f"JSON: {json_count} · defined ids: {id_count}")
    for w in warnings:
        print(f"  WARNING  {w}")
    if errors:
        print(f"\n{len(errors)} ERRORS:", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        sys.exit(1)
    print("Prompt Stack valid.")
    sys.exit(0)


def required_alternatives(schemas: object) -> list[list[str]] | None:
    """The key lists of an anyOf/oneOf made only of `{"required": [...]}` branches, else None."""
    if not isinstance(schemas, list) or not schemas:
        return None
    out = []
    for branch in schemas:
        if not (isinstance(branch, dict) and set(branch) == {"required"}):
            return None
        out.append(branch["required"])
    return out


def schema_message(e) -> str:
    """jsonschema messages repeat the whole instance for anyOf/oneOf/not: say what is wrong instead."""
    if e.validator in ("anyOf", "oneOf"):
        alternatives = required_alternatives(e.validator_value)
        if alternatives is not None:
            keys = ", ".join(" + ".join(a) for a in alternatives)
            return f"requires one of: {keys}"
        if e.context:
            return f"matches none of the allowed alternatives; closest: {short(best_match(e.context).message)}"
    if e.validator == "not" and isinstance(e.validator_value, dict):
        alternatives = required_alternatives(e.validator_value.get("anyOf"))
        if alternatives is not None and isinstance(e.instance, dict):
            present = sorted({k for a in alternatives for k in a if k in e.instance})
            return f"must not have {', '.join(present)} here"
        return f"must not match {short(json.dumps(e.validator_value), 200)}"
    return short(e.message)


def short(text: str, limit: int = 300) -> str:
    return text if len(text) <= limit else text[: limit - 1] + "…"


# ---------------------------------------------------------------- collection

def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """(frontmatter, body, problem). Frontmatter is None when absent or malformed."""
    if not text.startswith("---\n"):
        return None, text, "YAML frontmatter missing"
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None, text, "YAML frontmatter not closed by ---"
    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return None, parts[2], f"YAML frontmatter malformed — {short(' '.join(str(e).split()), 200)}"
    if fm is None:
        fm = {}
    if not isinstance(fm, dict):
        return None, parts[2], "YAML frontmatter is not a mapping"
    # YAML turns 2026-08-12 into datetime.date: the schema expects strings
    for k, v in list(fm.items()):
        if isinstance(v, (datetime.date, datetime.datetime)):
            fm[k] = v.isoformat()
    return fm, parts[2], None


texts: dict[pathlib.Path, str] = {p: p.read_text(encoding="utf-8") for p in sorted(DOCS.rglob("*.md"))}
docs_md = list(texts)

# path, def, frontmatter, body
artifacts: list[tuple[pathlib.Path, str, dict, str]] = []
# every artifact file on disk per kind, parsed or not: existence never depends on the frontmatter
files_by_kind: dict[str, dict[str, pathlib.Path]] = {kind: {} for kind in ARTIFACTS.values()}
for pattern, defname in ARTIFACTS.items():
    for p in sorted(DOCS.glob(pattern)):
        files_by_kind[defname][p.stem] = p
        fm, body, problem = split_frontmatter(texts[p])
        if fm is None:
            err(rel(p), problem or "YAML frontmatter missing or malformed")
            continue
        artifacts.append((p, defname, fm, body))

for p in sorted(DOCS.glob("nfr/RNF-*.md")):
    err(rel(p), f"RNF files live in requirements/ in ASF 8.3: move it to docs/requirements/{p.name}")

json_docs: dict[pathlib.Path, object] = {}
for p in sorted(DOCS.rglob("*.json")):
    try:
        json_docs[p] = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(rel(p), f"invalid JSON — {e}")


def build_registry() -> Registry:
    """Every schema under .asf/schema, addressable by its `$id` and by its relative path."""
    resources = []
    for p in sorted(SCHEMAS.rglob("*.json")):
        contents = json_docs.get(p)
        if not isinstance(contents, dict):
            continue
        try:
            resource = Resource.from_contents(contents, default_specification=DRAFT202012)
        except Exception:  # noqa: BLE001 — not a schema we can register
            continue
        relpath = p.relative_to(SCHEMAS).as_posix()
        resources.append((relpath, resource))
        if isinstance(contents.get("$id"), str) and contents["$id"] != relpath:
            resources.append((contents["$id"], resource))
    return Registry().with_resources(resources)


REGISTRY = build_registry()


def validator_for(schema: dict) -> Draft202012Validator:
    return Draft202012Validator(schema, registry=REGISTRY,
                                format_checker=Draft202012Validator.FORMAT_CHECKER)


# ---------------------------------------------------------------- 1. state.json: 8.3 gate

state_schema_path = SCHEMAS / "state.schema.json"
state_schema = json_docs.get(state_schema_path)
state = json_docs.get(STATE_PATH)


def accepted_versions(schema: dict) -> list | None:
    """The `meta.schema_version` values the state schema accepts (enum or const), refs followed."""
    resolver = REGISTRY.resolver(base_uri=schema.get("$id", "state.schema.json"))
    node: object = schema
    for key in ("meta", "schema_version"):
        while isinstance(node, dict) and "$ref" in node:
            resolved = resolver.lookup(node["$ref"])
            node, resolver = resolved.contents, resolved.resolver
        node = node.get("properties", {}).get(key) if isinstance(node, dict) else None
    while isinstance(node, dict) and "$ref" in node:
        resolved = resolver.lookup(node["$ref"])
        node, resolver = resolved.contents, resolved.resolver
    if not isinstance(node, dict):
        return None
    if isinstance(node.get("enum"), list):
        return node["enum"]
    if "const" in node:
        return [node["const"]]
    return None


gate_ok = False
if not state_schema_path.exists():
    err(rel(state_schema_path), "state schema missing — blocking error")
elif not isinstance(state_schema, dict):
    pass  # invalid JSON, already reported
elif not STATE_PATH.exists():
    err(STATE_REL, "file missing — blocking error")
elif STATE_PATH in json_docs:
    versions = accepted_versions(state_schema)
    meta = state.get("meta") if isinstance(state, dict) else None
    found = meta.get("schema_version") if isinstance(meta, dict) else None
    asf = meta.get("asf_version") if isinstance(meta, dict) else None
    if versions is None or found not in versions:
        accepts = (f"accepts {versions}" if versions is not None
                   else "declares no accepted meta.schema_version (a pre-8.3 schema)")
        err(STATE_REL,
            f"not an ASF 8.3 state file: meta.schema_version is {found!r} (meta.asf_version "
            f"{asf!r}), {rel(state_schema_path)} {accepts}; convert the tree with "
            f"migrate-to-8.3.py from the ASF standard — no other check runs until then")
    else:
        gate_ok = True

if not gate_ok:
    report_and_exit(len(docs_md), len(artifacts), len(json_docs), 0)

# ---------------------------------------------------------------- 1. JSON + schema

state = state if isinstance(state, dict) else {}


def locate(path) -> str:
    """JSON path -> `epics[Epic001].tasks[Task.Epic001.2].status` (ids instead of indexes)."""
    out, node = "", state
    for part in path:
        if isinstance(part, int):
            item = node[part] if isinstance(node, list) and part < len(node) else None
            key = item.get("id", item.get("filename")) if isinstance(item, dict) else None
            out += f"[{key if key is not None else part}]"
            node = item
        else:
            out += f".{part}" if out else str(part)
            node = node.get(part) if isinstance(node, dict) else None
    return out or "<root>"


for e in sorted(validator_for(state_schema).iter_errors(state), key=lambda x: list(map(str, x.path))):
    err(STATE_REL, f"schema: {locate(e.path)}: {schema_message(e)}")
ok(f"{STATE_REL} validates against {state_schema_path.name}")

# Other known JSON files, validated when present.
JSON_SCHEMAS = {
    ASF / "llm-config.json": SCHEMAS / "llm-config.schema.json",
    ASF / "pitch-kinds.json": SCHEMAS / "pitch-kinds.schema.json",
    DOCS / "decisions/decision-log.json": DOCS / "decisions/decision-log.schema.json",
}
for target, schema_path in JSON_SCHEMAS.items():
    if target not in json_docs:
        continue
    if not schema_path.exists():
        err(rel(schema_path), f"schema of {rel(target)} missing — blocking error")
        continue
    schema = json_docs.get(schema_path)
    if not isinstance(schema, dict):
        continue
    for e in sorted(validator_for(schema).iter_errors(json_docs[target]), key=lambda x: list(map(str, x.path))):
        err(rel(target), f"schema: {'/'.join(map(str, e.path)) or '<root>'}: {schema_message(e)}")
    ok(f"{rel(target)} validates against {schema_path.name}")

if (ASF / "recap-source.json").exists():
    warn("docs/.asf/recap-source.json", "obsolete in ASF 8.3 (state.json is the only source): delete it")

# ---------------------------------------------------------------- 2. frontmatter + schema

fm_schema_path = SCHEMAS / "frontmatter.schema.json"
fm_schema = json_docs.get(fm_schema_path)
if not fm_schema_path.exists():
    err(rel(fm_schema_path), "frontmatter schema missing — blocking error")
elif isinstance(fm_schema, dict):
    fm_uri = fm_schema.get("$id", "frontmatter.schema.json")
    declared = fm_schema.get("$defs", {})
    for p, defname, fm, _ in artifacts:
        if defname not in declared:
            err(rel(p), f"kind '{defname}' not declared by {rel(fm_schema_path)}: the file exists "
                        f"but no schema validates it — adopt ASF 8.3")
            continue
        v = validator_for({"$ref": f"{fm_uri}#/$defs/{defname}"})
        for e in sorted(v.iter_errors(fm), key=lambda x: list(map(str, x.path))):
            field = "/".join(map(str, e.path)) or "<frontmatter>"
            err(rel(p), f"frontmatter {field}: {schema_message(e)}")
        ok(f"{rel(p)} frontmatter ${defname}")

    # the non-normative archive has its own $def and must declare normative: false
    if ARCHIVE.exists() and "archive" in declared:
        fm, _, _ = split_frontmatter(texts[ARCHIVE])
        for e in validator_for({"$ref": f"{fm_uri}#/$defs/archive"}).iter_errors(fm or {}):
            err(rel(ARCHIVE), f"frontmatter: {schema_message(e)}")

# ---------------------------------------------------------------- state.json index


def dicts(node) -> list[dict]:
    return [x for x in node if isinstance(x, dict)] if isinstance(node, list) else []


def str_list(node) -> list[str]:
    return [x for x in node if isinstance(x, str)] if isinstance(node, list) else []


def sid(item: dict):
    return item.get("id")


requirements = state.get("requirements") if isinstance(state.get("requirements"), dict) else {}
epics = dicts(state.get("epics"))
COLLECTIONS: dict[str, tuple[str, list[dict]]] = {  # kind -> (locator, items)
    "rf": ("requirements.functional", dicts(requirements.get("functional"))),
    "rnf": ("requirements.non_functional", dicts(requirements.get("non_functional"))),
    "epic": ("epics", epics),
    "us": ("user_stories", dicts(state.get("user_stories"))),
    "bug": ("bugs", dicts(state.get("bugs"))),
}
sprints = dicts(state.get("sprints"))
roadmap = dicts(state.get("roadmap"))
tasks: list[tuple[str, dict]] = []  # (epic locator, task)
for epic in epics:
    for task in dicts(epic.get("tasks")):
        tasks.append((f"epics[{sid(epic)}]", task))

state_ids: dict[str, set] = {kind: {sid(x) for x in items if isinstance(sid(x), str)}
                             for kind, (_, items) in COLLECTIONS.items()}
state_ids["task"] = {sid(t) for _, t in tasks if isinstance(sid(t), str)}
task_by_id = {sid(t): t for _, t in tasks if isinstance(sid(t), str)}

# ---------------------------------------------------------------- 6a. unique ids


def check_unique(where: str, items: list[dict], key: str = "id") -> None:
    seen: set = set()
    for item in items:
        value = item.get(key)
        if value is None:
            continue
        if value in seen:
            err(STATE_REL, f"{where}: duplicate {key} {value}")
        seen.add(value)


for kind, (where, items) in COLLECTIONS.items():
    check_unique(where, items)
check_unique("sprints", sprints)
check_unique("roadmap", roadmap)
seen_tasks: dict[str, str] = {}
for where, task in tasks:
    i = sid(task)
    if not isinstance(i, str):
        continue
    if i in seen_tasks:
        err(STATE_REL, f"{where}.tasks: duplicate id {i} (already in {seen_tasks[i]})")
    else:
        seen_tasks[i] = where
check_unique("prompt_stack", dicts(state.get("prompt_stack")), "filename")

# ---------------------------------------------------------------- 6b. references resolve


def check_refs(where: str, item: dict, field: str, kind: str) -> None:
    for ref in str_list(item.get(field)):
        if ref not in state_ids[kind]:
            err(STATE_REL, f"{where}.{field}: {ref} is not in {KIND_LABEL[kind]}")


for sprint in sprints:
    check_refs(f"sprints[{sid(sprint)}]", sprint, "epic_refs", "epic")
for item in roadmap:
    check_refs(f"roadmap[{sid(item)}]", item, "epic_refs", "epic")
for epic in epics:
    where = f"epics[{sid(epic)}]"
    check_refs(where, epic, "user_story_refs", "us")
    check_refs(where, epic, "rnf_refs", "rnf")
    for dep in str_list(epic.get("depends_on")):
        if dep == sid(epic):
            err(STATE_REL, f"{where}.depends_on: {dep} depends on itself")
        elif dep not in state_ids["epic"]:
            err(STATE_REL, f"{where}.depends_on: {dep} is not in epics")
for epic_where, task in tasks:
    where = f"{epic_where}.tasks[{sid(task)}]"
    check_refs(where, task, "rf_refs", "rf")
    check_refs(where, task, "bug_refs", "bug")
    for dep in str_list(task.get("depends_on")):
        if dep == sid(task):
            err(STATE_REL, f"{where}.depends_on: {dep} depends on itself")
        elif dep not in state_ids["task"]:
            err(STATE_REL, f"{where}.depends_on: {dep} is not in epics[].tasks")
for story in COLLECTIONS["us"][1]:
    check_refs(f"user_stories[{sid(story)}]", story, "rf_refs", "rf")
for bug in COLLECTIONS["bug"][1]:
    where = f"bugs[{sid(bug)}]"
    check_refs(where, bug, "rf_refs", "rf")
    check_refs(where, bug, "rnf_refs", "rnf")
    dup = bug.get("duplicate_of")
    if isinstance(dup, str):
        if dup == sid(bug):
            err(STATE_REL, f"{where}.duplicate_of: a bug cannot be a duplicate of itself")
        elif dup not in state_ids["bug"]:
            err(STATE_REL, f"{where}.duplicate_of: {dup} is not in bugs")

# ---------------------------------------------------------------- 6c. task id prefix

for epic in epics:
    prefix = f"Task.{sid(epic)}."
    for task in dicts(epic.get("tasks")):
        if isinstance(sid(task), str) and not sid(task).startswith(prefix):
            err(STATE_REL, f"epics[{sid(epic)}].tasks[{sid(task)}]: a task of {sid(epic)} "
                           f"must have an id starting with {prefix}")

# ---------------------------------------------------------------- 6d. membership


def check_single_owner(owners_where: str, owners: list[dict], field: str, what: str) -> None:
    owned_by: dict[str, list[str]] = {}
    for owner in owners:
        for ref in dict.fromkeys(str_list(owner.get(field))):
            owned_by.setdefault(ref, []).append(str(sid(owner)))
    for ref, by in sorted(owned_by.items()):
        if len(by) > 1:
            err(STATE_REL, f"{owners_where}: {ref} is in the {field} of more than one {what} "
                           f"({', '.join(by)})")


check_single_owner("sprints", sprints, "epic_refs", "sprint")
check_single_owner("roadmap", roadmap, "epic_refs", "roadmap item")
check_single_owner("epics", epics, "user_story_refs", "epic")

# ---------------------------------------------------------------- 6e. dependency cycles


def check_cycles(where: str, graph: dict[str, list[str]]) -> None:
    """Tarjan's SCC: every strongly connected component with 2+ nodes is a cycle."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    counter = 0
    for root in sorted(graph):
        if root in index:
            continue
        work = [(root, iter(graph[root]))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            node, children = work[-1]
            child = next(children, None)
            if child is not None:
                if child == node or child not in graph:
                    continue  # self-references and dangling targets are reported elsewhere
                if child not in index:
                    index[child] = low[child] = counter
                    counter += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(graph[child])))
                elif child in on_stack:
                    low[node] = min(low[node], index[child])
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                component = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                if len(component) > 1:
                    err(STATE_REL, f"{where}: dependency cycle among {', '.join(sorted(component))}")


check_cycles("epics[].depends_on",
             {sid(e): str_list(e.get("depends_on")) for e in epics if isinstance(sid(e), str)})
check_cycles("epics[].tasks[].depends_on",
             {sid(t): str_list(t.get("depends_on")) for _, t in tasks if isinstance(sid(t), str)})

# ---------------------------------------------------------------- 6f. repos and files globs

project = state.get("project") if isinstance(state.get("project"), dict) else {}
repo_urls: dict[str, list[str]] = {}
for url in str_list(project.get("repos")):
    tail = re.split(r"[/:]", url.rstrip("/"))[-1]
    name = tail[:-4] if tail.endswith(".git") else tail
    repo_urls.setdefault(name, []).append(url)
for name, urls in sorted(repo_urls.items()):
    if len(urls) > 1:
        err(STATE_REL, f"project.repos: repo name {name!r} is used by more than one URL "
                       f"({', '.join(urls)})")
for epic_where, task in tasks:
    for glob in str_list(task.get("files")):
        first = glob.split("/", 1)[0]
        if first not in repo_urls:
            known = ", ".join(sorted(repo_urls)) or "none declared"
            err(STATE_REL, f"{epic_where}.tasks[{sid(task)}].files: {glob!r} must start with a "
                           f"repo name of project.repos ({known})")

# ---------------------------------------------------------------- 6g. prompt stack files

for entry in dicts(state.get("prompt_stack")):
    filename = entry.get("filename")
    if isinstance(filename, str) and filename and not (DOCS / filename).exists():
        err(STATE_REL, f"prompt_stack[{filename}].filename: docs/{filename} does not exist")

# ---------------------------------------------------------------- 6h. artifact files <-> state

product_path = DOCS / "product.md"
index_rows = INDEX_ROW_RE.findall(texts.get(product_path, ""))
indexed_rf = set(index_rows)

for kind, folder in STATE_KINDS.items():
    if kind == "task":
        entries = [(f"{w}.tasks[{sid(t)}]", sid(t)) for w, t in tasks]
    else:
        where, items = COLLECTIONS[kind]
        entries = [(f"{where}[{sid(x)}]", sid(x)) for x in items]
    for where, i in entries:
        if not isinstance(i, str) or i in files_by_kind[kind]:
            continue
        if kind == "rf":
            continue  # an RF may have only its product.md index row: checked with the index
        err(STATE_REL, f"{where}: {folder}/{i}.md does not exist")
    for stem, p in sorted(files_by_kind[kind].items()):
        if stem not in state_ids[kind]:
            err(rel(p), f"{stem} has a file but is not in state.json {KIND_LABEL[kind]}")

# ---------------------------------------------------------------- 6i. frontmatter id and H1

for p, defname, fm, body in artifacts:
    if defname not in STATE_KINDS:
        continue
    fid = fm.get("id")
    if fid != p.stem:
        err(rel(p), f"frontmatter id {fid!r} does not match the file name ({p.stem})")
    title = fm.get("title")
    if not isinstance(title, str):
        continue  # reported by the schema
    expected = f"# {p.stem} {EM_DASH} {title}"
    h1 = next((ln.rstrip() for ln in body.splitlines() if ln.startswith("# ")), None)
    if h1 is None:
        err(rel(p), f"no H1: the first heading must be {expected!r}")
    elif h1 != expected:
        err(rel(p), f"first H1 must be {expected!r}, found {h1!r}")

# ---------------------------------------------------------------- 6j. RF index of product.md

if not product_path.exists():
    err(rel(product_path), "missing: its RF index must list the RF ids of state.json "
                           "requirements.functional")
else:
    for rf in sorted({r for r in index_rows if index_rows.count(r) > 1}):
        err(rel(product_path), f"RF index lists {rf} more than once")
    for rf in sorted(indexed_rf - state_ids["rf"]):
        err(rel(product_path), f"RF index lists {rf}, which is not in state.json "
                               f"requirements.functional")
    for rf in sorted(state_ids["rf"] - indexed_rf):
        missing_file = "" if rf in files_by_kind["rf"] else f" (and requirements/{rf}.md does not exist)"
        err(rel(product_path), f"RF index lacks {rf}, which is in state.json "
                               f"requirements.functional{missing_file}")
if not product_path.exists():
    for rf in sorted(state_ids["rf"] - set(files_by_kind["rf"])):
        err(STATE_REL, f"requirements.functional[{rf}]: requirements/{rf}.md does not exist "
                       f"and there is no product.md RF index")

# ---------------------------------------------------------------- 3. cited ids

defined: dict[str, str] = {}
for p, _defname, fm, _ in artifacts:
    if fm.get("id"):
        defined[str(fm["id"])] = rel(p)
for kind, ids in state_ids.items():
    for i in ids:
        defined.setdefault(i, STATE_REL)
for i in indexed_rf:
    defined.setdefault(i, rel(product_path))
for name in L0_FILES:
    if (DOCS / name).exists():
        for m in re.finditer(r"\|\s*\*\*(R-\d{2})\*\*\s*\|", texts[DOCS / name]):
            defined[m.group(1)] = f"docs/{name}"
log = json_docs.get(DOCS / "decisions/decision-log.json")
if isinstance(log, dict):
    for r in dicts(log.get("records")):
        if r.get("id"):
            defined[str(r["id"])] = "docs/decisions/decision-log.json"
# the standard's ADR log: `.asf/architecture.json` adLog[].id (decisions/ADR-*.md stay valid too)
architecture = json_docs.get(ASF / "architecture.json")
if isinstance(architecture, dict):
    for adr in dicts(architecture.get("adLog")):
        if isinstance(adr.get("id"), str) and adr["id"]:
            defined.setdefault(adr["id"], "docs/.asf/architecture.json")

for p in docs_md:
    if p == ARCHIVE:
        continue
    for n, line in enumerate(texts[p].splitlines(), 1):
        clean = PLACEHOLDER.sub("", line)
        for id_ in sorted(set(ID_RE.findall(clean))):
            if id_ not in defined:
                err(f"{rel(p)}:{n}", f"cited id is not defined: {id_}")

# ---------------------------------------------------------------- 4. cited paths

for p in docs_md:
    if p == ARCHIVE:
        continue
    for n, line in enumerate(texts[p].splitlines(), 1):
        for cand in sorted(set(PATH_RE.findall(line))):
            cand = cand.rstrip(".,;:)`")
            if cand.endswith("/"):
                continue  # a cited folder: git keeps no empty folder, it may legitimately be absent
            if any(c in cand for c in "<>*{}") or TEMPLATE_TOKEN_RE.search(cand):
                continue  # pattern or template (`<id>`, `*`, `{fe,be}`, `YYYY-WW`)
            if PLACEHOLDER.search(cand) or re.search(r"\bXX+\b|\.N\.md$", cand):
                continue  # example form (RF-XX, EpicXXX, Task.EpicXX.N)
            head, _, tail = cand.partition("/")
            base = CITED_PREFIXES[head]
            target = base / tail if tail else base
            if not target.exists():
                err(f"{rel(p)}:{n}", f"cited path does not exist: {cand}")

# ---------------------------------------------------------------- 5. section references

SECTION_NUMBER_RE = re.compile(r"^(?:§\s*)?\d+(?:\.\d+)*[a-z]*[.)]?\s+")
SECTION_SEPARATORS = (" \u2014 ", " \u2013 ", " - ", ":", " (")


def section_name(text: str) -> str:
    """Heading or cited name, compared without numbering, emphasis, backticks or extra spaces."""
    text = re.sub(r"[`*]|(?<!\w)_+|_+(?!\w)", "", text)
    text = " ".join(text.split())
    return SECTION_NUMBER_RE.sub("", text)


def has_section(names: set[str], want: str) -> bool:
    """Sections are cited by name without numbers (stable across renumbering): `Sprint Execution`
    matches `15. Sprint Execution — Step by Step`, `Sprint Exec` does not."""
    want = section_name(want)
    return bool(want) and any(
        name == want or (name.startswith(want) and name[len(want):].startswith(SECTION_SEPARATORS))
        for name in names)


headings: dict[str, set[str]] = {}
for p in docs_md:
    hs = set()
    for line in texts[p].splitlines():
        m = re.match(r"^#{2,4} (.+?)\s*$", line)
        if m:
            hs.add(section_name(m.group(1)))
    headings[rel(p)] = hs
l0_headings = set().union(*(headings.get(f"docs/{name}", set()) for name in L0_FILES))

for p in docs_md:
    if p == ARCHIVE:
        continue
    for n, line in enumerate(texts[p].splitlines(), 1):
        for fname, sect in SEC_RE.findall(line):
            base = fname.lstrip("@")
            target = base if base.startswith("docs/") else f"docs/{pathlib.PurePath(base).name}"
            if target not in headings:
                continue
            want = re.sub(r"[`*]", "", sect).strip()
            if not has_section(headings[target], want):
                err(f"{rel(p)}:{n}", f"reference to a missing section: {base} → *{want}*")

# same-file section references: (*Title*)
for p in docs_md:
    if p == ARCHIVE:
        continue
    own = headings[rel(p)]
    for n, line in enumerate(texts[p].splitlines(), 1):
        if re.search(r"\.md`?\s*(?:→|->)", line):
            continue
        for m in re.finditer(r"\((\*[^*)]{6,}\*)\)", line):
            want = re.sub(r"[`*]", "", m.group(1)).strip()
            if want and not has_section(own, want) and not has_section(l0_headings, want):
                warn(f"{rel(p)}:{n}", f"possible reference to a missing section: *{want}*")

# ---------------------------------------------------------------- 7. AC

ac_ids: dict[str, list[str]] = {}
for p, defname, fm, body in artifacts:
    found = re.findall(r"\*\*(AC-\d{2})\b", body)
    ac_ids[str(fm.get("id", rel(p)))] = found
    if defname in ("rf", "task") and not found:
        err(rel(p), "no AC with an id (expected AC-01, AC-02, ...)")
    if len(found) != len(set(found)):
        dup = sorted({x for x in found if found.count(x) > 1})
        err(rel(p), f"duplicate ACs: {', '.join(dup)}")
    expected = [f"AC-{i:02d}" for i in range(1, len(found) + 1)]
    if found and found != expected:
        err(rel(p), f"ACs not progressive: {found} (expected {expected})")

for p, defname, fm, body in artifacts:
    if defname != "task":
        continue
    rf_refs = str_list((task_by_id.get(p.stem) or {}).get("rf_refs"))
    for m in re.finditer(r"`(RF-\d{2,3})/(AC-\d{2})`", body):
        rf, ac = m.groups()
        if rf not in ac_ids:
            if rf not in indexed_rf:
                err(rel(p), f"reference to {rf}, which has no file")
        elif ac not in ac_ids[rf]:
            err(rel(p), f"reference to {rf}/{ac}, which does not exist in that RF")
        if rf not in rf_refs:
            err(rel(p), f"AC reference to {rf}, which is not in the task's state.json rf_refs: {rf_refs}")

# ---------------------------------------------------------------- 8. ADR graph and RF statuses

adr_by_id = {str(fm["id"]): fm for _p, d, fm, _b in artifacts if d == "adr" and fm.get("id")}
for p, defname, fm, _ in artifacts:
    if defname != "adr":
        continue
    i = str(fm.get("id"))
    sb = fm.get("superseded_by")
    if sb and sb not in adr_by_id:
        err(rel(p), f"superseded_by points to a missing ADR: {sb}")
    for s in fm.get("supersedes") or []:
        if s not in adr_by_id:
            err(rel(p), f"supersedes points to a missing ADR: {s}")
        elif adr_by_id[s].get("superseded_by") != i:
            err(rel(p), f"{i} supersedes {s}, but {s} does not declare superseded_by {i}: one-way relation")

# RF <-> task: the RF status (state.json) should agree with the tasks citing it. A warning, not an
# error: an RF status stays a human decision, and an RF can move for work no task describes.
tasks_per_rf: dict[str, list[dict]] = {}
for _w, task in tasks:
    for rf in str_list(task.get("rf_refs")):
        tasks_per_rf.setdefault(rf, []).append(task)
for rf_item in COLLECTIONS["rf"][1]:
    rf, status = sid(rf_item), rf_item.get("status")
    if not isinstance(rf, str):
        continue
    citing = tasks_per_rf.get(rf, [])
    where = rel(files_by_kind["rf"][rf]) if rf in files_by_kind["rf"] else STATE_REL
    still_open = sorted(str(sid(t)) for t in citing if t.get("status") != "done")
    if status == "done" and still_open:
        warn(where, f"{rf} is done but these tasks are not: {', '.join(still_open)}")
    elif status == "todo" and any(t.get("status") == "done" for t in citing):
        warn(where, f"{rf} is todo but has done tasks: the work has started")
    elif status in ("in_progress", "review") and not citing:
        warn(where, f"{rf} is {status} but no task cites it: where does the work come from?")

# ---------------------------------------------------------------- report

report_and_exit(len(docs_md), len(artifacts), len(json_docs), len(defined))
