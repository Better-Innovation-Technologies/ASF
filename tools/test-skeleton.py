#!/usr/bin/env python3
"""A project born from the standard validates with zero errors (D-8.28).

Builds, in a temporary folder, the docs repo a host creates at kickoff from `skeleton.json` — the
listed files and folders, the empty folders, a stub of each file the host writes, a generated `.asf/state.json`, the literal placeholders
resolved — and runs `tools/validate-stack.py` on it. Then it recomposes `instructions.md` from the
catalog the way a host does (header, every module between `asf:module` markers, Project rules) and
validates again, enough times that **every module of the catalog** is composed at least once:
a module whose text cites an id, a path or a section the born stack does not have fails here, not
in the first project that chooses it.

The compositions check text, not choices: they rotate through the modules of each category and do
not honour `requires`/`excludes`, which the host checks and which change no line of the result.

Usage:  python3 tools/test-skeleton.py
Needs what validate-stack.py needs (`pyyaml`, `jsonschema>=4.18`). Exits 0 with
`Skeleton valid: N stacks.`, or 1 with the validator's output of the first stack that fails.
"""
from __future__ import annotations

import datetime
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "instructions"
PROJECT = "Skeleton Test"
PLACEHOLDER = re.compile(r"\{\{([a-z][a-z0-9_]*)\}\}")
MODULE_END = "<!-- /asf:module -->"
RULES_MARK = "<!-- asf:project-rules -->"


def asf_version() -> str:
    head = (ROOT / "AGENTS.md").read_text(encoding="utf-8")[:2000]
    m = re.search(r"\*\*ASF v(\d+\.\d+(?:\.\d+)?)\*\*", head)
    return m.group(1) if m else "0.0"


def born(docs: Path, version: str) -> None:
    """The docs repo right after kickoff, as `skeleton.json` declares it."""
    skeleton = json.loads((ROOT / "skeleton.json").read_text(encoding="utf-8"))
    today = datetime.date.today().isoformat()
    values = {"[Project Name]": PROJECT, "{project_name}": PROJECT, "{asf_version}": version,
              "{date}": today}
    assert set(values) == set(skeleton["placeholders"]), "skeleton.json placeholders changed"
    sources = [ROOT / f for f in skeleton["files"]]
    for d in skeleton["dirs"]:
        sources += sorted(p for p in (ROOT / d).rglob("*") if p.is_file())
    for src in sources:
        rel = src.relative_to(ROOT)
        dst = docs / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix in (".md", ".json"):
            text = src.read_text(encoding="utf-8")
            for k, v in values.items():
                text = text.replace(k, v)
            dst.write_text(text, encoding="utf-8")
        else:
            shutil.copyfile(src, dst)
    for rel in skeleton["host_files"]:  # the host writes them with its own content: a stub here
        (docs / rel).write_text("validate-stack:\n  script: python3 tools/validate-stack.py\n",
                                encoding="utf-8")
    for d in skeleton["empty_dirs"]:
        (docs / d).mkdir(parents=True, exist_ok=True)
    schema = json.loads((ROOT / ".asf/schema/state.schema.json").read_text(encoding="utf-8"))
    schema_version = schema["properties"]["meta"]["properties"]["schema_version"]["enum"][-1]
    state = {"$schema": "schema/state.schema.json",
             "meta": {"schema_version": schema_version, "asf_version": version},
             "project": {"name": PROJECT}, "epics": [], "requirements": {"functional": []}}
    (docs / ".asf/state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def value(p: dict) -> str:
    if "default" in p:
        return p["default"]
    if p.get("enum"):
        return p["enum"][0]
    return {"path": "src/example", "version": "1.0"}.get(p["type"], "example")


def compose(catalog: dict, chosen: list[dict], version: str) -> str:
    host = {"project_name": PROJECT, "asf_version": version,
            "composed_at": datetime.date.today().isoformat(), "catalog_ref": "test"}
    order = {c["id"]: c["order"] for c in catalog["categories"]}

    def fill(text: str, values: dict) -> str:
        return PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), text)

    values = {**{p["name"]: value(p) for m in chosen for p in m.get("placeholders", [])}, **host}
    blocks = []
    for m in sorted(chosen, key=lambda m: (order[m["category"]], m["id"])):
        body = fill((CATALOG / m["file"]).read_text(encoding="utf-8"), values).strip("\n")
        blocks.append(f"<!-- asf:module id={m['id']} version={m['version']} -->\n{body}\n{MODULE_END}")
    head = fill((CATALOG / catalog["header"]).read_text(encoding="utf-8"), host).strip("\n")
    rules = (CATALOG / catalog["project_rules"]).read_text(encoding="utf-8").strip("\n")
    return "\n\n".join([head, *blocks, f"{RULES_MARK}\n{rules}"]) + "\n"


def selections(catalog: dict) -> list[list[dict]]:
    """Enough choices to compose every module once: the k-th of each category, k = 0, 1, …"""
    by_cat: dict[str, list[dict]] = {}
    for m in catalog["modules"]:
        by_cat.setdefault(m["category"], []).append(m)
    rounds = max(len(ms) for ms in by_cat.values())
    return [[ms[k % len(ms)] for ms in by_cat.values()] for k in range(rounds)]


def validate(docs: Path, label: str) -> bool:
    run = subprocess.run([sys.executable, str(docs / "tools/validate-stack.py"), "--docs", str(docs)],
                         capture_output=True, text=True)
    out = run.stdout + run.stderr
    if run.returncode != 0 or "Prompt Stack valid." not in out:
        print(f"{label}: the born stack does not validate\n{out}")
        return False
    return True


def main() -> int:
    version = asf_version()
    catalog = json.loads((CATALOG / "catalog.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        docs = Path(tmp) / "docs"
        born(docs, version)
        stacks = 1
        if not validate(docs, "hand-written instructions.md"):
            return 1
        composed = set()
        for n, chosen in enumerate(selections(catalog), 1):
            (docs / "instructions.md").write_text(compose(catalog, chosen, version), encoding="utf-8")
            stacks += 1
            if not validate(docs, f"composition {n} ({', '.join(m['id'] for m in chosen)})"):
                return 1
            composed |= {m["id"] for m in chosen}
        missing = {m["id"] for m in catalog["modules"]} - composed
        assert not missing, f"modules never composed: {sorted(missing)}"
    print(f"Skeleton valid: {stacks} stacks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
