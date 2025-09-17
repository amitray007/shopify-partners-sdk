#!/usr/bin/env python3
"""
Comprehensive GraphQL Schema Analyzer for Shopify Partners API
Analyzes all schema versions and extracts complete field structures including interfaces
"""

from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Optional


class GraphQLSchemaAnalyzer:
    def __init__(self):
        self.schemas = {}
        self.type_registry = {}
        self.interface_implementations = defaultdict(list)
        self.all_queries = {}
        self.all_mutations = {}
        self.version_differences = {}

    def load_all_schemas(self):
        """Load all schema versions"""
        schema_files = [
            "../versions/2024-10/introspection.json",
            "../versions/2025-01/introspection.json",
            "../versions/2025-04/introspection.json",
            "../versions/2025-07/introspection.json",
            "../versions/unstable/introspection.json",
        ]

        for schema_file in schema_files:
            if Path(schema_file).exists():
                version = schema_file.split("/")[2]
                print(f"Loading schema version: {version}")
                with Path(schema_file).open(encoding="utf-8") as f:
                    self.schemas[version] = json.load(f)

    def analyze_type(self, type_info: dict[str, Any]) -> str:
        """Recursively analyze GraphQL type structure"""
        if not type_info:
            return "Unknown"

        kind = type_info.get("kind", "")
        name = type_info.get("name", "")

        if kind == "NON_NULL":
            return f"{self.analyze_type(type_info.get('ofType', {}))}!"
        if kind == "LIST":
            return f"[{self.analyze_type(type_info.get('ofType', {}))}]"
        if kind in ["SCALAR", "OBJECT", "INTERFACE", "UNION", "ENUM", "INPUT_OBJECT"]:
            return name
        return f"{kind}({name})"

    def get_field_structure(
        self,
        type_name: str,
        schema_data: dict,
        visited: Optional[set[str]] = None,
        depth: int = 0,
    ) -> dict[str, Any]:
        """Get complete field structure for a type including nested fields"""
        if visited is None:
            visited = set()

        if depth > 3 or type_name in visited:  # Prevent infinite recursion
            return {"type": type_name, "fields": "... (recursive/deep nesting)"}

        visited.add(type_name)

        # Find the type definition
        type_def = None
        for type_info in schema_data["data"]["__schema"]["types"]:
            if type_info.get("name") == type_name:
                type_def = type_info
                break

        if not type_def:
            return {"type": type_name, "fields": "Type not found"}

        result = {
            "type": type_name,
            "kind": type_def.get("kind"),
            "description": type_def.get("description"),
            "fields": {},
        }

        # Handle different type kinds
        if type_def.get("kind") == "OBJECT" or type_def.get("kind") == "INTERFACE":
            fields = type_def.get("fields", [])
            for field in fields:
                field_name = field.get("name")
                field_type = self.analyze_type(field.get("type", {}))
                field_desc = field.get("description", "")
                field_args = field.get("args", [])

                field_info = {
                    "type": field_type,
                    "description": field_desc,
                    "isDeprecated": field.get("isDeprecated", False),
                    "deprecationReason": field.get("deprecationReason"),
                }

                # Add arguments if any
                if field_args:
                    field_info["arguments"] = {}
                    for arg in field_args:
                        arg_name = arg.get("name")
                        arg_type = self.analyze_type(arg.get("type", {}))
                        arg_desc = arg.get("description", "")
                        arg_default = arg.get("defaultValue")

                        field_info["arguments"][arg_name] = {
                            "type": arg_type,
                            "description": arg_desc,
                            "defaultValue": arg_default,
                        }

                # For object types, get nested structure (limited depth)
                base_type = (
                    field_type.replace("!", "").replace("[", "").replace("]", "")
                )
                if depth < 2 and base_type not in [
                    "String",
                    "Int",
                    "Boolean",
                    "ID",
                    "Float",
                    "DateTime",
                    "Url",
                    "Money",
                ]:
                    field_info["nestedFields"] = self.get_field_structure(
                        base_type, schema_data, visited.copy(), depth + 1
                    )

                result["fields"][field_name] = field_info

        elif type_def.get("kind") == "ENUM":
            enum_values = type_def.get("enumValues", [])
            result["enumValues"] = [ev.get("name") for ev in enum_values]

        elif type_def.get("kind") == "UNION":
            possible_types = type_def.get("possibleTypes", [])
            result["possibleTypes"] = [pt.get("name") for pt in possible_types]

        # Handle interfaces
        if type_def.get("kind") == "INTERFACE":
            # Find implementations
            implementations = []
            for type_info in schema_data["data"]["__schema"]["types"]:
                if type_info.get("kind") == "OBJECT":
                    interfaces = type_info.get("interfaces", [])
                    for interface in interfaces:
                        if interface.get("name") == type_name:
                            implementations.append(type_info.get("name"))
            result["implementations"] = implementations

        visited.remove(type_name)
        return result

    def analyze_interface_implementations(
        self, schema_data: dict
    ) -> dict[str, list[str]]:
        """Find all interface implementations"""
        implementations = defaultdict(list)

        for type_info in schema_data["data"]["__schema"]["types"]:
            if type_info.get("kind") == "OBJECT":
                interfaces = type_info.get("interfaces", [])
                type_name = type_info.get("name")

                for interface in interfaces:
                    interface_name = interface.get("name")
                    implementations[interface_name].append(type_name)

        return dict(implementations)

    def build_complete_query_example(
        self, query_name: str, query_info: dict, schema_data: dict
    ) -> str:
        """Build complete GraphQL query example with all fields"""
        query_type = self.analyze_type(query_info.get("type", {}))
        args = query_info.get("args", [])

        # Build query structure
        query_parts = [f"query {query_name.title()}Query"]

        # Add variables if there are arguments
        variables = []
        argument_list = []

        for arg in args:
            arg_name = arg.get("name")
            arg_type = self.analyze_type(arg.get("type", {}))
            variables.append(f"${arg_name}: {arg_type}")
            argument_list.append(f"{arg_name}: ${arg_name}")

        if variables:
            query_parts[0] += f"({', '.join(variables)})"

        query_parts.append(" {")

        # Add query field with arguments
        if argument_list:
            query_parts.append(f"  {query_name}({', '.join(argument_list)}) {{")
        else:
            query_parts.append(f"  {query_name} {{")

        # Get field structure for return type
        base_type = query_type.replace("!", "").replace("[", "").replace("]", "")
        field_structure = self.get_field_structure(base_type, schema_data)

        # Build field selection
        indent = "    "
        query_parts.extend(
            self._build_field_selection(field_structure, indent, schema_data)
        )

        query_parts.append("  }")
        query_parts.append("}")

        return "\n".join(query_parts)

    def _build_field_selection(
        self, field_structure: dict, indent: str, schema_data: dict
    ) -> list[str]:
        """Build field selection for GraphQL query"""
        lines = []
        fields = field_structure.get("fields", {})

        # Handle interface types with implementations
        if field_structure.get("kind") == "INTERFACE":
            implementations = field_structure.get("implementations", [])

            # Add common interface fields first
            for field_name, field_info in fields.items():
                if field_info.get("isDeprecated"):
                    continue

                field_type = field_info.get("type", "")
                base_type = (
                    field_type.replace("!", "").replace("[", "").replace("]", "")
                )

                if base_type in [
                    "String",
                    "Int",
                    "Boolean",
                    "ID",
                    "Float",
                    "DateTime",
                    "Url",
                    "Money",
                ]:
                    lines.append(f"{indent}{field_name}")
                elif "Connection" in base_type:
                    lines.append(f"{indent}{field_name} {{")
                    lines.append(f"{indent}  edges {{")
                    lines.append(f"{indent}    cursor")
                    lines.append(f"{indent}    node {{")
                    lines.append(f"{indent}      # Node fields...")
                    lines.append(f"{indent}    }}")
                    lines.append(f"{indent}  }}")
                    lines.append(f"{indent}  pageInfo {{")
                    lines.append(f"{indent}    hasNextPage")
                    lines.append(f"{indent}    hasPreviousPage")
                    lines.append(f"{indent}  }}")
                    lines.append(f"{indent}}}")

            # Add inline fragments for implementations
            for impl in implementations:
                lines.append(f"{indent}... on {impl} {{")
                impl_structure = self.get_field_structure(impl, schema_data)
                impl_fields = impl_structure.get("fields", {})

                for field_name, field_info in impl_fields.items():
                    if field_info.get("isDeprecated"):
                        continue
                    field_type = field_info.get("type", "")
                    base_type = (
                        field_type.replace("!", "").replace("[", "").replace("]", "")
                    )

                    if base_type in [
                        "String",
                        "Int",
                        "Boolean",
                        "ID",
                        "Float",
                        "DateTime",
                        "Url",
                        "Money",
                    ]:
                        lines.append(f"{indent}  {field_name}")

                lines.append(f"{indent}}}")

        else:
            # Regular object fields
            for field_name, field_info in fields.items():
                if field_info.get("isDeprecated"):
                    continue

                field_type = field_info.get("type", "")
                base_type = (
                    field_type.replace("!", "").replace("[", "").replace("]", "")
                )

                if base_type in [
                    "String",
                    "Int",
                    "Boolean",
                    "ID",
                    "Float",
                    "DateTime",
                    "Url",
                    "Money",
                ]:
                    lines.append(f"{indent}{field_name}")
                elif "Connection" in base_type:
                    # Handle connection pattern
                    lines.append(f"{indent}{field_name}(")

                    # Add pagination arguments if they exist
                    args = field_info.get("arguments", {})
                    arg_lines = []
                    for arg_name, _arg_info in args.items():
                        if arg_name in ["first", "last", "after", "before"]:
                            arg_lines.append(f"{indent}  {arg_name}: ${arg_name}")
                        elif "types" in arg_name.lower():
                            arg_lines.append(f"{indent}  {arg_name}: [ENUM_VALUE]")
                        else:
                            arg_lines.append(f"{indent}  {arg_name}: ${arg_name}")

                    if arg_lines:
                        lines.extend(arg_lines)

                    lines.append(f"{indent}) {{")
                    lines.append(f"{indent}  edges {{")
                    lines.append(f"{indent}    cursor")
                    lines.append(f"{indent}    node {{")
                    lines.append(f"{indent}      # Add specific node fields here")
                    lines.append(f"{indent}    }}")
                    lines.append(f"{indent}  }}")
                    lines.append(f"{indent}  pageInfo {{")
                    lines.append(f"{indent}    hasNextPage")
                    lines.append(f"{indent}    hasPreviousPage")
                    lines.append(f"{indent}  }}")
                    lines.append(f"{indent}}}")
                elif field_info.get("nestedFields"):
                    lines.append(f"{indent}{field_name} {{")
                    nested_lines = self._build_field_selection(
                        field_info["nestedFields"], indent + "  ", schema_data
                    )
                    lines.extend(nested_lines[:5])  # Limit nested depth
                    lines.append(f"{indent}}}")
                else:
                    lines.append(f"{indent}{field_name}")

        return lines

    def analyze_version_differences(self):
        """Compare schema versions to find differences"""
        if len(self.schemas) < 2:
            return

        versions = sorted(self.schemas.keys())
        differences = {}

        for i in range(len(versions)):
            for j in range(i + 1, len(versions)):
                v1, v2 = versions[i], versions[j]

                # Compare types
                v1_types = {
                    t["name"]: t
                    for t in self.schemas[v1]["data"]["__schema"]["types"]
                    if t.get("name")
                }
                v2_types = {
                    t["name"]: t
                    for t in self.schemas[v2]["data"]["__schema"]["types"]
                    if t.get("name")
                }

                added = set(v2_types.keys()) - set(v1_types.keys())
                removed = set(v1_types.keys()) - set(v2_types.keys())

                differences[f"{v1}_to_{v2}"] = {
                    "added_types": list(added),
                    "removed_types": list(removed),
                }

        self.version_differences = differences

    def generate_complete_documentation(self):
        """Generate complete documentation for all operations"""
        if not self.schemas:
            return "No schemas loaded"

        # Use the most recent schema (unstable)
        latest_schema = self.schemas.get("unstable") or list(self.schemas.values())[-1]

        doc_lines = []
        doc_lines.append("# Shopify Partners API - Complete GraphQL Documentation")
        doc_lines.append("=" * 60)
        doc_lines.append("")

        # Get query and mutation root types
        schema_info = latest_schema["data"]["__schema"]
        query_type_name = schema_info["queryType"]["name"]
        mutation_type_name = schema_info.get("mutationType", {}).get("name", "")

        # Find query and mutation type definitions
        query_type = None
        mutation_type = None

        for type_info in schema_info["types"]:
            if type_info["name"] == query_type_name:
                query_type = type_info
            elif type_info["name"] == mutation_type_name:
                mutation_type = type_info

        # Document queries
        if query_type:
            doc_lines.append("## QUERIES")
            doc_lines.append("=" * 20)
            doc_lines.append("")

            for field in query_type.get("fields", []):
                query_name = field["name"]
                doc_lines.append(f"### {query_name}")
                doc_lines.append("-" * 40)

                if field.get("description"):
                    doc_lines.append(f"**Description:** {field['description']}")

                if field.get("isDeprecated"):
                    doc_lines.append(
                        f"**DEPRECATED:** {field.get('deprecationReason', 'No reason provided')}"
                    )

                doc_lines.append("")

                # Build complete query example
                query_example = self.build_complete_query_example(
                    query_name, field, latest_schema
                )
                doc_lines.append("**Complete Query Example:**")
                doc_lines.append("```graphql")
                doc_lines.append(query_example)
                doc_lines.append("```")
                doc_lines.append("")

                # Document variables
                args = field.get("args", [])
                if args:
                    doc_lines.append("**Variables:**")
                    for arg in args:
                        arg_name = arg["name"]
                        arg_type = self.analyze_type(arg["type"])
                        arg_desc = arg.get("description", "No description")
                        default_val = arg.get("defaultValue")

                        doc_lines.append(f"- `${arg_name}`: {arg_type}")
                        doc_lines.append(f"  - {arg_desc}")
                        if default_val:
                            doc_lines.append(f"  - Default: {default_val}")

                    doc_lines.append("")

                # Document return type structure
                return_type = self.analyze_type(field["type"])
                base_return_type = (
                    return_type.replace("!", "").replace("[", "").replace("]", "")
                )

                field_structure = self.get_field_structure(
                    base_return_type, latest_schema
                )
                doc_lines.append("**Return Type Structure:**")
                doc_lines.append(f"Type: {return_type}")

                if field_structure.get("description"):
                    doc_lines.append(f"Description: {field_structure['description']}")

                # Handle interface implementations
                if field_structure.get("kind") == "INTERFACE":
                    implementations = field_structure.get("implementations", [])
                    if implementations:
                        doc_lines.append("**Interface Implementations:**")
                        for impl in implementations:
                            doc_lines.append(f"- {impl}")

                doc_lines.append("")
                doc_lines.append("-" * 60)
                doc_lines.append("")

        # Document mutations
        if mutation_type:
            doc_lines.append("## MUTATIONS")
            doc_lines.append("=" * 20)
            doc_lines.append("")

            for field in mutation_type.get("fields", []):
                mutation_name = field["name"]
                doc_lines.append(f"### {mutation_name}")
                doc_lines.append("-" * 40)

                if field.get("description"):
                    doc_lines.append(f"**Description:** {field['description']}")

                doc_lines.append("")

                # Build mutation example
                mutation_example = self.build_complete_query_example(
                    mutation_name, field, latest_schema
                )
                # Convert to mutation syntax
                mutation_example = mutation_example.replace("query", "mutation")

                doc_lines.append("**Complete Mutation Example:**")
                doc_lines.append("```graphql")
                doc_lines.append(mutation_example)
                doc_lines.append("```")
                doc_lines.append("")

                doc_lines.append("-" * 60)
                doc_lines.append("")

        # Add interface documentation
        doc_lines.append("## INTERFACE IMPLEMENTATIONS")
        doc_lines.append("=" * 30)
        doc_lines.append("")

        interface_impls = self.analyze_interface_implementations(latest_schema)
        for interface_name, implementations in interface_impls.items():
            if implementations:
                doc_lines.append(f"### {interface_name}")
                doc_lines.append("Implementations:")
                for impl in implementations:
                    doc_lines.append(f"- {impl}")

                doc_lines.append("")

        # Add version differences
        if self.version_differences:
            doc_lines.append("## VERSION DIFFERENCES")
            doc_lines.append("=" * 25)
            doc_lines.append("")

            for comparison, diff in self.version_differences.items():
                doc_lines.append(f"### {comparison}")
                if diff["added_types"]:
                    doc_lines.append("Added types:")
                    for type_name in diff["added_types"]:
                        doc_lines.append(f"- {type_name}")
                if diff["removed_types"]:
                    doc_lines.append("Removed types:")
                    for type_name in diff["removed_types"]:
                        doc_lines.append(f"- {type_name}")
                doc_lines.append("")

        return "\n".join(doc_lines)


