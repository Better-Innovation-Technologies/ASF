#!/usr/bin/env python3
"""Validate the ASF instructions catalog (`instructions/catalog.json` and its modules).

Standard library only. Checks what the JSON schema cannot: every referenced file exists and nothing
else is in `modules/`; the placeholders a module declares are exactly the `{{name}}` it uses (host
placeholders excluded); `requires` and `excludes` name real modules; ids are unique and match their
file; every required category has exactly one default module, and a `one` category at most one;
the languages of a project are stated, never defaulted (D-8.30): no `prose_language` or
`business_language` placeholder carries a default, and no `language` module is the default.

Exits 0 with `Instructions catalog valid.`, or 1 with `N ERRORS:` and one line each.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{([a-z][a-z0-9_]*)\}\}")
#: Facts about the team that a default would deduce instead of asking (D-8.30).
STATED_PLACEHOLDERS = ("prose_language", "business_language")


def check(root: Path) -> list[str]:
    errors: list[str] = []
    catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    host = {p["name"] for p in catalog.get("host_placeholders", [])}
    categories = {c["id"]: c for c in catalog["categories"]}
    modules = catalog["modules"]
    ids = [m["id"] for m in modules]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"catalog.json: module id `{dup}` is not unique")
    known = set(ids)
    for name in ("header", "project_rules"):
        path = root / catalog[name]
        if not path.is_file():
            errors.append(f"catalog.json: `{name}` file {catalog[name]} does not exist")
        else:
            for used in sorted(set(PLACEHOLDER.findall(path.read_text(encoding="utf-8"))) - host):
                errors.append(f"{catalog[name]}: `{{{{{used}}}}}` is not a host placeholder")
    referenced = set()
    for m in modules:
        where = f"catalog.json: module `{m['id']}`"
        if m["category"] not in categories:
            errors.append(f"{where}: unknown category `{m['category']}`")
        expected = f"modules/{m['category']}/{m['id']}.md"
        if m["file"] != expected:
            errors.append(f"{where}: file must be {expected}, not {m['file']}")
        referenced.add(m["file"])
        path = root / m["file"]
        if not path.is_file():
            errors.append(f"{where}: file {m['file']} does not exist")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.lstrip().startswith(("## ", "<!--")):
            errors.append(f"{m['file']}: a module starts with a `## ` heading")
        used = set(PLACEHOLDER.findall(text)) - host
        declared = {p["name"] for p in m.get("placeholders", [])}
        for name in sorted(used - declared):
            errors.append(f"{m['file']}: uses `{{{{{name}}}}}` but `{m['id']}` does not declare it")
        for name in sorted(declared - used):
            errors.append(f"{where}: declares `{name}` but {m['file']} never uses it")
        for p in m.get("placeholders", []):
            if p["name"] in STATED_PLACEHOLDERS and "default" in p:
                errors.append(f"{where}: `{p['name']}` has a default, but a language is stated at "
                              f"composition, never deduced (D-8.30)")
        if m["category"] == "language" and m.get("default"):
            errors.append(f"{where}: a `language` module is never the default (D-8.30)")
        for group in m.get("requires", []):
            for ref in group:
                if ref not in known:
                    errors.append(f"{where}: requires unknown module `{ref}`")
        for ref in m.get("excludes", []):
            if ref not in known:
                errors.append(f"{where}: excludes unknown module `{ref}`")
    for path in sorted((root / "modules").rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if rel not in referenced:
            errors.append(f"{rel}: not referenced by catalog.json")
    for cid, cat in categories.items():
        defaults = [m["id"] for m in modules if m["category"] == cid and m.get("default")]
        if not any(m["category"] == cid for m in modules):
            errors.append(f"catalog.json: category `{cid}` has no modules")
        if cat["required"] and not defaults:
            errors.append(f"catalog.json: required category `{cid}` has no default module")
        if cat["cardinality"] == "one" and len(defaults) > 1:
            errors.append(f"catalog.json: category `{cid}` is `one` but has defaults {defaults}")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "instructions"
    errors = check(root)
    if errors:
        print(f"{len(errors)} ERRORS:")
        for e in errors:
            print(f"  {e}")
        return 1
    print("Instructions catalog valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
