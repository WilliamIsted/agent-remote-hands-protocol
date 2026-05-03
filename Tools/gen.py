#!/usr/bin/env python3
"""Spec generator.

Reads:
  - spec/verbs/*.json          per-verb strict-tool definitions with x-* extensions
  - spec/families.json         family declarations + per-family metadata (token paths, etc.)
  - spec/framing/*.md          hand-written markdown for non-verb PROTOCOL.md sections

Writes:
  - dist/PROTOCOL.md           framing sections + generated §4 (verbs by namespace)
  - dist/<family>/VERBS.md     per-family one-liner catalogue, filtered to verbs that
                               family actually implements
  - dist/verbs.json            concatenated strict-tool definitions with x-* stripped,
                               ready for `client.messages.create(tools=...)`

Run from the repo root:

    python Tools/gen.py
"""

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = REPO_ROOT / "spec"
DIST_DIR = REPO_ROOT / "dist"

# Order in which verb namespaces appear under §4. Mirrors the order PROTOCOL.md
# carried (system → screen → window → … → connection).
NAMESPACE_ORDER = [
    "system", "screen", "window", "input", "element",
    "file", "directory", "process", "registry", "clipboard",
    "watch", "connection",
]


# ---------------------------------------------------------------------------
# strip_x_extensions: 5-LOC helper at the API boundary
# ---------------------------------------------------------------------------

def strip_x_extensions(node):
    """Recursively remove every key starting with `x-`. Used at the API
    boundary; not used for rendering (we want the x-* metadata for that)."""
    if isinstance(node, dict):
        return {k: strip_x_extensions(v) for k, v in node.items() if not k.startswith("x-")}
    if isinstance(node, list):
        return [strip_x_extensions(v) for v in node]
    return node


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def load_verbs():
    verbs = []
    for path in sorted((SPEC_DIR / "verbs").glob("*.json")):
        with path.open(encoding="utf-8") as f:
            verbs.append(json.load(f))
    return verbs


def load_families():
    with (SPEC_DIR / "families.json").open(encoding="utf-8") as f:
        return json.load(f)["families"]


