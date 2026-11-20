"""Compact raw introspection files into the schema data bundled with the SDK.

Usage (from the repository root):

    python schema/utils/build_sdk_schema.py          # all supported versions
    python schema/utils/build_sdk_schema.py 2026-10  # selected versions

Raw files live in schema/versions/<version>/introspection.json. Output goes to
src/shopify_partners_sdk/schema/data/partner_<version>.json. Versions that Shopify
no longer supports are skipped unless named explicitly.
"""

import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "schema" / "versions"
OUT_DIR = REPO_ROOT / "src" / "shopify_partners_sdk" / "schema" / "data"

# Versions Shopify supports as of the 2026-10 release (stable, release candidate,
# and unstable). Update this list when Shopify ships or retires a version.
SUPPORTED_VERSIONS = ["2026-01", "2026-04", "2026-07", "2026-10", "2027-01", "unstable"]


def type_ref(ref: dict[str, Any]) -> str:
    """Render an introspection type reference as GraphQL type syntax."""
    if ref["kind"] == "NON_NULL":
        return type_ref(ref["ofType"]) + "!"
    if ref["kind"] == "LIST":
        return "[" + type_ref(ref["ofType"]) + "]"
    return str(ref["name"])


def compact_field(raw: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "type": type_ref(raw["type"]),
        "args": {a["name"]: type_ref(a["type"]) for a in raw["args"]},
    }
    required = [
        a["name"]
        for a in raw["args"]
        if a["type"]["kind"] == "NON_NULL" and a.get("defaultValue") is None
    ]
    if required:
        out["required"] = required
    if raw.get("isDeprecated"):
        out["deprecated"] = True
    return out


def compact_type(raw: dict[str, Any]) -> dict[str, Any]:
    """Keep only what the SDK needs to type variables and validate selections."""
    out: dict[str, Any] = {"kind": raw["kind"]}
    if raw.get("fields"):
        out["fields"] = {f["name"]: compact_field(f) for f in raw["fields"]}
    if raw.get("inputFields"):
        out["inputFields"] = {
            f["name"]: type_ref(f["type"]) for f in raw["inputFields"]
        }
    if raw.get("enumValues"):
        out["enumValues"] = [e["name"] for e in raw["enumValues"]]
    if raw.get("possibleTypes"):
        out["possibleTypes"] = sorted(p["name"] for p in raw["possibleTypes"])
    if raw.get("interfaces"):
        out["interfaces"] = sorted(i["name"] for i in raw["interfaces"])
    return out


def compact_schema(introspection: dict[str, Any]) -> dict[str, Any]:
    schema = introspection["data"]["__schema"]
    return {
        "queryType": schema["queryType"]["name"],
        "mutationType": (schema.get("mutationType") or {}).get("name"),
        "types": {
            t["name"]: compact_type(t)
            for t in sorted(schema["types"], key=lambda t: t["name"])
            if not t["name"].startswith("__")
        },
    }


def dump(compact: dict[str, Any]) -> str:
    """Write one type per line so version bumps produce readable diffs."""
    header = {k: v for k, v in compact.items() if k != "types"}
    lines = [json.dumps(header, sort_keys=True)[:-1] + ', "types": {']
    entries = [
        f"{json.dumps(name)}: {json.dumps(body, sort_keys=True)}"
        for name, body in compact["types"].items()
    ]
    lines.append(",\n".join(entries))
    lines.append("}}")
    return "\n".join(lines) + "\n"


def build(version: str) -> Path:
    raw = json.loads((RAW_DIR / version / "introspection.json").read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    target = OUT_DIR / f"partner_{version}.json"
    target.write_text(dump(compact_schema(raw)))
    return target


def main(argv: list[str]) -> None:
    for version in argv or SUPPORTED_VERSIONS:
        path = build(version)
        print(f"{version}: {path.relative_to(REPO_ROOT)} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main(sys.argv[1:])
