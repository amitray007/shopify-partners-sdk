#!/usr/bin/env python3
"""
Compare different schema versions to identify changes and differences
"""

import json
from pathlib import Path


def load_schema(version_path: str) -> dict:
    """Load a schema from the given path"""
    introspection_file = Path(version_path) / "introspection.json"
    if introspection_file.exists():
        with introspection_file.open(encoding="utf-8") as f:
            return json.load(f)
    return {}


def extract_types(schema: dict) -> dict[str, dict]:
    """Extract types from schema"""
    types = {}
    if (
        "data" in schema
        and "__schema" in schema["data"]
        and "types" in schema["data"]["__schema"]
    ):
        for type_info in schema["data"]["__schema"]["types"]:
            name = type_info.get("name")
            if name and not name.startswith("__"):  # Skip introspection types
                types[name] = type_info
    return types


def extract_operations(schema: dict) -> dict[str, list[str]]:
    """Extract queries and mutations from schema"""
    operations = {"queries": [], "mutations": []}

    if "data" not in schema or "__schema" not in schema["data"]:
        return operations

    schema_info = schema["data"]["__schema"]

    # Get query root type
    query_type_name = schema_info.get("queryType", {}).get("name")
    if query_type_name:
        for type_info in schema_info["types"]:
            if type_info.get("name") == query_type_name:
                operations["queries"] = [
                    f.get("name") for f in type_info.get("fields", []) if f.get("name")
                ]
                break

    # Get mutation root type
    mutation_type = schema_info.get("mutationType")
    if mutation_type:
        mutation_type_name = mutation_type.get("name")
        if mutation_type_name:
            for type_info in schema_info["types"]:
                if type_info.get("name") == mutation_type_name:
                    operations["mutations"] = [
                        f.get("name")
                        for f in type_info.get("fields", [])
                        if f.get("name")
                    ]
                    break

    return operations


def compare_versions():
    """Compare all schema versions"""
    schema_dirs = [
        "../versions/2024-10",
        "../versions/2025-01",
        "../versions/2025-04",
        "../versions/2025-07",
        "../versions/unstable",
    ]
    schemas = {}

    # Load all schemas
    for schema_dir in schema_dirs:
        version = schema_dir.split("/")[-1]
        schema = load_schema(schema_dir)
        if schema:
            schemas[version] = schema
            print(f"Loaded schema: {version}")

    if not schemas:
        print("No schemas found!")
        return

    # Compare schemas
    comparison_results = []
    versions = sorted(schemas.keys())

    for i in range(len(versions) - 1):
        current_version = versions[i]
        next_version = versions[i + 1]

        current_types = extract_types(schemas[current_version])
        next_types = extract_types(schemas[next_version])

        current_ops = extract_operations(schemas[current_version])
        next_ops = extract_operations(schemas[next_version])

        # Find differences
        added_types = set(next_types.keys()) - set(current_types.keys())
        removed_types = set(current_types.keys()) - set(next_types.keys())

        added_queries = set(next_ops["queries"]) - set(current_ops["queries"])
        removed_queries = set(current_ops["queries"]) - set(next_ops["queries"])

        added_mutations = set(next_ops["mutations"]) - set(current_ops["mutations"])
        removed_mutations = set(current_ops["mutations"]) - set(next_ops["mutations"])

        # Check for modified types
        modified_types = []
        common_types = set(current_types.keys()) & set(next_types.keys())

        for type_name in common_types:
            current_type = current_types[type_name]
            next_type = next_types[type_name]

            # Compare fields for object types
            if (
                current_type.get("kind") == "OBJECT"
                and next_type.get("kind") == "OBJECT"
            ):
                current_fields = {
                    f.get("name"): f
                    for f in current_type.get("fields", [])
                    if f.get("name")
                }
                next_fields = {
                    f.get("name"): f
                    for f in next_type.get("fields", [])
                    if f.get("name")
                }

                added_fields = set(next_fields.keys()) - set(current_fields.keys())
                removed_fields = set(current_fields.keys()) - set(next_fields.keys())

                if added_fields or removed_fields:
                    modified_types.append(
                        {
                            "name": type_name,
                            "added_fields": list(added_fields),
                            "removed_fields": list(removed_fields),
                        }
                    )

        comparison_results.append(
            {
                "from_version": current_version,
                "to_version": next_version,
                "added_types": list(added_types),
                "removed_types": list(removed_types),
                "added_queries": list(added_queries),
                "removed_queries": list(removed_queries),
                "added_mutations": list(added_mutations),
                "removed_mutations": list(removed_mutations),
                "modified_types": modified_types,
            }
        )

    # Generate report
    report_lines = []
    report_lines.append("# Schema Version Comparison Report")
    report_lines.append("=" * 50)
    report_lines.append("")

    for comparison in comparison_results:
        report_lines.append(
            f"## Changes from {comparison['from_version']} to {comparison['to_version']}"
        )
        report_lines.append("-" * 40)
        report_lines.append("")

        if comparison["added_types"]:
            report_lines.append("### Added Types:")
            for type_name in comparison["added_types"]:
                report_lines.append(f"- {type_name}")
            report_lines.append("")

        if comparison["removed_types"]:
            report_lines.append("### Removed Types:")
            for type_name in comparison["removed_types"]:
                report_lines.append(f"- {type_name}")
            report_lines.append("")

        if comparison["added_queries"]:
            report_lines.append("### Added Queries:")
            for query_name in comparison["added_queries"]:
                report_lines.append(f"- {query_name}")
            report_lines.append("")

        if comparison["removed_queries"]:
            report_lines.append("### Removed Queries:")
            for query_name in comparison["removed_queries"]:
                report_lines.append(f"- {query_name}")
            report_lines.append("")

        if comparison["added_mutations"]:
            report_lines.append("### Added Mutations:")
            for mutation_name in comparison["added_mutations"]:
                report_lines.append(f"- {mutation_name}")
            report_lines.append("")

        if comparison["removed_mutations"]:
            report_lines.append("### Removed Mutations:")
            for mutation_name in comparison["removed_mutations"]:
                report_lines.append(f"- {mutation_name}")
            report_lines.append("")

        if comparison["modified_types"]:
            report_lines.append("### Modified Types:")
            for mod_type in comparison["modified_types"]:
                report_lines.append(f"- **{mod_type['name']}**")
                if mod_type["added_fields"]:
                    report_lines.append(
                        f"  - Added fields: {', '.join(mod_type['added_fields'])}"
                    )
                if mod_type["removed_fields"]:
                    report_lines.append(
                        f"  - Removed fields: {', '.join(mod_type['removed_fields'])}"
                    )
                report_lines.append("")

        report_lines.append("")

    # Write comparison report
    output_file = "../analysis/version_comparison.md"
    with Path(output_file).open("w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"Version comparison report written to {output_file}")

    # Summary report
    summary_lines = []
    summary_lines.append("Schema Evolution Summary")
    summary_lines.append("=" * 30)

    for version, schema in schemas.items():
        types = extract_types(schema)
        operations = extract_operations(schema)

        summary_lines.append(f"\n{version}:")
        summary_lines.append(f"  - Types: {len(types)}")
        summary_lines.append(f"  - Queries: {len(operations['queries'])}")
        summary_lines.append(f"  - Mutations: {len(operations['mutations'])}")

    summary_file = "../analysis/evolution_summary.txt"
    with Path(summary_file).open("w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

    print(f"Evolution summary written to {summary_file}")


if __name__ == "__main__":
    compare_versions()
