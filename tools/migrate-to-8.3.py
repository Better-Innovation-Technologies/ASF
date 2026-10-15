#!/usr/bin/env python3
"""Migrate an ASF docs tree to ASF 8.3: `state.json` 2.0.0 and strict artifact frontmatter.

Reads the docs tree (`--docs`), builds the 8.3 `.asf/state.json` from the old `state.json`,
`recap-source.json`, the artifact frontmatter and the docs git history, then rewrites every artifact
`.md`: frontmatter reduced to the keys of its 8.3 def, first H1 set to `# <id> — <title>`, body
blocks that only repeat references removed. It installs the standard's 8.3 schemas and validator
(`tools/validate-stack.py`) into the tree and drops `recap-source.json` and its schema. Every
non-empty value of the input `state.json` that is neither carried nor removed by the spec as
derived or kept elsewhere is reported as `dropped_value_lost`, with its value.

    python3 tools/migrate-to-8.3.py --docs DIR [--out DIR | --write] [--repos-root DIR]
        [--repo URL]... [--closed-on SPRINT=YYYY-MM-DD]...
        [--sprint-dates SPRINT=YYYY-MM-DD..YYYY-MM-DD]... [--report FILE.json]

Without `--out` or `--write` it is a dry run (report only). `--out` writes a converted copy of the
whole tree (without `.git`); items with blockers are left out of `state.json` and their files are
copied unconverted. `--write` converts in place and refuses when there are blockers.
Exit 0 ok, 1 blockers, 2 usage or IO error.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("missing dependency: PyYAML")

SCHEMA_VERSION = "2.0.0"
ASF_VERSION = "8.3"
STANDARD_ROOT = Path(__file__).resolve().parent.parent
# Files of the standard installed into the converted tree: (source, path in the docs tree).
STANDARD_FILES = (
    (STANDARD_ROOT / ".asf" / "schema" / "state.schema.json", ".asf/schema/state.schema.json"),
    (STANDARD_ROOT / ".asf" / "schema" / "frontmatter.schema.json", ".asf/schema/frontmatter.schema.json"),
    (STANDARD_ROOT / "tools" / "validate-stack.py", "tools/validate-stack.py"),
)
DROPPED_FILES = (".asf/recap-source.json", ".asf/schema/recap-source.schema.json")
# Pre-8.3 tooling that re-runs the KStudio reconciler on merge and rewrites `.asf/state.json`.
RECAP_TOOLING = ("tools/reconcile-recap.sh", "tools/merge-driver-recap.sh", "tools/install-git-hooks.sh")

WORK_STATUS = ("todo", "in_progress", "review", "done", "blocked")
BUG_STATUS = WORK_STATUS + ("triage", "not_reproducible", "wont_fix", "duplicate")
RNF_STATUS = ("unverified", "satisfied", "at_risk", "violated", "waived")
PRIORITY = ("low", "medium", "high", "critical")
SEVERITY = ("blocker", "critical", "high", "low", "trivial")
POINTS = (1, 2, 3, 5, 8)
EPIC_KIND = ("feature", "container")
DASHBOARD = ("pipeline", "product_log", "alerts", "releases", "inbox")

ID_RE = {
    "rf": re.compile(r"^RF-\d{2,3}$"),
    "rnf": re.compile(r"^RNF-\d{2,3}$"),
    "epic": re.compile(r"^Epic\d{3}$"),
    "task": re.compile(r"^Task\.Epic\d{3}\.\d+$"),
    "bug": re.compile(r"^BUG-\d{2,3}$"),
    "us": re.compile(r"^US-\d{2,3}$"),
}
PERSONA_RE = re.compile(r"^[^<>]+ <[^<>\s@]+@[^<>\s]+>$")
REPO_URL_RE = re.compile(r"^(?:https://[A-Za-z0-9.-]+(?::[0-9]+)?/|git@[A-Za-z0-9.-]+:)[A-Za-z0-9._~-]+"
                         r"(?:/[A-Za-z0-9._~-]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KIND_LABEL = {"rf": "RF", "rnf": "RNF", "epic": "epic", "task": "task", "bug": "bug", "us": "story"}

# Artifact files: kind -> [(folder, glob)]. RNF files under `nfr/` move to `requirements/`.
ARTIFACT_GLOBS = {
    "rf": [("requirements", "RF-*.md")],
    "rnf": [("requirements", "RNF-*.md"), ("nfr", "RNF-*.md")],
    "epic": [("epics", "Epic*.md")],
    "task": [("tasks", "Task.*.md")],
    "bug": [("bugs", "BUG-*.md")],
    "us": [("stories", "US-*.md")],
}
TARGET_FOLDER = {"rf": "requirements", "rnf": "requirements", "epic": "epics", "task": "tasks",
                 "bug": "bugs", "us": "stories"}
# Keys each 8.3 frontmatter def allows (spec `frontmatter[].resta`).
KEEP = {
    "rf": ("id", "title", "owner"),
    "rnf": ("id", "title", "category", "metric", "threshold", "verification", "owner"),
    "epic": ("id", "title"),
    "task": ("id", "title", "adr", "rules", "reads"),
    "bug": ("id", "title", "area", "found_in", "reported_by", "reported_at", "regression_test"),
    "us": ("id", "title", "actor", "owner"),
}
EMPTY = (None, "", [], {})
# Where each kind of item sits in a pre-8.3 state.json (v1.x KStudio, v8.2 standard, 8.3).
STATE_ENTITIES = {
    ("meta",): "meta",
    ("project",): "project",
    ("sprint",): "sprint_block",
    ("sprints", "[]"): "sprint",
    ("roadmap",): "roadmap",
    ("prompt_stack", "[]"): "prompt_stack",
    ("epics", "[]"): "epic",
    ("tasks", "[]"): "task",
    ("requirements", "sections", "[]"): "rf_section",
    ("requirements", "sections", "[]", "requirements", "[]"): "rf",
    ("requirements", "functional", "[]"): "rf",
    ("requirements", "non_functional", "[]"): "rnf",
    ("nfrs", "[]"): "rnf",
    ("nfrs", "items", "[]"): "rnf",
    ("user_stories", "[]"): "us",
    ("user_stories", "items", "[]"): "us",
    ("bugs", "[]"): "bug",
    ("bugs", "items", "[]"): "bug",
}
# Pre-8.3 state.json fields the spec removes because they are derived, live in git history or
# outside docs (KStudio, infra), or are computed: never reported as lost.
STATE_DERIVED = {
    "root": {"version", "gates", "traceability", "open_questions", "velocity_history", "velocity_periods",
             "retro", "retrospectives"},
    "meta": {"schema_version", "asf_version", "generated_at", "generated_by", "updated_at", "updated_by", "notice"},
    "project": {"id", "dev_lead", "client", "tech_stack", "gitlab_group", "registry_namespace", "docs_project_id",
                "cloud_provider", "namespaces", "bootstrap_date", "wizard_version", "status"},
    "sprint_block": {"status", "velocity_pts", "velocity_target", "velocity_history", "burndown", "issues"},
    "sprint": {"label", "declared", "velocity_target", "velocity_pts", "epic_velocity", "retro"},
    "roadmap": {"last_updated", "last_commit_sha", "gitlab_file_path"},
    "prompt_stack": {"layer", "status", "author", "last_updated", "warn_message"},
    "epic": {"rf_refs", "requirements", "slice", "points", "pts", "story_points", "file_path", "tasks_total",
             "tasks_done"},
    "task": {"epic_ref", "assignee", "file_path", "sprint", "sprint_id"},
    "rf_section": {"id", "slice", "title", "author", "last_updated"},
    "rf": {"epic_ref", "file_path", "slice"},
    "rnf": {"scope", "bug_refs", "file_path"},
    "us": {"status", "epic_ref", "file_path"},
    "bug": {"epic_ref", "resolved_at", "task_refs", "points", "file_path", "created_at", "updated_at"},
}
# Pre-8.3 state.json fields that 8.3 keeps only in the artifact `.md`: lost when the file is missing.
STATE_IN_MD = {
    "epic": {"title", "description"},
    "task": {"title"},
    "rf": {"title", "description"},
    "rnf": {"title", "category", "metric", "threshold", "verification", "description"},
    "bug": {"title", "area", "found_in", "reported_at", "reported_by", "regression_test", "description"},
    "us": {"title", "actor", "description"},
}
# The current sprint block (`sprint`): 8.3 key -> names in recap-source / v1.x / v8.2.
SPRINT_BLOCK_KEYS = (("current", ("current", "id")), ("next", ("next",)), ("starts_at", ("starts_at", "start_date")),
                     ("ends_at", ("ends_at", "end_date")), ("note", ("note", "goal")))
ROADMAP_KEYS = ("id", "title", "start_date", "end_date", "epic_refs")
# Dropped keys whose value goes to state.json, is derived, or is removed by the spec without a
# replacement. Keys with a dedicated check live in `check_dropped`; any other key is a loss.
DROPPED_PLAIN = {
    "rf": {"status", "priority", "slice"},
    "rnf": {"status", "verified_at", "verified_by", "priority", "scope"},
    "epic": {"status", "product_priority", "kind", "slice", "requirements"},
    "task": {"status", "points", "depends_on", "requirements", "bugs", "epic"},
    "bug": {"status", "severity", "duplicate_of", "requirements", "nfr", "epic", "resolved_at"},
    "us": {"priority", "requirements", "status"},
}

# The standard's L0/L1 files, in Prompt Stack order (L0 is AGENTS.md, CLAUDE.md in older projects).
PROMPT_STACK_L1 = (".asf/architecture.json", "instructions.md", "deployment.md", "product.md",
                   "Roadmap.md", "ProductLog.md")
PROMPT_STACK_EXTRA = ("architecture.md",)

HEADER_LINE_RE = re.compile(r"^\*\*(Validated by|Area|RF covered|Dependencies)(?::\*\*|\*\*\s*:)\s*(.*?)\s*$")
EPIC_RF_HEADINGS = ("rf in scope", "requisiti")
STORY_RF_HEADINGS = ("requisiti che la soddisfano",)
PLACEHOLDER_VALUES = {"", "—", "-", "–", "none", "nessuna", "nessuno", "n/a", "tbd"}
AREA_TOKENS = {"fe", "be", "api", "core", "worker", "deployer", "notify", "infra", "docs"}


class UsageError(Exception):
    pass


# ----------------------------------------------------------------------------- helpers

def id_key(ident: str) -> tuple:
    """Sort key: prefix, then every number in the id (Task.Epic001.12 -> ('Task.Epic', 1, 12))."""
    nums = tuple(int(n) for n in re.findall(r"\d+", ident))
    return (re.sub(r"[\d.\-]+", "", ident), nums, ident)


def sorted_ids(ids) -> list[str]:
    return sorted(set(ids), key=id_key)


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if v is not None]
    return [str(value)]


def iso_dates(value: Any) -> Any:
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [iso_dates(v) for v in value]
    if isinstance(value, dict):
        return {k: iso_dates(v) for k, v in value.items()}
    return value


def items_of(node: Any) -> list[dict]:
    """A v1.x section is either a list or `{items: [...]}`."""
    if isinstance(node, dict):
        node = node.get("items")
    return [n for n in node or [] if isinstance(n, dict)]


def valid_date(value: Any) -> bool:
    if not isinstance(value, str) or not DATE_RE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


# ----------------------------------------------------------------------------- state.json audit

class _Index(str):
    """A list position in a state.json path: the item's `id` when unique, else its index."""