def main():
    analyzer = GraphQLSchemaAnalyzer()

    print("Loading all schema versions...")
    analyzer.load_all_schemas()

    print("Analyzing version differences...")
    analyzer.analyze_version_differences()

    print("Generating complete documentation...")
    documentation = analyzer.generate_complete_documentation()

    # Write to file
    output_file = "../analysis/complete_field_structures.txt"
    with Path(output_file).open("w", encoding="utf-8") as f:
        f.write(documentation)

    print(f"Complete documentation written to {output_file}")

    # Also create a summary
    summary_lines = []
    summary_lines.append("SCHEMA ANALYSIS SUMMARY")
    summary_lines.append("=" * 30)

    for version, schema in analyzer.schemas.items():
        schema_info = schema["data"]["__schema"]
        types = schema_info["types"]

        query_type = schema_info.get("queryType", {}).get("name", "Unknown")
        mutation_type = schema_info.get("mutationType", {}).get("name", "Unknown")

        # Count queries and mutations
        query_count = 0
        mutation_count = 0

        for type_info in types:
            if type_info["name"] == query_type:
                query_count = len(type_info.get("fields", []))
            elif type_info["name"] == mutation_type:
                mutation_count = len(type_info.get("fields", []))

        summary_lines.append(f"Version {version}:")
        summary_lines.append(f"  Total Types: {len(types)}")
        summary_lines.append(f"  Queries: {query_count}")
        summary_lines.append(f"  Mutations: {mutation_count}")
        summary_lines.append("")

    summary_file = "../analysis/schema_summary.txt"
    with Path(summary_file).open("w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))

    print(f"Schema summary written to {summary_file}")


if __name__ == "__main__":
    main()