def load_framing():
    """Return list of (slug, content) pairs, sorted by filename ordinal."""
    framing_dir = SPEC_DIR / "framing"
    if not framing_dir.is_dir():
        return []
    out = []
    for path in sorted(framing_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        slug = path.stem
        out.append((slug, path.read_text(encoding="utf-8")))
    return out


# ---------------------------------------------------------------------------
# Type formatting
# ---------------------------------------------------------------------------

def format_type(prop_schema):
    """Render a property's type as a short bare-text string. Callers add
    backticks where appropriate — keeps composition (object inner, array
    items) free of nested-or-missing-backtick artefacts."""
    if "$ref" in prop_schema:
        return prop_schema["$ref"].rsplit("/", 1)[-1]
    if "const" in prop_schema:
        c = prop_schema["const"]
        return f'"{c}"' if isinstance(c, str) else repr(c)
    t = prop_schema.get("type")
    if t == "object":
        sub = prop_schema.get("properties", {})
        if sub:
            inner = ", ".join(f"{k}: {format_type(v)}" for k, v in sub.items())
            return "{" + inner + "}"
        return "object"
    if t == "array":
        items = prop_schema.get("items", {})
        return f"array of {format_type(items)}"
    if isinstance(t, list):  # union types (e.g. ["string", "null"])
        return " \\| ".join(t)
    if t is None:
        return "any"
    if "enum" in prop_schema:
        values = prop_schema.get("enum", [])
        if values and len(values) <= 5 and all(isinstance(v, str) for v in values):
            return " \\| ".join(f'"{v}"' for v in values)
        return f"{t} enum"
    return t


# ---------------------------------------------------------------------------
# Per-verb section rendering (used by dist/PROTOCOL.md §4)
# ---------------------------------------------------------------------------

def render_input_table(input_schema):
    props = input_schema.get("properties", {})
    if not props:
        return "_No inputs._"
    required = set(input_schema.get("required", []))
    rows = ["| Field | Type | Required | Notes |", "|---|---|---|---|"]
    for name, spec in props.items():
        type_str = format_type(spec)
        req = "yes" if name in required else "no"
        notes_parts = []
        if "default" in spec:
            notes_parts.append(f"Default: `{json.dumps(spec['default'])}`.")
        if "enum" in spec:
            enum_str = ", ".join(f"`{v}`" for v in spec["enum"])
            notes_parts.append(f"One of {enum_str}.")
        desc = spec.get("description", "")
        if desc:
            notes_parts.append(desc.replace("\n", " ").strip())
        notes = " ".join(notes_parts).strip() or "—"
        rows.append(f"| `{name}` | `{type_str}` | {req} | {notes} |")
    return "\n".join(rows)


def render_output_section(verb):
    out = verb.get("x-output-schema")
    if not out:
        return "_Not declared._"
    desc = out.get("description", "")
    t_str = format_type(out)
    line = f"`{t_str}`"
    if desc:
        line += f" — {desc}"

    # If the output is an object with properties, render the field table too.
    if out.get("type") == "object" and out.get("properties"):
        rows = ["", "| Field | Type | Notes |", "|---|---|---|"]
        required = set(out.get("required", []))
        for name, spec in out["properties"].items():
            type_str = format_type(spec)
            req_marker = " (required)" if name in required else ""
            field_desc = spec.get("description", "")
            if "enum" in spec and not field_desc.startswith("One of"):
                enum_str = ", ".join(f"`{v}`" for v in spec["enum"])
                field_desc = f"One of {enum_str}. {field_desc}".strip()
            rows.append(f"| `{name}`{req_marker} | `{type_str}` | {field_desc.replace(chr(10), ' ').strip()} |")
        line += "\n" + "\n".join(rows)
    return line


def render_event_section(verb):
    """Render x-event-schema section for watch.* verbs."""
    ev = verb.get("x-event-schema")
    if not ev:
        return None
    lines = ["", "**Event frames**"]
    desc = ev.get("description", "")
    if desc:
        lines.append("")
        lines.append(desc)
    if ev.get("type") == "object" and ev.get("properties"):
        lines.append("")
        lines.append("| Field | Type | Notes |")
        lines.append("|---|---|---|")
        required = set(ev.get("required", []))
        for name, spec in ev["properties"].items():
            type_str = format_type(spec)
            req_marker = " (required)" if name in required else ""
            field_desc = spec.get("description", "")
            if "enum" in spec and not field_desc.startswith("One of"):
                enum_str = ", ".join(f"`{v}`" for v in spec["enum"])
                field_desc = f"One of {enum_str}. {field_desc}".strip()
            lines.append(f"| `{name}`{req_marker} | `{type_str}` | {field_desc.replace(chr(10), ' ').strip()} |")
    return "\n".join(lines)


def render_family_block(family_name, family_data):
    """Render one x-families.<family> block."""
    if family_data.get("implemented") is False:
        reason = family_data.get("reason", "(no reason given)")
        return f"#### {family_name}\n\n_Not implemented._ **Reason:** {reason}"

    lines = [f"#### {family_name}", ""]
    desc = family_data.get("description", "").strip()
    if desc:
        lines.append(desc)
        lines.append("")

    chain = family_data.get("implementations_in_order")
    if chain:
        lines.append("**Backend chain (preferred → last-ditch):** " + " → ".join(f"`{b}`" for b in chain))
        lines.append("")

    fb = family_data.get("fallback_behavior")
    if fb:
        lines.append(f"**Exhausted-chain behaviour:** `{fb}`")
        lines.append("")

    hint = family_data.get("install_hint")
    if hint:
        lines.append(f"**Install hint:** {hint}")
        lines.append("")

    well_known = {"description", "implementations_in_order", "fallback_behavior",
                  "install_hint", "implemented", "reason"}
    extras = {k: v for k, v in family_data.items() if k not in well_known}
    if extras:
        lines.append("<details><summary>Additional family-specific metadata</summary>")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(extras, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")
        lines.append("</details>")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_verb_section(verb, families, section_no):
    """Render one verb as a markdown sub-section under §4.N."""
    name = verb["name"]
    crudx = verb.get("x-crudx", "?")
    since = verb.get("x-since", "?")
    mutex = verb.get("x-mutually-exclusive", [])

    lines = [f"#### {section_no} `{name}` ({crudx})", ""]

    desc = verb.get("description", "").strip()
    if desc:
        lines.append(desc)
        lines.append("")

    meta_bits = [f"**CRUDX:** {crudx}", f"**Since:** {since}"]
    if mutex:
        meta_bits.append("**Mutually exclusive:** " + ", ".join(f"`{m}`" for m in mutex))
    lines.append(" · ".join(meta_bits))
    lines.append("")

    lines.append("**Inputs**")
    lines.append("")
    lines.append(render_input_table(verb.get("input_schema", {})))
    lines.append("")

    lines.append("**Output**")
    lines.append("")
    lines.append(render_output_section(verb))
    lines.append("")

    errs = verb.get("x-errors", [])
    if errs:
        lines.append("**Errors:** " + ", ".join(f"`{e}`" for e in errs))
        lines.append("")
    else:
        lines.append("**Errors:** _none declared_")
        lines.append("")

    impls = verb.get("x-implementations", [])
    if impls:
        lines.append("**Implementations**")
        lines.append("")
        lines.append("| Backend | Available on | Notes |")
        lines.append("|---|---|---|")
        for impl in impls:
            iname = impl.get("name", "?")
            avail = ", ".join(f"`{f}`" for f in impl.get("available_on", []))
            inotes = impl.get("description", "").replace("\n", " ").strip()
            lines.append(f"| `{iname}` | {avail} | {inotes} |")
        lines.append("")

    event_block = render_event_section(verb)
    if event_block:
        lines.append(event_block)
        lines.append("")

    lines.append("**Per-family behaviour**")
    lines.append("")
    x_families = verb.get("x-families", {})
    if not x_families:
        lines.append("_No per-family overlays declared._")
        lines.append("")
    else:
        for family_name in families:
            if family_name in x_families:
                lines.append(render_family_block(family_name, x_families[family_name]))
                lines.append("")
        unknown = set(x_families) - set(families)
        for family_name in sorted(unknown):
            lines.append(f"_(unknown family `{family_name}`)_")
            lines.append("")
            lines.append(render_family_block(family_name, x_families[family_name]))
            lines.append("")
    return "\n".join(lines).rstrip()


# ---------------------------------------------------------------------------
# §4 generation: walk verbs grouped by namespace, in NAMESPACE_ORDER
# ---------------------------------------------------------------------------

def render_section_4(verbs, families):
    """Render the full §4 (Verbs by namespace) markdown."""
    by_ns = {}
    for verb in verbs:
        ns = verb.get("x-namespace", "?")
        by_ns.setdefault(ns, []).append(verb)

    # Stable verb order within a namespace: by name.
    for ns in by_ns:
        by_ns[ns].sort(key=lambda v: v["name"])

    namespaces = [ns for ns in NAMESPACE_ORDER if ns in by_ns]
    # Tail: any namespace not in the canonical order, alphabetised.
    tail = sorted(set(by_ns) - set(namespaces))
    namespaces.extend(tail)

    lines = ["## 4. Verbs by namespace", ""]
    lines.append("This section is generated from `spec/verbs/*.json`. Edit the per-verb files, not this section.")
    lines.append("")

    for n_idx, ns in enumerate(namespaces, start=1):
        lines.append(f"### 4.{n_idx} `{ns}.*`")
        lines.append("")
        for v_idx, verb in enumerate(by_ns[ns], start=1):
            lines.append(render_verb_section(verb, families, f"4.{n_idx}.{v_idx}"))
            lines.append("")

    return "\n".join(lines).rstrip()


# ---------------------------------------------------------------------------
# dist/PROTOCOL.md: framing concat + §4 splice
# ---------------------------------------------------------------------------

def render_token_file_table(families):
    """Render per-family token_file_path / token_file_acl as a markdown table.
    Substituted into the framing where `<!-- gen.py: token-file-table -->`
    appears."""
    rows = ["| Family | Token file path | ACL |", "|---|---|---|"]
    for fam_name, fam in families.items():
        if fam.get("_placeholder"):
            continue
        path = fam.get("token_file_path", "_(unspecified)_")
        acl = fam.get("token_file_acl", "_(unspecified)_")
        rows.append(f"| `{fam_name}` | `{path}` | {acl} |")
    return "\n".join(rows)


def apply_framing_substitutions(content, families):
    """Replace gen.py markers in framing content with rendered substitutions."""
    return content.replace(
        "<!-- gen.py: token-file-table -->",
        render_token_file_table(families),
    )


def render_protocol_md(verbs, families, framing):
    """Concat framing files in filename-ordinal order; splice generated §4
    between `03-*.md` and `05-*.md`."""
    parts = []
    section_4_inserted = False

    for slug, content in framing:
        ordinal = slug.split("-", 1)[0]
        try:
            n = int(ordinal)
        except ValueError:
            n = -1

        if n >= 5 and not section_4_inserted:
            parts.append(render_section_4(verbs, families))
            parts.append("\n\n---\n\n")
            section_4_inserted = True

        parts.append(apply_framing_substitutions(content, families).rstrip())
        parts.append("\n\n---\n\n")

    if not section_4_inserted:
        # No section >=5 in framing; append §4 at end.
        parts.append(render_section_4(verbs, families))

    # Trim final separator
    text = "".join(parts).rstrip()
    if text.endswith("---"):
        text = text[:-3].rstrip()
    return text + "\n"


# ---------------------------------------------------------------------------
# dist/<family>/VERBS.md: per-family one-liner catalogue
# ---------------------------------------------------------------------------

def verb_implemented_for(verb, family_name):
    """Is the verb implemented on this family?"""
    fam = verb.get("x-families", {}).get(family_name)
    if fam is None:
        return False
    if fam.get("implemented") is False:
        return False
    return True


def render_verbs_md(verbs, family_name, families_meta):
    """One-liner catalogue per verb for the given family. Filters out verbs
    not implemented on the family."""
    by_ns = {}
    for verb in verbs:
        if not verb_implemented_for(verb, family_name):
            continue
        ns = verb.get("x-namespace", "?")
        by_ns.setdefault(ns, []).append(verb)
    for ns in by_ns:
        by_ns[ns].sort(key=lambda v: v["name"])

    fam_meta = families_meta.get(family_name, {})
    fam_desc = fam_meta.get("description", "").strip()

    lines = [f"# Verb catalogue — `{family_name}`", ""]
    if fam_desc:
        lines.append(fam_desc)
        lines.append("")
    lines.append(f"One-line conceptual index of every verb the `{family_name}` agent implements. Generated from `spec/verbs/*.json` filtered by each verb's `x-families.{family_name}` slot. Verbs marked `implemented: false` for this family are omitted.")
    lines.append("")
    lines.append("Tier shorthand: **R** = read, **C** = create, **U** = update, **D** = delete, **X** = extra_risky.")
    lines.append("")
    lines.append("Read [`PROTOCOL.md`](../PROTOCOL.md) when you need full signatures, error codes, or framing details. Read [`LLM-OPERATORS.md`](../../LLM-OPERATORS.md) when you're an LLM driving an agent.")
    lines.append("")
    lines.append("---")
    lines.append("")

    namespaces = [ns for ns in NAMESPACE_ORDER if ns in by_ns]
    tail = sorted(set(by_ns) - set(namespaces))
    namespaces.extend(tail)

    for ns in namespaces:
        lines.append(f"## `{ns}.*`")
        lines.append("")
        for verb in by_ns[ns]:
            crudx = verb.get("x-crudx", "?")
            desc = verb.get("description", "").strip().split("\n")[0]
            # Use the first sentence (split on first ". " followed by capital or end-of-string).
            # Cheap heuristic — keeps the line tight.
            if desc.endswith("."):
                first_sentence = desc
            else:
                first_sentence = desc + "."
            # If multi-sentence, keep just the first.
            if ". " in first_sentence:
                first_sentence = first_sentence.split(". ", 1)[0] + "."
            lines.append(f"- `{verb['name']}` ({crudx}): {first_sentence}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# dist/verbs.json: concatenated strict-tool defs with x-* stripped
# ---------------------------------------------------------------------------

def render_verbs_json(verbs):
    return [strip_x_extensions(v) for v in verbs]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    verbs = load_verbs()
    families = load_families()
    framing = load_framing()

    DIST_DIR.mkdir(exist_ok=True)

    # 1. dist/PROTOCOL.md
    protocol_md = render_protocol_md(verbs, families, framing)
    (DIST_DIR / "PROTOCOL.md").write_text(protocol_md, encoding="utf-8")

    # 2. dist/<family>/VERBS.md per family
    for family_name in families:
        if families[family_name].get("_placeholder"):
            continue
        family_dir = DIST_DIR / family_name
        family_dir.mkdir(exist_ok=True)
        verbs_md = render_verbs_md(verbs, family_name, families)
        (family_dir / "VERBS.md").write_text(verbs_md, encoding="utf-8")

    # 3. dist/verbs.json
    api_tools = render_verbs_json(verbs)
    (DIST_DIR / "verbs.json").write_text(
        json.dumps(api_tools, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Report
    print(f"Wrote dist/PROTOCOL.md       ({len(protocol_md)} chars)")
    for family_name in families:
        if families[family_name].get("_placeholder"):
            continue
        path = DIST_DIR / family_name / "VERBS.md"
        if path.exists():
            print(f"Wrote dist/{family_name}/VERBS.md")
    print(f"Wrote dist/verbs.json        ({len(api_tools)} verbs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