class Tracked(dict):
    """A JSON object of the input state.json that records which keys the migration reads."""
    __slots__ = ("path", "audit")

    def __getitem__(self, key):
        self.audit.reads.add(self.path + (key,))
        return super().__getitem__(key)

    def get(self, key, default=None):
        self.audit.reads.add(self.path + (key,))
        return super().get(key, default)


class StateAudit:
    """Which paths of the input state.json the migration read (`reads`) or handled whole (`consumed`)."""

    def __init__(self) -> None:
        self.reads: set[tuple] = set()
        self.consumed: set[tuple] = set()

    def track(self, node: Any, path: tuple = ()) -> Any:
        if isinstance(node, dict):
            tracked = Tracked((k, self.track(v, path + (k,))) for k, v in node.items())
            tracked.path, tracked.audit = path, self
            return tracked
        if isinstance(node, list):
            labels = [str(v["id"]) if isinstance(v, dict) and isinstance(v.get("id"), (str, int))
                      and not isinstance(v.get("id"), bool) else str(i) for i, v in enumerate(node)]
            if len(set(labels)) != len(labels):
                labels = [str(i) for i in range(len(node))]
            return [self.track(v, path + (_Index(label),)) for v, label in zip(node, labels)]
        return node

    def consume(self, parent: Any, key: str) -> None:
        if isinstance(parent, Tracked):
            self.consumed.add(parent.path + (key,))

    def consume_node(self, node: Any) -> None:
        if isinstance(node, Tracked):
            self.consumed.add(node.path)


def state_path_label(path: tuple) -> str:
    return "".join(f"[{s}]" if isinstance(s, _Index) else (f".{s}" if i else s) for i, s in enumerate(path))


def audit_label(node: Any) -> str:
    return state_path_label(node.path) if isinstance(node, Tracked) else "state.json"


def removed_state_path(path: tuple) -> bool:
    """True for a value the spec removes because it is derived or lives in git, the `.md` or elsewhere."""
    norm = tuple("[]" if isinstance(s, _Index) else s for s in path)
    kind = STATE_ENTITIES.get(norm[:-1], "root" if len(norm) == 1 else None)
    return kind is not None and (norm[-1] in STATE_DERIVED.get(kind, ()) or norm[-1] in STATE_IN_MD.get(kind, ()))


def norm_title(text: str) -> str:
    text = re.sub(r"[*`_]", "", str(text))
    text = text.replace("’", "'").replace("‘", "'").replace("–", "—")
    text = re.sub(r"\s+", " ", text).strip().rstrip(".").strip()
    return text.casefold()


def git(cwd: Path, *args: str) -> str | None:
    try:
        done = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                              check=False)
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


def strip_credentials(url: str) -> str:
    return re.sub(r"^([a-z][a-z0-9+.-]*://)[^/@]*@", r"\1", url.strip())


def repo_url_ok(url: str) -> bool:
    """The form of `$defs/repo_url` in state.schema.json."""
    return bool(REPO_URL_RE.match(url)) and not re.search(r"://[^/]*@", url)


def repo_name(url: str) -> str:
    tail = re.split(r"[/:]", url.rstrip("/"))[-1]
    return tail[:-4] if tail.endswith(".git") else tail


def read_utf8(path: Path, docs: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise UsageError(f"{path.relative_to(docs).as_posix()}: not valid UTF-8 ({exc.reason} at byte {exc.start})") \
            from exc


# ----------------------------------------------------------------------------- report

class Report:
    def __init__(self) -> None:
        self.blockers: list[dict] = []
        self.warnings: list[dict] = []

    @staticmethod
    def _entry(kind: str, ident: str, message: str, file: str | None) -> dict:
        entry = {"kind": kind, "id": ident, "message": message}
        if file:
            entry["file"] = file
        return entry

    def block(self, kind: str, ident: str, message: str, file: str | None = None) -> None:
        self.blockers.append(self._entry(kind, ident, message, file))

    def warn(self, kind: str, ident: str, message: str, file: str | None = None) -> None:
        self.warnings.append(self._entry(kind, ident, message, file))


# ----------------------------------------------------------------------------- artifacts

class Artifact:
    def __init__(self, kind: str, rel: str, text: str) -> None:
        self.kind = kind
        self.rel = rel
        self.id = Path(rel).stem
        self.text = text
        self.fm: dict | None = None
        self.fm_text = ""
        self.body = text
        if text.startswith("---\n"):
            parts = text.split("---\n", 2)
            if len(parts) == 3:
                try:
                    loaded = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    loaded = None
                if isinstance(loaded, dict):
                    self.fm = iso_dates(loaded)
                    self.fm_text = parts[1]
                    self.body = parts[2]

    @property
    def target(self) -> str:
        return f"{TARGET_FOLDER[self.kind]}/{self.id}.md"


def load_artifacts(docs: Path, report: Report) -> tuple[dict[str, dict[str, Artifact]], dict[str, dict[str, list[str]]]]:
    """Artifacts by kind and id, and the files with a blocker (kind -> id -> files), which stay unconverted."""
    found: dict[str, dict[str, Artifact]] = {}
    blocked: dict[str, dict[str, list[str]]] = {}
    for kind, globs in ARTIFACT_GLOBS.items():
        found[kind], blocked[kind] = {}, {}
        files: dict[str, list[Artifact]] = {}
        for folder, pattern in globs:
            for path in sorted((docs / folder).glob(pattern)):
                art = Artifact(kind, path.relative_to(docs).as_posix(), read_utf8(path, docs))
                if ID_RE[kind].match(art.id):
                    files.setdefault(art.id, []).append(art)
        for ident, arts in files.items():
            ok = len(arts) == 1
            if not ok:
                report.block("duplicate_id", ident, f"defined by {', '.join(a.rel for a in arts)}", arts[-1].rel)
            for art in arts:
                title = art.fm.get("title") if art.fm is not None else None
                if art.fm is None:
                    report.block("bad_frontmatter", ident, "frontmatter missing or malformed", art.rel)
                elif str(art.fm.get("id")) != ident:
                    report.block("id_mismatch", ident,
                                 f"frontmatter id {art.fm.get('id')!r} differs from the file name", art.rel)
                elif not isinstance(title, str) or len(title.strip()) < 3:
                    report.block("missing_title", ident,
                                 f"frontmatter title {title!r} is not a string of at least 3 characters", art.rel)
                else:
                    continue
                ok = False
            if ok:
                found[kind][ident] = arts[0]
            else:
                blocked[kind][ident] = [a.rel for a in arts]
    return found, blocked


def product_index(docs: Path) -> dict[str, str]:
    """RF rows of the `## Indice RF` section of product.md: id -> title."""
    path = docs / "product.md"
    if not path.is_file():
        return {}
    rows: dict[str, str] = {}
    inside = False
    for line in read_utf8(path, docs).splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().lower().startswith("indice rf")
            continue
        m = re.match(r"^\|\s*(RF-\d{2,3})\s*\|\s*(.+?)\s*\|$", line) if inside else None
        if m:
            rows.setdefault(m.group(1), m.group(2))
    return rows


# ----------------------------------------------------------------------------- body rewriting

def fence_mask(lines: list[str]) -> list[bool]:
    mask, inside = [], False
    for line in lines:
        if line.lstrip().startswith("```"):
            mask.append(True)
            inside = not inside
            continue
        mask.append(inside)
    return mask


def heading_level(line: str) -> int:
    m = re.match(r"^(#{1,6})\s", line)
    return len(m.group(1)) if m else 0


def ref_cell(cell: str) -> str | None:
    m = re.match(r"^[*`\[]*(RF-\d{2,3})[*`\]]*$", cell.strip())
    return m.group(1) if m else None


def is_reference_line(line: str, titles: dict[str, set[str]]) -> bool:
    """True when the line holds RF references and their titles only."""
    s = line.strip()

    def title_ok(ident: str, text: str) -> bool:
        text = text.strip()
        return not text or norm_title(text) in titles.get(ident, set())

    if s.startswith("|"):
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            return True
        if [c.casefold() for c in cells] in (["rf"], ["rf", "titolo"], ["rf", "title"],
                                             ["requisito", "titolo"], ["id", "titolo"]):
            return True
        ident = ref_cell(cells[0]) if cells else None
        return bool(ident) and len(cells) <= 2 and title_ok(ident, cells[1] if len(cells) == 2 else "")
    m = re.match(r"^[-*+]\s+[*`\[]*(RF-\d{2,3})[*`\]]*(?:\s*(?:[—–:]|-)\s*(.*))?$", s)
    if m:
        return title_ok(m.group(1), m.group(2) or "")
    segments = [seg.strip().rstrip(".").strip() for seg in s.split("·")]
    for seg in segments:
        m = re.match(r"^`?(RF-\d{2,3})`?\s*(.*)$", seg)
        if not m or not title_ok(m.group(1), m.group(2)):
            return False
    return bool(segments)


def remove_section(lines: list[str], headings: tuple[str, ...], titles: dict[str, set[str]]
                   ) -> tuple[list[str], int, list[str]]:
    """Remove `## <heading>` sections made of references only. Returns lines, removed, kept."""
    removed, kept = 0, []
    i = 0
    while i < len(lines):
        mask = fence_mask(lines)
        line = lines[i]
        if mask[i] or heading_level(line) != 2 or line[3:].strip().casefold() not in headings:
            i += 1
            continue
        end = i + 1
        while end < len(lines) and not (not mask[end] and (0 < heading_level(lines[end]) <= 2
                                                          or re.fullmatch(r"(-{3,}|\*{3,})\s*", lines[end]))):
            end += 1
        content = [ln for ln in lines[i + 1:end] if ln.strip()]
        if content and all(not mask[i + 1 + k] for k in range(end - i - 1)) and \
                all(is_reference_line(ln, titles) for ln in content):
            at_end = end == len(lines)
            lines = lines[:i] + lines[end:]
            if at_end:
                while lines and not lines[-1].strip():
                    lines.pop()
            removed += 1
            continue
        kept.append(line.strip())
        i = end
    return lines, removed, kept


def header_line_pure(key: str, value: str, epic_signed: bool) -> bool:
    v = value.strip().strip("[]").strip()
    if v.casefold().strip('"') in PLACEHOLDER_VALUES:
        return True
    tokens = [t for t in re.split(r"[\s,·;/]+", v) if t]
    if key == "RF covered":
        return all(ID_RE["rf"].match(t.strip("`*")) for t in tokens)
    if key == "Dependencies":
        return all(ID_RE["epic"].match(t.strip("`*")) for t in tokens)
    if key == "Area":
        return all(t.strip("`*").lower() in AREA_TOKENS for t in tokens)
    return epic_signed  # Validated by: the signature now lives in state.json


def dependencies_from_header(body: str) -> list[str]:
    deps: list[str] = []
    lines = body.splitlines()
    mask = fence_mask(lines)
    for line, fenced in zip(lines, mask):
        m = HEADER_LINE_RE.match(line)
        if not fenced and m and m.group(1) == "Dependencies":
            deps += re.findall(r"Epic\d{3}", m.group(2))
    return deps


def rewrite_h1(lines: list[str], wanted: str) -> tuple[list[str], str | None, bool]:
    """Set the first H1 to `wanted`. Returns lines, old H1 (None if absent), changed."""
    mask = fence_mask(lines)
    for i, line in enumerate(lines):
        if not mask[i] and heading_level(line) == 1:
            if line.rstrip() == wanted:
                return lines, line, False
            return lines[:i] + [wanted] + lines[i + 1:], line, True
    lead = 0
    while lead < len(lines) and not lines[lead].strip():
        lead += 1
    return [""] + [wanted, ""] + lines[lead:], None, True


def filter_frontmatter(fm_text: str, fm: dict, keep: tuple[str, ...]) -> str:
    """Keep the top-level YAML blocks of `keep`, verbatim and in their original order."""
    out, keeping = [], True
    for line in fm_text.splitlines(keepends=True):
        m = re.match(r"^([A-Za-z_\"'][^:#]*?)\s*:(\s|$)", line)
        if m and not line[0].isspace():
            keeping = m.group(1).strip("\"'") in keep
        if keeping:
            out.append(line)
    text = "".join(out)
    wanted = {k: v for k, v in fm.items() if k in keep}
    try:
        reloaded = iso_dates(yaml.safe_load(text) or {})
    except yaml.YAMLError:
        reloaded = None
    if reloaded != wanted:
        text = yaml.safe_dump(wanted, sort_keys=False, allow_unicode=True, width=10_000)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


# ----------------------------------------------------------------------------- migration

class Migration:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.docs: Path = args.docs
        self.report = Report()
        self.counts: Counter = Counter()
        self.outputs: dict[str, str] = {}   # rel path -> new text (converted .md)
        self.moves: dict[str, str] = {}     # old rel -> new rel
        self.deletes: list[str] = []

    # -- sources ------------------------------------------------------------------------------

    def load_json(self, rel: str) -> dict:
        path = self.docs / rel
        try:
            data = json.loads(read_utf8(path, self.docs))
        except json.JSONDecodeError as exc:
            raise UsageError(f"{rel}: not valid JSON ({exc})") from exc
        if not isinstance(data, dict):
            raise UsageError(f"{rel}: the top level is a JSON {type(data).__name__}, not an object")
        return data

    def load(self) -> None:
        if not (self.docs / ".asf" / "state.json").is_file():
            raise UsageError(f"{self.docs / '.asf' / 'state.json'}: not found")
        self.audit = StateAudit()
        self.old = self.audit.track(self.load_json(".asf/state.json"))
        recap = ".asf/recap-source.json"
        self.recap = self.load_json(recap) if (self.docs / recap).is_file() else {}
        self.art, self.blocked = load_artifacts(self.docs, self.report)
        self.index = product_index(self.docs)
        functional = self.old.get("requirements")
        rf_items: list[dict] = []
        if isinstance(functional, dict):
            for section in functional.get("sections") or []:
                rf_items += items_of(section.get("requirements"))
            rf_items += items_of(functional.get("functional"))
        else:
            rf_items = items_of(functional)
        self.old_rf = self.by_id(rf_items, "rf", "requirements")
        rnf_items = items_of(self.old.get("nfrs"))
        if isinstance(functional, dict):
            rnf_items += items_of(functional.get("non_functional"))
        self.old_rnf = self.by_id(rnf_items, "rnf", "nfrs")
        self.old_epics = self.by_id(items_of(self.old.get("epics")), "epic", "epics")
        self.old_bugs = self.by_id(items_of(self.old.get("bugs")), "bug", "bugs")
        self.old_us = self.by_id(items_of(self.old.get("user_stories")), "us", "user_stories")
        self.old_tasks = self.by_id(items_of(self.old.get("tasks")), "task", "tasks")

    def by_id(self, items: list[dict], kind: str, where: str) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for item in items:
            ident = str(item.get("id"))
            if ident in out:
                self.report.block("duplicate_id", ident, f"listed twice in state.json `{where}`: the first is kept",
                                  ".asf/state.json")
                self.audit.consume_node(item)
                continue
            out[ident] = item
        return out

    def pick(self, kind: str, ident: str, field: str, state_item: dict | None, fm_key: str | None = None,
             label: str | None = None, aliases: tuple[str, ...] = ()) -> Any:
        """state.json wins over frontmatter (ADR-020); every disagreement is reported.
        `aliases` are pre-8.3 names of the same state.json field (spec: `state` → `status`, `pts` → `points`)."""
        art = self.art[kind].get(ident)
        fm_val = art.fm.get(fm_key or field) if art else None
        st_val = next((v for v in ((state_item or {}).get(f) for f in (field, *aliases)) if v is not None), None)
        if st_val is not None and fm_val is not None and st_val != fm_val:
            self.report.warn("state_frontmatter_disagreement", ident,
                             f"{label or field}: state.json {st_val!r}, frontmatter {fm_val!r} — state.json wins",
                             art.rel if art else None)
        return st_val if st_val is not None else fm_val

    def title_of(self, kind: str, ident: str) -> str | None:
        art = self.art[kind].get(ident)
        if art and art.fm.get("title"):
            return str(art.fm["title"])
        return None

    # -- build ---------------------------------------------------------------------------------

    def build(self) -> None:
        rep = self.report
        self.repos = self.collect_repos()
        self.signatures = self.collect_signatures()

        # requirements.functional
        self.rf: dict[str, dict] = {}
        for ident in sorted_ids(set(self.old_rf) | set(self.art["rf"])):
            st = self.old_rf.get(ident)
            art = self.art["rf"].get(ident)
            if st is None:
                rep.warn("missing_in_state", ident, "RF file without a state.json entry: status taken from frontmatter",
                         art.rel)
            item = {"id": ident, "status": self.pick("rf", ident, "status", st, label="status")}
            priority = self.pick("rf", ident, "priority", st, label="priority")
            if priority is not None:
                item["priority"] = priority
            self.rf[ident] = item

        # requirements.non_functional
        self.rnf: dict[str, dict] = {}
        self.rnf_epics: dict[str, list[str]] = {}
        for ident in sorted_ids(set(self.old_rnf) | set(self.art["rnf"])):
            st = self.old_rnf.get(ident)
            art = self.art["rnf"].get(ident)
            if st is None:
                rep.warn("missing_in_state", ident, "RNF file without a state.json entry: status taken from frontmatter",
                         art.rel)
            item = {"id": ident, "status": self.pick("rnf", ident, "status", st, label="status")}
            for field in ("verified_at", "verified_by", "priority"):
                value = self.pick("rnf", ident, field, st)
                if value is not None:
                    item[field] = value
            self.rnf[ident] = item
            epics = as_list((st or {}).get("epic_ref")) + as_list(art.fm.get("epic") if art else None)
            self.rnf_epics[ident] = sorted_ids(epics)

        # bugs
        self.bugs: dict[str, dict] = {}
        for ident in sorted_ids(set(self.old_bugs) | set(self.art["bug"])):
            st = self.old_bugs.get(ident)
            art = self.art["bug"].get(ident)
            fm = art.fm if art else {}
            if st is None:
                rep.warn("missing_in_state", ident, "bug file without a state.json entry: status taken from frontmatter",
                         art.rel)
            item = {"id": ident, "status": self.pick("bug", ident, "status", st, label="status"),
                    "severity": self.pick("bug", ident, "severity", st, label="severity")}
            rf_refs = as_list(fm.get("requirements")) if art else as_list((st or {}).get("rf_refs"))
            if art and st and st.get("rf_refs") is not None and sorted_ids(as_list(st["rf_refs"])) != sorted_ids(rf_refs):
                rep.warn("state_frontmatter_disagreement", ident,
                         f"RF refs: state.json {sorted_ids(as_list(st['rf_refs']))}, frontmatter {sorted_ids(rf_refs)} "
                         "— relations come from frontmatter", art.rel)
            rnf_refs = as_list(fm.get("nfr")) + as_list((st or {}).get("nfr_refs")) + as_list((st or {}).get("rnf_refs"))
            if rf_refs:
                item["rf_refs"] = sorted_ids(rf_refs)
            if rnf_refs:
                item["rnf_refs"] = sorted_ids(rnf_refs)
            dup = fm.get("duplicate_of") or (st or {}).get("duplicate_of")
            if dup:
                item["duplicate_of"] = str(dup)
            self.bugs[ident] = item

        # user stories
        self.stories: dict[str, dict] = {}
        story_epics: dict[str, list[str]] = {}
        for ident in sorted_ids(set(self.old_us) | set(self.art["us"])):
            st = self.old_us.get(ident)
            art = self.art["us"].get(ident)
            fm = art.fm if art else {}
            if st is None:
                rep.warn("missing_in_state", ident, "story file without a state.json entry", art.rel)
            rf_refs = as_list(fm.get("requirements")) if art else as_list((st or {}).get("rf_refs"))
            if art and st and st.get("rf_refs") is not None and sorted_ids(as_list(st["rf_refs"])) != sorted_ids(rf_refs):
                rep.warn("state_frontmatter_disagreement", ident,
                         f"RF refs: state.json {sorted_ids(as_list(st['rf_refs']))}, frontmatter {sorted_ids(rf_refs)} "
                         "— relations come from frontmatter", art.rel)
            item = {"id": ident, "rf_refs": sorted_ids(rf_refs)}
            priority = self.pick("us", ident, "priority", st, label="priority")
            if priority is not None:
                item["priority"] = priority
            self.stories[ident] = item
            story_epics[ident] = sorted_ids(as_list(fm.get("epic")) + as_list((st or {}).get("epic_ref")))

        # tasks, grouped by their `epic`
        self.tasks: dict[str, dict] = {}
        self.task_epic: dict[str, str] = {}
        self.task_nfr: dict[str, list[str]] = {}
        for ident in sorted_ids(self.art["task"]):
            art = self.art["task"][ident]
            fm = art.fm
            epic = str(fm.get("epic") or ident.rsplit(".", 1)[0].split(".", 1)[1])
            if not ident.startswith(f"Task.{epic}."):
                rep.block("task_epic_mismatch", ident, f"frontmatter epic {epic} differs from the id prefix", art.rel)
                continue
            st = self.old_tasks.get(ident)
            item: dict[str, Any] = {"id": ident, "status": self.pick("task", ident, "status", st, label="status")}
            points = self.pick("task", ident, "points", st, label="points", aliases=("pts", "story_points"))
            if points is not None:
                if points in POINTS:
                    item["points"] = points
                else:
                    rep.warn("dropped_value_lost", ident, f"points {points!r} is not one of {list(POINTS)}: omitted",
                             art.rel)
            for src, dst in (("requirements", "rf_refs"), ("bugs", "bug_refs"), ("depends_on", "depends_on")):
                refs = as_list(fm.get(src))
                if refs:
                    item[dst] = sorted_ids(refs)
            if st is not None and ("rf_refs" in st or "rf_ref" in st):
                st_refs = sorted_ids(as_list(st.get("rf_refs")) + as_list(st.get("rf_ref")))
                if st_refs != item.get("rf_refs", []):
                    rep.warn("state_frontmatter_disagreement", ident,
                             f"RF refs: state.json {st_refs}, frontmatter {item.get('rf_refs', [])} "
                             "— relations come from frontmatter", art.rel)
            files = self.files_for(ident, self.pick("task", ident, "layer", st, label="layer"), art.rel)
            if files:
                item["files"] = files
            self.tasks[ident] = item
            self.task_epic[ident] = epic
            self.task_nfr[ident] = as_list(fm.get("nfr"))

        # epics
        self.epics: dict[str, dict] = {}
        self.epic_sprint: dict[str, int] = {}
        self.old_signatures: dict[str, dict] = {}
        for ident in sorted_ids(set(self.old_epics) | set(self.art["epic"])):
            st = self.old_epics.get(ident)
            art = self.art["epic"].get(ident)
            fm = art.fm if art else {}
            if st is None:
                rep.warn("missing_in_state", ident, "epic file without a state.json entry: status taken from frontmatter",
                         art.rel)
            item: dict[str, Any] = {"id": ident, "status": self.pick("epic", ident, "status", st, label="status",
                                                                     aliases=("state",))}
            pp = self.pick("epic", ident, "product_priority", st)
            if pp is not None:
                item["product_priority"] = pp
            kind = self.pick("epic", ident, "kind", st, aliases=("type",))
            if kind is not None:
                if kind in EPIC_KIND:
                    item["kind"] = kind
                else:
                    rep.warn("dropped_value_lost", ident, f"kind {kind!r} is not one of {list(EPIC_KIND)}: omitted",
                             art.rel if art else None)
            old = st or {}
            deps = (dependencies_from_header(art.body) if art else []) + as_list(old.get("depends_on"))
            if deps:
                item["depends_on"] = sorted_ids(deps)
            stories = as_list(fm.get("stories")) + as_list(old.get("user_story_refs"))
            stories += [s for s, eps in story_epics.items() if ident in eps]
            if stories:
                item["user_story_refs"] = sorted_ids(stories)
            rnfs = as_list(fm.get("nfr")) + as_list(old.get("rnf_refs"))
            rnfs += [r for r, eps in self.rnf_epics.items() if ident in eps]
            rnfs += [r for t, e in self.task_epic.items() if e == ident for r in self.task_nfr[t]]
            if rnfs:
                item["rnf_refs"] = sorted_ids(rnfs)
            item["tasks"] = [t for t in sorted_ids(self.task_epic) if self.task_epic[t] == ident]
            old_sig = {k: old.get(k) for k in ("validated_by", "validated_at") if old.get(k) not in (None, "")}
            if old_sig:
                self.old_signatures[ident] = old_sig
            sprint = self.pick("epic", ident, "sprint", st)
            sprint_id = (st or {}).get("sprint_id")
            if sprint is None:
                sprint = sprint_id
            elif sprint_id not in EMPTY and str(sprint_id) != str(sprint):
                rep.warn("dropped_value_lost", ident, f"state.json sprint_id {sprint_id!r} differs from sprint "
                         f"{sprint!r}: sprint wins", art.rel if art else None)
            if sprint is not None:
                try:
                    self.epic_sprint[ident] = int(sprint)
                except (TypeError, ValueError):
                    rep.warn("dropped_value_lost", ident, f"sprint {sprint!r} is not a sprint number: omitted",
                             art.rel if art else None)
            self.epics[ident] = item
        for t, e in self.task_epic.items():
            if e not in self.epics and e not in self.blocked["epic"]:
                rep.block("unresolved_reference", t, f"epic {e} does not exist", self.art["task"][t].rel)

        self.story_epics = story_epics
        self.state_without_file()
        self.validate_values()
        self.build_sprints()
        self.build_roadmap()
        self.prune()
        self.sign_epics()

    def state_without_file(self) -> None:
        """Leave out items whose file has a blocker; report state.json entries without a file."""
        tables = {"rf": (self.rf, self.old_rf), "rnf": (self.rnf, self.old_rnf), "bug": (self.bugs, self.old_bugs),
                  "us": (self.stories, self.old_us), "epic": (self.epics, self.old_epics),
                  "task": (self.tasks, self.old_tasks)}
        for kind, (table, old) in tables.items():
            for ident in sorted_ids(old):
                if ident in self.blocked[kind]:
                    if ident in table:
                        table[ident]["_invalid"] = True
                elif ident not in self.art[kind] and not (kind == "rf" and ident in self.index):
                    # Values that lived in the missing .md; other unread values are reported by the audit.
                    lost = [k for k, v in old[ident].items() if k in STATE_IN_MD[kind] and v not in EMPTY]
                    where = f"{TARGET_FOLDER[kind]}/{ident}.md" + (" or a product.md index row" if kind == "rf" else "")
                    rep_msg = f"in state.json without {where}" + (": left out of 8.3" if kind == "task" else "")
                    rep_msg += f"; dropped {', '.join(lost)}" if lost else ""
                    self.report.warn("missing_file", ident, rep_msg)

    def validate_values(self) -> None:
        rep = self.report
        checks = (("rf", self.rf, "status", WORK_STATUS), ("rnf", self.rnf, "status", RNF_STATUS),
                  ("bug", self.bugs, "status", BUG_STATUS), ("bug", self.bugs, "severity", SEVERITY),
                  ("epic", self.epics, "status", WORK_STATUS), ("task", self.tasks, "status", WORK_STATUS))
        for kind, table, field, allowed in checks:
            for ident, item in table.items():
                if not item.get("_invalid") and item.get(field) not in allowed:
                    art = self.art[kind].get(ident)
                    rep.block("invalid_value", ident, f"{field} {item.get(field)!r} is not one of {list(allowed)}",
                              art.rel if art else None)
                    item["_invalid"] = True
        for kind, table in (("rf", self.rf), ("rnf", self.rnf), ("us", self.stories)):
            for ident, item in table.items():
                if "priority" in item and item["priority"] not in PRIORITY:
                    art = self.art[kind].get(ident)
                    rep.warn("dropped_value_lost", ident, f"priority {item['priority']!r} is not one of "
                             f"{list(PRIORITY)}: omitted", art.rel if art else None)
                    del item["priority"]
        for ident, item in self.epics.items():
            pp = item.get("product_priority")
            if pp is not None and not (isinstance(pp, int) and not isinstance(pp, bool) and pp >= 1):
                rep.warn("dropped_value_lost", ident, f"product_priority {pp!r} is not an integer ≥1: omitted")
                del item["product_priority"]
        for ident, item in self.rnf.items():
            if item.get("_invalid"):
                continue
            by, at = item.get("verified_by"), item.get("verified_at")
            bad = (by is None) != (at is None) or (by is not None and (not PERSONA_RE.match(str(by))
                                                                      or str(by).startswith("agent:")))
            needs = item["status"] in ("satisfied", "at_risk", "violated")
            if bad or (needs and by is None) or (item["status"] == "unverified" and by is not None):
                art = self.art["rnf"].get(ident)
                rep.block("invalid_value", ident, f"verified_by/verified_at {by!r}/{at!r} do not fit status "
                          f"{item['status']!r}", art.rel if art else None)
                item["_invalid"] = True
        for ident, item in self.bugs.items():
            if item.get("_invalid"):
                continue
            if (item["status"] == "duplicate") != ("duplicate_of" in item):
                art = self.art["bug"].get(ident)
                rep.block("invalid_value", ident, "duplicate_of must be present exactly when status is duplicate",
                          art.rel if art else None)
                item["_invalid"] = True

    def build_sprints(self) -> None:
        rep = self.report
        # The current sprint: recap-source and state.json `sprint` (state.json wins); v8.2 names it
        # with `id`, `start_date`, `end_date` and `goal`.
        block: dict[str, Any] = {}
        for src in (self.recap.get("sprint"), self.old.get("sprint")):
            if not isinstance(src, dict):
                continue
            for key, names in SPRINT_BLOCK_KEYS:
                value = next((v for v in [src.get(n) for n in names] if v is not None), None)
                if value is not None:
                    block[key] = value
        current = block.get("current")
        current = int(current) if current is not None else None
        nxt = block.get("next")
        declared: dict[int, dict] = {}
        for src in items_of(self.recap.get("sprints")) + items_of(self.old.get("sprints")):
            number = src.get("id", src.get("number"))
            if number is not None:
                declared.setdefault(int(number), src)
        numbers = set(declared) | set(self.epic_sprint.values())
        if current is not None:
            numbers.add(current)
        if nxt is not None:
            numbers.add(int(nxt))
        overrides = dict(self.args.closed_on)
        dates = dict(self.args.sprint_dates)
        closed_in_note = {int(n): d for n, d in re.findall(r"Sprint\s+(\d+)\s+chius[oa] il (\d{4}-\d{2}-\d{2})",
                                                          str(block.get("note") or ""))}
        self.sprints: dict[int, dict] = {}
        claims: dict[str, dict[int, list[str]]] = {}
        for e, n in self.epic_sprint.items():
            claims.setdefault(e, {}).setdefault(n, []).append("the epic's sprint")
        for n in sorted(declared):
            for e in as_list(declared[n].get("epic_refs")):
                claims.setdefault(e, {}).setdefault(n, []).append(f"sprints[{n}].epic_refs")
        for e in sorted_ids(claims):
            if len(claims[e]) > 1:
                chosen = max(claims[e])
                rep.warn("epic_in_many_sprints", e,
                         "claimed by " + "; ".join(f"sprint {n} ({', '.join(src)})" for n, src in sorted(claims[e].items()))
                         + f": kept in the latest, sprint {chosen}")
            self.epic_sprint[e] = max(claims[e])
        numbers |= set(self.epic_sprint.values())
        for n in sorted(numbers):
            src = declared.get(n, {})
            status = src.get("status", src.get("state"))
            status = {"current": "active"}.get(status, status)
            if status not in ("planned", "active", "closed"):
                status = ("closed" if n < current else "active" if n == current else "planned") \
                    if current is not None else "planned"
            item: dict[str, Any] = {"id": n, "status": status}
            start = src.get("start_date", src.get("starts_at"))
            end = src.get("end_date", src.get("ends_at"))
            goal = src.get("goal", src.get("note"))
            if n == current:
                start = start or block.get("starts_at")
                end = end or block.get("ends_at")
                goal = goal if goal is not None else block.get("note")
            if n in dates:
                start, end = dates[n]
            if start:
                item["start_date"] = str(start)
            if end:
                item["end_date"] = str(end)
            if status == "closed":
                closed = overrides.get(n) or src.get("closed_on") or closed_in_note.get(n)
                if closed:
                    item["closed_on"] = str(closed)
                else:
                    rep.block("closed_sprint_without_date", f"Sprint {n}",
                              f"sprint {n} is closed but no closing date was found: pass --closed-on {n}=YYYY-MM-DD")
                    item["_invalid"] = True
            elif n in overrides:
                rep.warn("closed_on_ignored", f"Sprint {n}", f"--closed-on given for sprint {n}, which is {status}")
            if goal is not None:
                item["goal"] = str(goal)
            if status == "active" and not (start and end):
                rep.block("invalid_value", f"Sprint {n}", "active sprint without start_date and end_date")
                item["_invalid"] = True
            self.sprints[n] = item
        for n in sorted(set(overrides) | set(dates)):
            if n not in self.sprints:
                rep.warn("sprint_override_ignored", f"Sprint {n}", f"--closed-on/--sprint-dates given for sprint {n}, "
                         "which is not declared")
        active = [n for n, s in self.sprints.items() if s["status"] == "active"]
        if len(active) > 1:
            rep.block("many_active_sprints", ", ".join(f"Sprint {n}" for n in active),
                      "more than one active sprint: all of them are left out")
            for n in active:
                self.sprints[n]["_invalid"] = True

    def build_roadmap(self) -> None:
        """v8.2 `roadmap.sections[]` (or an 8.3 `roadmap[]`) -> `roadmap[]`; every other stage field is reported."""
        rep = self.report
        node = self.old.get("roadmap")
        stages = node.get("sections") if isinstance(node, dict) else node
        self.roadmap: list[dict] = []
        if stages in EMPTY:
            return
        if not isinstance(stages, list):
            rep.warn("dropped_value_lost", "roadmap", f"{compact(stages)}: not a list of stages: omitted", ".asf/state.json")
            self.audit.consume(self.old, "roadmap")
            return
        seen: set[str] = set()
        for stage in stages:
            where = audit_label(stage)
            self.audit.consume_node(stage)
            if not isinstance(stage, dict):
                rep.warn("dropped_value_lost", "roadmap", f"{compact(stage)}: not a stage object: omitted",
                         ".asf/state.json")
                continue
            sid, title = stage.get("id"), stage.get("title")
            if sid in EMPTY or isinstance(sid, bool) or not isinstance(title, str) or not title.strip():
                rep.warn("dropped_value_lost", where, f"{compact(stage)}: a stage needs an id and a title: omitted",
                         ".asf/state.json")
                continue
            sid = str(sid)
            if sid in seen:
                rep.block("duplicate_id", sid, "roadmap stage listed twice in state.json: the first is kept",
                          ".asf/state.json")
                continue
            seen.add(sid)
            item: dict[str, Any] = {"id": sid, "title": title}
            for key in ("start_date", "end_date"):
                value = stage.get(key)
                if valid_date(value):
                    item[key] = value
                elif value not in EMPTY:
                    rep.warn("dropped_value_lost", f"{where}.{key}", f"{compact(value)} is not a YYYY-MM-DD date: omitted",
                             ".asf/state.json")
            item["_epic_refs"] = as_list(stage.get("epic_refs"))
            for key in stage:
                if key not in ROADMAP_KEYS and stage[key] not in EMPTY:
                    hint = ": it belongs in Roadmap.md" if key == "description" else ""
                    rep.warn("dropped_value_lost", f"{where}.{key}", f"{compact(stage[key])}: not carried to 8.3{hint}",
                             ".asf/state.json")
            self.roadmap.append(item)

    def prune(self) -> None:
        """Drop items with blockers, then drop what depended on them, until nothing changes."""
        rep = self.report
        existed = {"rf": set(self.rf), "rnf": set(self.rnf), "bug": set(self.bugs), "us": set(self.stories),
                   "epic": set(self.epics), "task": set(self.tasks)}
        for kind, ids in self.blocked.items():
            existed[kind] |= set(ids)
        for table in (self.rf, self.rnf, self.bugs, self.stories, self.epics, self.tasks):
            for ident in [i for i, it in table.items() if it.pop("_invalid", False)]:
                table.pop(ident)
        for ident in sorted_ids(i for i, e in self.task_epic.items() if e not in self.epics and i in self.tasks):
            self.tasks.pop(ident)
            if self.task_epic[ident] in existed["epic"]:
                rep.warn("reference_to_blocked_item", ident, f"left out with its epic {self.task_epic[ident]}",
                         self.art["task"][ident].rel)
        for n in [n for n, s in self.sprints.items() if s.pop("_invalid", False)]:
            self.sprints.pop(n)
        live = {"rf": self.rf, "rnf": self.rnf, "bug": self.bugs, "us": self.stories, "epic": self.epics,
                "task": self.tasks}
        self.removed_refs: set[tuple[str, str, str]] = set()

        def resolve(owner_kind: str, owner: str, item: dict, field: str, target: str) -> bool:
            """Check refs; False when the owner must go (reference to an id that never existed)."""
            refs = item.get(field)
            if refs is None:
                return True
            single = isinstance(refs, str)
            refs = [refs] if single else refs
            art = self.art[owner_kind].get(owner)
            missing = [r for r in refs if r not in existed[target]]
            if missing or (owner in refs and field in ("depends_on", "duplicate_of")):
                why = f"{field}: {', '.join(missing)} not found" if missing else f"{field}: refers to itself"
                rep.block("unresolved_reference", owner, why, art.rel if art else None)
                return False
            gone = [r for r in refs if r not in live[target]]
            if gone:
                if (owner_kind, owner, field) not in self.removed_refs:
                    self.removed_refs.add((owner_kind, owner, field))
                    rep.warn("reference_to_blocked_item", owner,
                             f"{field}: {', '.join(gone)} left out of state.json (blocker): reference dropped",
                             art.rel if art else None)
                kept = [r for r in refs if r in live[target]]
                if single or not kept:
                    item.pop(field)
                else:
                    item[field] = kept
            return True

        changed = True
        while changed:
            changed = False
            for ident in list(self.tasks):
                t = self.tasks[ident]
                ok = all(resolve("task", ident, t, f, k) for f, k in
                         (("rf_refs", "rf"), ("bug_refs", "bug"), ("depends_on", "task")))
                epic = self.epics.get(self.task_epic[ident])
                if ok and epic is not None and "rnf_refs" not in epic and not (t.get("rf_refs") or t.get("bug_refs")):
                    rep.block("task_without_citation", ident,
                              "cites neither an RF nor a bug, and its epic has no rnf_refs", self.art["task"][ident].rel)
                    ok = False
                if not ok:
                    self.tasks.pop(ident)
                    changed = True
            for ident in list(self.epics):
                e = self.epics[ident]
                e["tasks"] = [t for t in e["tasks"] if t in self.tasks]
                ok = all(resolve("epic", ident, e, f, k) for f, k in
                         (("user_story_refs", "us"), ("rnf_refs", "rnf"), ("depends_on", "epic")))
                if ok and not e["tasks"]:
                    art = self.art["epic"].get(ident)
                    rep.block("epic_without_tasks", ident, "epic without tasks: left out of state.json",
                              art.rel if art else None)
                    ok = False
                if not ok:
                    self.epics.pop(ident)
                    for t in [t for t, ep in self.task_epic.items() if ep == ident and t in self.tasks]:
                        self.tasks.pop(t)
                        rep.warn("reference_to_blocked_item", t, f"left out with its epic {ident}",
                                 self.art["task"][t].rel)
                    changed = True
            for ident in list(self.stories):
                s = self.stories[ident]
                ok = resolve("us", ident, s, "rf_refs", "rf")
                if ok and not s.get("rf_refs"):
                    art = self.art["us"].get(ident)
                    rep.block("story_without_rf", ident, "story without RF references", art.rel if art else None)
                    ok = False
                if not ok:
                    self.stories.pop(ident)
                    changed = True
            for ident in list(self.bugs):
                b = self.bugs[ident]
                if not all(resolve("bug", ident, b, f, k) for f, k in
                           (("rf_refs", "rf"), ("rnf_refs", "rnf"), ("duplicate_of", "bug"))):
                    self.bugs.pop(ident)
                    changed = True
        # a story in at most one epic
        owners: dict[str, list[str]] = {}
        for ident, e in self.epics.items():
            for s in e.get("user_story_refs", []):
                owners.setdefault(s, []).append(ident)
        for s, eps in sorted(owners.items()):
            if len(eps) > 1:
                rep.block("story_in_many_epics", s, f"listed by {', '.join(eps)}")
                for ident in eps:
                    self.epics[ident]["user_story_refs"].remove(s)
                    if not self.epics[ident]["user_story_refs"]:
                        del self.epics[ident]["user_story_refs"]
        # sprint epic_refs
        for n, sprint in self.sprints.items():
            refs = [e for e, sn in self.epic_sprint.items() if sn == n]
            unknown = [e for e in refs if e not in existed["epic"]]
            if unknown:
                rep.block("unresolved_reference", f"Sprint {n}",
                          f"epic_refs: {', '.join(sorted_ids(unknown))} not found: reference dropped")
            gone = [e for e in refs if e in existed["epic"] and e not in self.epics]
            if gone:
                rep.warn("reference_to_blocked_item", f"Sprint {n}",
                         f"epic_refs: {', '.join(sorted_ids(gone))} left out of state.json (blocker)")
            kept = sorted_ids(e for e in refs if e in self.epics)
            if kept:
                sprint["epic_refs"] = kept
        for e, n in sorted(self.epic_sprint.items()):
            if e in self.epics and n not in self.sprints:
                rep.warn("reference_to_blocked_item", e, f"sprint {n} left out of state.json: the epic is now in the backlog")
        # roadmap epic_refs: an epic in at most one stage, the first that lists it
        claimed: dict[str, str] = {}
        for stage in self.roadmap:
            refs = stage.pop("_epic_refs")
            unknown = [e for e in refs if e not in existed["epic"]]
            if unknown:
                rep.block("unresolved_reference", f"roadmap {stage['id']}",
                          f"epic_refs: {', '.join(sorted_ids(unknown))} not found: reference dropped")
            gone = [e for e in refs if e in existed["epic"] and e not in self.epics]
            if gone:
                rep.warn("reference_to_blocked_item", f"roadmap {stage['id']}",
                         f"epic_refs: {', '.join(sorted_ids(gone))} left out of state.json (blocker)")
            kept = []
            for e in sorted_ids(e for e in refs if e in self.epics):
                if e in claimed:
                    rep.warn("epic_in_many_stages", e, f"listed by roadmap stages {claimed[e]} and {stage['id']}: "
                             f"kept in the first, {claimed[e]}")
                else:
                    claimed[e] = stage["id"]
                    kept.append(e)
            if kept:
                stage["epic_refs"] = kept

    def sign_epics(self) -> None:
        """Signature of done epics: the `approva` commit, else a valid pre-8.3 `validated_by`/`validated_at`."""
        for ident, e in self.epics.items():
            art = self.art["epic"].get(ident)
            old = self.old_signatures.get(ident, {})
            by, at = old.get("validated_by"), old.get("validated_at")
            old_ok = isinstance(by, str) and PERSONA_RE.match(by) and not by.startswith("agent:") and valid_date(at)
            sig = self.signatures.get(ident)
            used = False
            if e["status"] == "done":
                if sig:
                    e["validated_by"], e["validated_at"] = sig["by"], sig["at"]
                    used = (by, at) == (sig["by"], sig["at"])
                elif old_ok:
                    e["validated_by"], e["validated_at"] = by, at
                    used = True
                else:
                    e["status"] = "review"
                    self.report.warn("epic_done_to_review", ident,
                                     "done without an `approva` commit carrying an Approved-by trailer: set to review",
                                     art.rel if art else None)
            if old and not used:
                if sig and e["status"] == "done":
                    why = "replaced by the `approva` commit"
                elif not old_ok:
                    why = "not a `Name <email>` persona with a YYYY-MM-DD date"
                else:
                    why = "the epic is not done"
                self.report.warn("dropped_value_lost", ident,
                                 f"state.json validated_by/validated_at {by!r}/{at!r}: {why}", art.rel if art else None)

    # -- external sources ---------------------------------------------------------------------

    def collect_repos(self) -> list[str]:
        """project.repos: the old state.json `project.repos` (list or v8.2 object), overridden by the CLI."""
        rep = self.report
        old_project = self.old.get("project") if isinstance(self.old.get("project"), dict) else {}
        old_repos = old_project.get("repos")
        seeded = [old_repos[k] for k in old_repos] if isinstance(old_repos, dict) else as_list(old_repos)
        cli: list[tuple[str, str]] = []
        root = self.args.repos_root
        if root:
            for d in sorted(p for p in root.iterdir() if p.is_dir() and (p / ".git").exists()):
                out = git(d, "config", "--get", "remote.origin.url")
                if out and out.strip():
                    cli.append((out.strip(), f"origin of {d}"))
                else:
                    rep.warn("repo_without_origin", d.name, f"{d}: git repo without an origin remote")
        cli += [(u, "--repo") for u in self.args.repo]

        def usable(raw: Any, source: str) -> str | None:
            url = strip_credentials(str(raw)) if isinstance(raw, str) else None
            if url is None or not repo_url_ok(url):
                kind = "dropped_value_lost" if source == "state.json" else "repo_url_rejected"
                shown = url if url is not None else raw
                rep.warn(kind, repo_name(url) if url else "project.repos",
                         f"{source}: {shown!r} is not an https://host/path or git@host:path URL: omitted")
                return None
            return url

        by_name: dict[str, str] = {}
        for raw in seeded:
            url = usable(raw, "state.json")
            if url and repo_name(url) in by_name and by_name[repo_name(url)] != url:
                rep.warn("dropped_value_lost", repo_name(url), f"state.json project.repos {url!r}: the name is already "
                         f"used by {by_name[repo_name(url)]!r}: omitted")
            elif url:
                by_name[repo_name(url)] = url
        from_cli: dict[str, str] = {}
        for raw, source in cli:
            url = usable(raw, source)
            if not url:
                continue
            name = repo_name(url)
            if name in from_cli and from_cli[name] != url:
                rep.block("duplicate_id", name, f"repo name used by {from_cli[name]} and {url}")
                continue
            from_cli[name] = url
            if name in by_name and by_name[name] != url:
                rep.warn("dropped_value_lost", name, f"state.json project.repos {by_name[name]!r} replaced by "
                         f"{url!r} ({source})")
            by_name[name] = url
        return [by_name[n] for n in sorted(by_name)]

    def collect_signatures(self) -> dict[str, dict]:
        out = git(self.docs, "log", "HEAD", "--format=%H%x1f%cs%x1f%(trailers:key=Approved-by,valueonly,separator=%x1e)%x1f%s%x1d")
        sigs: dict[str, dict] = {}
        if out is None:
            self.report.warn("no_git_history", "docs", "the docs tree has no readable git history: no epic signature")
            return sigs
        for record in out.split("\x1d"):
            parts = record.strip("\n").split("\x1f")
            if len(parts) != 4:
                continue
            sha, date, trailers, subject = parts
            m = re.match(r"^approva (Epic\d{3})\b", subject)
            if not m or m.group(1) in sigs:
                continue
            people = [t.strip() for t in trailers.split("\x1e") if t.strip()]
            person = next((p for p in people if PERSONA_RE.match(p) and not p.startswith("agent:")), None)
            if person:
                sigs[m.group(1)] = {"by": person, "at": date, "sha": sha}
        return sigs

    def files_for(self, ident: str, layer: Any, rel: str) -> list[str]:
        names = {repo_name(u) for u in self.repos}
        if layer is None:
            return []
        layer = str(layer)
        if layer in names:
            return [f"{layer}/**"]
        root = self.args.repos_root
        if root and "api" in names and (root / "api" / layer).is_dir():
            return [f"api/{layer}/**"]
        self.report.warn("layer_not_mappable", ident, f"layer {layer!r} is neither a repo nor an api/<layer> folder: "
                         "no files", rel)
        return []

    def prompt_stack(self) -> list[dict]:
        rep = self.report
        l0 = "AGENTS.md" if (self.docs / "AGENTS.md").is_file() else "CLAUDE.md"
        names = [n for n in (l0, *PROMPT_STACK_L1, *PROMPT_STACK_EXTRA) if (self.docs / n).is_file()]
        signed: dict[str, dict] = {}
        for entry in items_of(self.old.get("prompt_stack")):
            filename, by, at = entry.get("filename"), entry.get("validated_by"), entry.get("validated_at")
            where = audit_label(entry)
            if filename not in names:
                rep.warn("dropped_value_lost", where, f"{compact(entry)}: {filename!r} is not an L0/L1 file of the "
                         "standard present in the tree: entry dropped", ".asf/state.json")
                self.audit.consume_node(entry)
            elif by is not None or at is not None:
                if isinstance(by, str) and PERSONA_RE.match(by) and not by.startswith("agent:") and valid_date(at):
                    signed[filename] = {"validated_by": by, "validated_at": at}
                else:
                    rep.warn("dropped_value_lost", where, f"validated_by/validated_at {by!r}/{at!r}: not a "
                             "`Name <email>` persona with a YYYY-MM-DD date", ".asf/state.json")
        gates = self.old.get("gates") or self.recap.get("gates") or {}
        gate = gates.get("quality_gate_layer_1") if isinstance(gates, dict) else None
        out = []
        for name in names:
            item = {"filename": name, **signed.get(name, {})}
            if "validated_by" not in item:
                if gate and gate.get("status") == "signed":
                    why = (f"the L1 gate of {gate.get('signed_at')} names only the role "
                           f"{gate.get('signer_role')!r}, not a person: unsigned")
                else:
                    why = "no signature found: unsigned"
                rep.warn("prompt_stack_unsigned", name, why, name)
            out.append(item)
        return out

    # -- state.json ---------------------------------------------------------------------------

    def state(self) -> dict:
        out: dict[str, Any] = {"$schema": self.old.get("$schema") or "schema/state.schema.json",
                               "meta": {"schema_version": SCHEMA_VERSION, "asf_version": ASF_VERSION}}
        meta = self.old.get("meta") or {}
        old_project = self.old.get("project") if isinstance(self.old.get("project"), dict) else {}
        name = old_project.get("name") or meta.get("project") or self.recap.get("project")
        if not name:
            self.report.block("invalid_value", "project", "no project name in state.json or recap-source.json")
            name = ""
        project: dict[str, Any] = {"name": str(name)}
        if self.repos:
            project["repos"] = self.repos
        out["project"] = project
        ps = self.prompt_stack()
        if ps:
            out["prompt_stack"] = ps
        if self.sprints:
            out["sprints"] = [self.sprints[n] for n in sorted(self.sprints)]
        if self.roadmap:
            out["roadmap"] = self.roadmap
        epics = []
        for ident in sorted_ids(self.epics):
            e = self.epics[ident]
            epic = {k: e[k] for k in ("id", "status", "product_priority", "kind", "depends_on", "user_story_refs",
                                      "rnf_refs", "validated_by", "validated_at") if k in e}
            epic["tasks"] = [self.tasks[t] for t in e["tasks"]]
            epics.append(epic)
        out["epics"] = epics
        requirements: dict[str, Any] = {"functional": [self.rf[i] for i in sorted_ids(self.rf)]}
        if self.rnf:
            requirements["non_functional"] = [self.rnf[i] for i in sorted_ids(self.rnf)]
        out["requirements"] = requirements
        if self.stories:
            out["user_stories"] = [self.stories[i] for i in sorted_ids(self.stories)]
        if self.bugs:
            out["bugs"] = [self.bugs[i] for i in sorted_ids(self.bugs)]
        for key in DASHBOARD:
            if key in self.old:
                out[key] = json.loads(json.dumps(self.old[key]))
                self.audit.consume(self.old, key)
        return out

    # -- analysis warnings ---------------------------------------------------------------------

    def relation_warnings(self) -> None:
        rep = self.report
        rf_new: dict[str, set[str]] = {}
        bug_new: dict[str, set[str]] = {}
        for e in self.epics.values():
            for t in e["tasks"]:
                for r in self.tasks[t].get("rf_refs", []):
                    rf_new.setdefault(r, set()).add(e["id"])
                for b in self.tasks[t].get("bug_refs", []):
                    bug_new.setdefault(b, set()).add(e["id"])
        for ident in sorted_ids(self.rf):
            st = self.old_rf.get(ident) or {}
            art = self.art["rf"].get(ident)
            old = st.get("epic_ref") if "epic_ref" in st else (art.fm.get("epic") if art else None)
            new = sorted_ids(rf_new.get(ident, ()))
            rel = art.rel if art else None
            if old and not new:
                rep.warn("rf_loses_epic", ident, f"was in {old}; no task cites it", rel)
            elif new and new != [old]:
                rep.warn("rf_epic_changed", ident, f"epic {old or 'none'} → {', '.join(new)} (epics of the tasks citing it)",
                         rel)
        for ident in sorted_ids(self.bugs):
            st = self.old_bugs.get(ident) or {}
            art = self.art["bug"].get(ident)
            old = st.get("epic_ref") or (art.fm.get("epic") if art else None)
            new = sorted_ids(bug_new.get(ident, ()))
            rel = art.rel if art else None
            if old and not new:
                rep.warn("bug_loses_epic", ident, f"was in {old}; no task fixes it", rel)
            elif new and new != [old]:
                rep.warn("bug_epic_changed", ident, f"epic {old or 'none'} → {', '.join(new)} (epics of the tasks fixing it)",
                         rel)
        listed = set(self.index)
        have = set(self.rf)
        if listed != have:
            parts = []
            if have - listed:
                parts.append(f"missing from the index: {', '.join(sorted_ids(have - listed))}")
            if listed - have:
                parts.append(f"not in state.json: {', '.join(sorted_ids(listed - have))}")
            rep.warn("product_index_mismatch", "product.md",
                     f"RF index lists {len(listed)} RF, state.json {len(have)}; " + "; ".join(parts), "product.md")

    def check_dropped(self, art: Artifact) -> None:
        """Every dropped frontmatter value must be in state.json or derivable; else warn."""
        rep, ident, fm = self.report, art.id, art.fm
        lost = lambda key, why: rep.warn("dropped_value_lost", ident, f"frontmatter `{key}`: {why}", art.rel)
        for key, value in fm.items():
            if key in KEEP[art.kind] or key in DROPPED_PLAIN[art.kind] or value in (None, [], ""):
                continue
            if art.kind == "rf" and key == "epic":
                continue  # derived from tasks; rf_loses_epic / rf_epic_changed report the change
            if art.kind == "rf" and key == "stories":
                missing = [s for s in as_list(value) if ident not in self.stories.get(s, {}).get("rf_refs", [])]
                if missing:
                    lost(key, f"{', '.join(missing)} do not list {ident} in user_stories[].rf_refs")
            elif art.kind == "rnf" and key == "epic":
                missing = [e for e in as_list(value) if ident not in self.epics.get(e, {}).get("rnf_refs", [])]
                if missing:
                    lost(key, f"{', '.join(missing)} not in state.json with this RNF in rnf_refs")
            elif art.kind == "epic" and key == "sprint":
                sprint = self.sprints.get(self.epic_sprint.get(ident), {})
                if ident not in sprint.get("epic_refs", []):
                    lost(key, f"sprint {value} does not list it in epic_refs")
            elif art.kind == "epic" and key in ("stories", "nfr"):
                field = "user_story_refs" if key == "stories" else "rnf_refs"
                missing = [v for v in as_list(value) if v not in self.epics[ident].get(field, [])]
                if missing:
                    lost(key, f"{', '.join(missing)} not in epics[].{field}")
            elif art.kind == "epic" and key == "bugs":
                fixed = {b for t in self.epics[ident]["tasks"] for b in self.tasks[t].get("bug_refs", [])}
                missing = [b for b in as_list(value) if b not in fixed]
                if missing:
                    lost(key, f"{', '.join(missing)} fixed by no task of the epic")
            elif art.kind == "epic" and key == "points":
                total = sum(self.tasks[t].get("points", 0) for t in self.epics[ident]["tasks"])
                if value != total:
                    lost(key, f"{value} differs from the sum of its task points ({total}), which replaces it")
            elif art.kind == "task" and key == "nfr":
                epic = self.epics[self.task_epic[ident]]
                missing = [r for r in as_list(value) if r not in epic.get("rnf_refs", [])]
                if missing:
                    lost(key, f"{', '.join(missing)} not in {epic['id']} rnf_refs")
            elif art.kind == "task" and key == "layer":
                continue  # layer_not_mappable reports a layer without files
            elif art.kind == "bug" and key == "points":
                total = sum(t.get("points", 0) for t in self.tasks.values() if ident in t.get("bug_refs", []))
                if value != total:
                    lost(key, f"{value} differs from the sum of the points of its fixing tasks ({total}), which replaces it")
            elif art.kind == "us" and key == "epic":
                missing = [e for e in as_list(value) if ident not in self.epics.get(e, {}).get("user_story_refs", [])]
                if missing:
                    lost(key, f"{', '.join(missing)} not in state.json with this story in user_story_refs")
            else:
                lost(key, f"{value!r} has no place in 8.3")

    # -- markdown ------------------------------------------------------------------------------

    def rf_titles(self) -> dict[str, set[str]]:
        titles: dict[str, set[str]] = {}
        for ident in set(self.rf) | set(self.old_rf) | set(self.art["rf"]) | set(self.index):
            cands = [self.title_of("rf", ident), (self.old_rf.get(ident) or {}).get("title"), self.index.get(ident)]
            titles[ident] = {norm_title(c) for c in cands if c}
        return titles

    def convert_markdown(self) -> None:
        rep = self.report
        titles = self.rf_titles()
        live = {"rf": self.rf, "rnf": self.rnf, "epic": self.epics, "task": self.tasks, "bug": self.bugs,
                "us": self.stories}
        for kind in ARTIFACT_GLOBS:
            for ident in sorted_ids(self.blocked[kind]):
                for rel in self.blocked[kind][ident]:
                    rep.warn("file_not_converted", ident, "left unconverted: the file has a blocker", rel)
            for ident in sorted_ids(self.art[kind]):
                art = self.art[kind][ident]
                if ident not in live[kind]:
                    rep.warn("file_not_converted", ident, "left unconverted: the item has a blocker", art.rel)
                    continue
                self.check_dropped(art)
                body = art.body.split("\n")
                if kind == "epic":
                    body = self.strip_header_lines(art, body)
                    body, removed, kept = remove_section(body, EPIC_RF_HEADINGS, titles)
                elif kind == "us":
                    body, removed, kept = remove_section(body, STORY_RF_HEADINGS, titles)
                else:
                    removed, kept = 0, []
                self.counts["body_blocks_removed"] += removed
                for heading in kept:
                    self.counts["body_blocks_kept"] += 1
                    rep.warn("body_block_kept", ident, f"`{heading}` holds more than references: kept", art.rel)
                wanted = f"# {ident} — {art.fm.get('title')}"
                body, old_h1, changed = rewrite_h1(body, wanted)
                if changed:
                    self.counts["h1_rewritten"] += 1
                    rep.warn("h1_rewritten", ident, f"{old_h1!r} → {wanted!r}" if old_h1 else f"H1 added: {wanted!r}",
                             art.target)
                fm_text = filter_frontmatter(art.fm_text, art.fm, KEEP[kind])
                text = "---\n" + fm_text + "---\n" + "\n".join(body)
                if not text.endswith("\n"):
                    text += "\n"
                if art.rel != art.target:
                    self.moves[art.rel] = art.target
                if text != art.text or art.rel != art.target:
                    self.outputs[art.target] = text
                    self.counts["md_rewritten"] += 1

    def strip_header_lines(self, art: Artifact, body: list[str]) -> list[str]:
        mask = fence_mask(body)
        out = []
        signed = "validated_by" in self.epics[art.id]
        for line, fenced in zip(body, mask):
            m = None if fenced else HEADER_LINE_RE.match(line)
            if m is None:
                out.append(line)
            elif header_line_pure(m.group(1), m.group(2), signed):
                self.counts["body_blocks_removed"] += 1
            else:
                out.append(line)
                self.counts["body_blocks_kept"] += 1
                self.report.warn("body_block_kept", art.id, f"`**{m.group(1)}**` holds more than references: kept",
                                 art.rel)
        return out

    # -- run -----------------------------------------------------------------------------------

    def run(self) -> dict:
        self.load()
        self.build()
        self.relation_warnings()
        self.new_state = self.state()
        self.convert_markdown()
        self.audit_state()
        self.deletes = [p for p in DROPPED_FILES if (self.docs / p).is_file()]
        self.installs = self.standard_files()
        self.cited_deletes()
        self.merge_tooling()
        self.counts.update({
            "epics": len(self.new_state["epics"]),
            "tasks": sum(len(e["tasks"]) for e in self.new_state["epics"]),
            "rf": len(self.new_state["requirements"]["functional"]),
            "rnf": len(self.new_state["requirements"].get("non_functional", [])),
            "bugs": len(self.new_state.get("bugs", [])),
            "stories": len(self.new_state.get("user_stories", [])),
            "sprints": len(self.new_state.get("sprints", [])),
            "prompt_stack": len(self.new_state.get("prompt_stack", [])),
            "repos": len(self.new_state["project"].get("repos", [])),
        })
        return self.new_state

    def audit_state(self) -> None:
        """Report every non-empty value of the input state.json that the migration did not read, unless the
        spec removes it as derived or kept elsewhere (`STATE_DERIVED`, `STATE_IN_MD`)."""
        audit = self.audit

        def lost(path: tuple, value: Any) -> None:
            self.report.warn("dropped_value_lost", state_path_label(path), f"{compact(value)}: not carried to 8.3",
                             ".asf/state.json")

        def walk(node: Tracked) -> None:
            for key, value in dict.items(node):
                path = node.path + (key,)
                if path in audit.consumed or value in EMPTY or removed_state_path(path):
                    continue
                children = [v for v in value if isinstance(v, Tracked)] if isinstance(value, list) else []
                if path in audit.reads:
                    if isinstance(value, Tracked):
                        walk(value)
                    for child in children:
                        if child.path not in audit.consumed:
                            walk(child)
                elif children and len(children) == len(value):
                    for child in children:  # one report per item: milestones[M1], attachments[a1]…
                        if child.path not in audit.consumed:
                            lost(child.path, child)
                else:
                    lost(path, value)

        walk(self.old)

    def cited_deletes(self) -> None:
        """Lines of files left in the tree that still cite a file the migration drops."""
        names = [Path(p).name for p in self.deletes]
        if not names:
            return
        replaced = {*self.deletes, *self.installs, ".asf/state.json"}
        for path in sorted(p for p in self.docs.rglob("*") if p.is_file()):
            rel = path.relative_to(self.docs).as_posix()
            if rel.startswith(".git/") or rel in replaced or rel in self.moves:
                continue
            text = self.outputs.get(rel)
            if text is None:
                try:
                    text = path.read_text(encoding="utf-8")
                except (UnicodeDecodeError, OSError):
                    continue
            for n, line in enumerate(text.splitlines(), 1):
                for name in names:
                    if name in line:
                        self.report.warn("dropped_file_cited", f"{rel}:{n}", f"cites {name}, which 8.3 drops", rel)

    def merge_tooling(self) -> None:
        """Pre-8.3 tooling that re-runs the KStudio reconciler on merge would rewrite the migrated files."""
        why = ("re-runs the pre-8.3 KStudio reconciler on merge and would rewrite migrated files: KStudio must "
               "support 8.3, or the driver and hooks must be removed, before the migrated tree is merged")
        attrs = self.docs / ".gitattributes"
        if attrs.is_file():
            for n, line in enumerate(attrs.read_text(encoding="utf-8").splitlines(), 1):
                fields = line.split()
                if fields and not fields[0].startswith("#") and fields[0].lstrip("/") == ".asf/state.json" and \
                        any(f.startswith("merge=") for f in fields[1:]):
                    self.report.warn("merge_driver_active", f".gitattributes:{n}",
                                     f"`{line.strip()}` assigns a merge driver to .asf/state.json; it {why}",
                                     ".gitattributes")
        for rel in RECAP_TOOLING:
            if (self.docs / rel).is_file():
                self.report.warn("merge_driver_active", rel, f"recap hook tooling: it {why}", rel)

    def standard_files(self) -> dict[str, bytes]:
        """Files of the standard copied into the tree: 8.3 schemas and validator."""
        files = {}
        for src, rel in STANDARD_FILES:
            if src.is_file():
                files[rel] = src.read_bytes()
            else:
                self.report.warn("standard_file_not_installed", rel, f"{src} not found: not installed")
        return files

    def write_tree(self, dest: Path) -> None:
        """All or nothing: stage every new file next to its target, then swap; on error restore the tree."""
        state_text = json.dumps(self.new_state, ensure_ascii=False, indent=2) + "\n"
        writes: dict[str, bytes] = dict(self.installs)
        writes.update((rel, text.encode("utf-8")) for rel, text in self.outputs.items())
        writes[".asf/state.json"] = state_text.encode("utf-8")
        removes = [rel for rel in (*self.deletes, *self.moves) if rel not in writes and (dest / rel).exists()]
        tag = f".asf9-{os.getpid()}"
        made_dirs: list[Path] = []
        staged: dict[str, Path] = {}
        backups: dict[str, Path] = {}
        placed: list[str] = []
        try:
            for rel, data in writes.items():
                target = dest / rel
                missing = [p for p in target.parents if not p.exists()]
                for d in reversed(missing):
                    d.mkdir()
                    made_dirs.append(d)
                tmp = target.with_name(f".{target.name}{tag}.new")
                staged[rel] = tmp
                tmp.write_bytes(data)
                if target.exists():
                    shutil.copymode(target, tmp)
                if rel in self.installs and rel.endswith(".py"):
                    tmp.chmod(0o755)
            for rel in (*writes, *removes):
                target = dest / rel
                if target.exists():
                    backup = target.with_name(f".{target.name}{tag}.old")
                    os.replace(target, backup)
                    backups[rel] = backup
            for rel, tmp in staged.items():
                os.replace(tmp, dest / rel)
                placed.append(rel)
        except OSError as exc:
            failed = []
            for step in ([lambda r=rel: (dest / r).unlink(missing_ok=True) for rel in placed]
                         + [lambda r=rel, b=b: os.replace(b, dest / r) for rel, b in backups.items()]
                         + [lambda t=t: t.unlink(missing_ok=True) for t in staged.values()]
                         + [lambda d=d: d.rmdir() for d in reversed(made_dirs)]):
                try:
                    step()
                except OSError as undo:
                    failed.append(str(undo))
            state = "the tree is unchanged" if not failed else f"ROLLBACK INCOMPLETE: {'; '.join(failed)}"
            raise UsageError(f"writing {dest}: {exc}; {state}") from exc
        for rel, backup in backups.items():
            try:
                backup.unlink()
            except OSError as exc:
                self.report.warn("leftover_backup", rel, f"could not remove {backup}: {exc}")


# ----------------------------------------------------------------------------- CLI

def iso_date(value: str) -> str:
    try:
        datetime.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{value!r} is not a valid date") from exc
    return value


def closed_on_arg(value: str) -> tuple[int, str]:
    m = re.fullmatch(r"(\d+)=(\d{4}-\d{2}-\d{2})", value)
    if not m:
        raise argparse.ArgumentTypeError(f"expected SPRINT=YYYY-MM-DD, got {value!r}")
    return int(m.group(1)), iso_date(m.group(2))


def sprint_dates_arg(value: str) -> tuple[int, tuple[str, str]]:
    m = re.fullmatch(r"(\d+)=(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})", value)
    if not m:
        raise argparse.ArgumentTypeError(f"expected SPRINT=YYYY-MM-DD..YYYY-MM-DD, got {value!r}")
    start, end = iso_date(m.group(2)), iso_date(m.group(3))
    if start > end:
        raise argparse.ArgumentTypeError(f"start {start} is after end {end} in {value!r}")
    return int(m.group(1)), (start, end)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Migrate an ASF docs tree to ASF 8.3.")
    p.add_argument("--docs", type=Path, required=True, help="docs tree to read")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--out", type=Path, help="write a converted copy of the docs tree here (must not exist or be empty)")
    mode.add_argument("--write", action="store_true", help="convert in place; refused when there are blockers")
    p.add_argument("--repos-root", type=Path, help="folder holding the project's git repos (origin -> project.repos)")
    p.add_argument("--repo", action="append", default=[], metavar="URL", help="repo URL for project.repos (repeatable)")
    p.add_argument("--closed-on", action="append", default=[], type=closed_on_arg, metavar="SPRINT=YYYY-MM-DD",
                   help="closing date of a closed sprint (repeatable, overrides the sprint note)")
    p.add_argument("--sprint-dates", action="append", default=[], type=sprint_dates_arg,
                   metavar="SPRINT=YYYY-MM-DD..YYYY-MM-DD",
                   help="start_date and end_date of a sprint (repeatable, overrides every other source)")
    p.add_argument("--report", type=Path, metavar="FILE.json", help="write the JSON report here")
    return p.parse_args(argv)


def human_report(mig: Migration, mode: str, exit_code: int) -> str:
    rep, c = mig.report, mig.counts
    lines = [f"ASF 8.3 migration of {mig.docs} ({mode})",
             f"migrated: {c['epics']} epics, {c['tasks']} tasks, {c['rf']} RF, {c['rnf']} RNF, {c['bugs']} bugs, "
             f"{c['stories']} stories, {c['sprints']} sprints, {c['prompt_stack']} prompt_stack files, {c['repos']} repos",
             f"markdown: {c['md_rewritten']} files rewritten, {c['h1_rewritten']} H1 rewritten, "
             f"{c['body_blocks_removed']} body blocks removed, {c['body_blocks_kept']} kept"]
    for title, entries in (("BLOCKERS", rep.blockers), ("WARNINGS", rep.warnings)):
        lines.append(f"\n{len(entries)} {title}")
        for kind, n in sorted(Counter(e["kind"] for e in entries).items()):
            lines.append(f"  {kind} ({n})")
            for e in entries:
                if e["kind"] == kind:
                    where = f" [{e['file']}]" if "file" in e else ""
                    lines.append(f"    {e['id']}: {e['message']}{where}")
    lines.append(f"\nexit {exit_code}")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    try:
        if not (args.docs / ".asf").is_dir():
            raise UsageError(f"{args.docs}: not a docs tree (no .asf/)")
        if args.repos_root and not args.repos_root.is_dir():
            raise UsageError(f"{args.repos_root}: not a directory")
        if args.out:
            docs, out = args.docs.resolve(), args.out.resolve()
            if out == docs or docs in out.parents:
                raise UsageError(f"{args.out}: --out must be outside --docs")
            if out.exists() and (not out.is_dir() or any(out.iterdir())):
                raise UsageError(f"{args.out}: exists and is not an empty directory")
        mig = Migration(args)
        mig.run()
        blockers = bool(mig.report.blockers)
        exit_code = 1 if blockers else 0
        if args.out:
            mode = f"--out {args.out}"
            existed = args.out.exists()
            try:
                shutil.copytree(args.docs, args.out, ignore=shutil.ignore_patterns(".git"), dirs_exist_ok=True)
                mig.write_tree(args.out)
            except (OSError, UsageError):
                if existed:
                    for child in args.out.iterdir():
                        shutil.rmtree(child) if child.is_dir() and not child.is_symlink() else child.unlink()
                else:
                    shutil.rmtree(args.out, ignore_errors=True)
                raise
        elif args.write:
            mode = "--write" + (" refused: blockers" if blockers else "")
            if not blockers:
                mig.write_tree(args.docs)
        else:
            mode = "dry run"
        rep = mig.report
        payload = {
            "docs": str(args.docs), "mode": mode, "exit_code": exit_code,
            "counts": {k: mig.counts[k] for k in ("epics", "tasks", "rf", "rnf", "bugs", "stories", "sprints",
                                                  "prompt_stack", "repos", "md_rewritten", "h1_rewritten",
                                                  "body_blocks_removed", "body_blocks_kept")},
            "summary": {"blockers": dict(sorted(Counter(e["kind"] for e in rep.blockers).items())),
                        "warnings": dict(sorted(Counter(e["kind"] for e in rep.warnings).items()))},
            "blockers": rep.blockers, "warnings": rep.warnings,
        }
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        sys.stdout.write(human_report(mig, mode, exit_code))
        return exit_code
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
