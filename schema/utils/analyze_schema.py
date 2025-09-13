#!/usr/bin/env python3
"""
GraphQL Schema Analysis Tool for Shopify Partners API

This script analyzes the GraphQL introspection JSON file and extracts comprehensive
information about all queries and mutations available in the Shopify Partners API.

Features:
- Extracts all queries and mutations with complete field structures
- Identifies arguments, return types, and nested field definitions
- Detects deprecation notices and enum values
- Identifies GraphQL patterns like connections and pagination
- Generates a detailed analysis report
"""

import json
import os
from typing import Dict, List, Any, Optional
from collections import defaultdict


class GraphQLTypeAnalyzer:
    """Analyzes GraphQL types and resolves complex type structures."""

    def __init__(self, types_by_name: Dict[str, Any]):
        self.types_by_name = types_by_name
        self.connection_types = set()
        self.enum_types = {}
        self._identify_patterns()

    def _identify_patterns(self):
        """Identify common GraphQL patterns like connections."""
        for type_name, type_def in self.types_by_name.items():
            if type_name.endswith('Connection'):
                self.connection_types.add(type_name)
            elif type_def.get('kind') == 'ENUM':
                self.enum_types[type_name] = [
                    enum_val['name'] for enum_val in type_def.get('enumValues', [])
                ]

    def resolve_type(self, type_def: Dict[str, Any], depth: int = 0) -> Dict[str, Any]:
        """Resolve a GraphQL type definition to its complete structure."""
        if depth > 10:  # Prevent infinite recursion
            return {"type": "...", "description": "Max depth reached"}

        kind = type_def.get('kind')
        name = type_def.get('name')
        of_type = type_def.get('ofType')

        if kind == 'NON_NULL':
            resolved = self.resolve_type(of_type, depth + 1)
            resolved['required'] = True
            return resolved

        elif kind == 'LIST':
            resolved = self.resolve_type(of_type, depth + 1)
            return {
                "type": f"[{resolved.get('type', 'Unknown')}]",
                "description": resolved.get('description', ''),
                "list": True,
                "element_type": resolved
            }

        elif kind in ['SCALAR', 'ENUM', 'INPUT_OBJECT']:
            result = {
                "type": name,
                "kind": kind,
                "description": ""
            }
            if name in self.enum_types:
                result['enum_values'] = self.enum_types[name]
            return result

        elif kind == 'OBJECT':
            type_info = self.types_by_name.get(name, {})
            result = {
                "type": name,
                "kind": kind,
                "description": type_info.get('description', ''),
            }

            # Add connection pattern info
            if name in self.connection_types:
                result['is_connection'] = True

            # Add fields for non-recursive types
            if depth < 3:  # Limit field expansion depth
                fields = type_info.get('fields', [])
                if fields:
                    result['fields'] = {}
                    for field in fields[:10]:  # Limit number of fields shown
                        field_type = self.resolve_type(field['type'], depth + 1)
                        result['fields'][field['name']] = {
                            "type": field_type.get('type', 'Unknown'),
                            "description": field.get('description', ''),
                            "deprecated": field.get('isDeprecated', False)
                        }
                        if field.get('isDeprecated'):
                            result['fields'][field['name']]['deprecation_reason'] = field.get('deprecationReason')

            return result

        elif kind == 'INTERFACE':
            return {
                "type": name,
                "kind": kind,
                "description": self.types_by_name.get(name, {}).get('description', '')
            }

        elif kind == 'UNION':
            union_info = self.types_by_name.get(name, {})
            possible_types = [pt['name'] for pt in union_info.get('possibleTypes', [])]
            return {
                "type": name,
                "kind": kind,
                "description": union_info.get('description', ''),
                "possible_types": possible_types
            }

        return {"type": name or "Unknown", "kind": kind}


class GraphQLSchemaAnalyzer:
    """Main analyzer class for GraphQL schema introspection data."""

    def __init__(self, introspection_data: Dict[str, Any]):
        self.schema = introspection_data['data']['__schema']
        self.types = self.schema['types']
        self.types_by_name = {t['name']: t for t in self.types}
        self.type_analyzer = GraphQLTypeAnalyzer(self.types_by_name)

        # Find root types
        self.query_root = self._find_root_type('QueryRoot')
        self.mutation_root = self._find_root_type('MutationRoot')

    def _find_root_type(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Find a root type by name."""
        return self.types_by_name.get(type_name)

    def analyze_field(self, field: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single field (query or mutation)."""
        field_info = {
            'name': field['name'],
            'description': field.get('description', ''),
            'deprecated': field.get('isDeprecated', False),
            'deprecation_reason': field.get('deprecationReason') if field.get('isDeprecated') else None,
            'arguments': [],
            'return_type': {}
        }

        # Analyze arguments
        for arg in field.get('args', []):
            arg_type = self.type_analyzer.resolve_type(arg['type'])
            arg_info = {
                'name': arg['name'],
                'description': arg.get('description', ''),
                'type': arg_type,
                'default_value': arg.get('defaultValue'),
                'required': arg_type.get('required', False)
            }
            field_info['arguments'].append(arg_info)

        # Analyze return type
        field_info['return_type'] = self.type_analyzer.resolve_type(field['type'])

        return field_info

    def analyze_queries(self) -> List[Dict[str, Any]]:
        """Analyze all query fields."""
        if not self.query_root:
            return []

        queries = []
        for field in self.query_root.get('fields', []):
            queries.append(self.analyze_field(field))

        return queries

    def analyze_mutations(self) -> List[Dict[str, Any]]:
        """Analyze all mutation fields."""
        if not self.mutation_root:
            return []

        mutations = []
        for field in self.mutation_root.get('fields', []):
            mutations.append(self.analyze_field(field))

        return mutations

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall schema statistics."""
        stats = {
            'total_types': len(self.types),
            'query_count': len(self.query_root.get('fields', [])) if self.query_root else 0,
            'mutation_count': len(self.mutation_root.get('fields', [])) if self.mutation_root else 0,
            'connection_types': len(self.type_analyzer.connection_types),
            'enum_types': len(self.type_analyzer.enum_types),
        }

        # Count types by kind
        type_counts = defaultdict(int)
        for type_def in self.types:
            type_counts[type_def.get('kind', 'UNKNOWN')] += 1

        stats['types_by_kind'] = dict(type_counts)
        return stats


def format_type_info(type_info: Dict[str, Any], indent: str = "") -> str:
    """Format type information for readable output."""
    result = []
    type_name = type_info.get('type', 'Unknown')
    kind = type_info.get('kind', '')

    if type_info.get('required'):
        type_name += '!'

    if type_info.get('list'):
        result.append(f"{indent}Type: {type_name}")
    else:
        result.append(f"{indent}Type: {type_name}")
        if kind:
            result.append(f"{indent}Kind: {kind}")

    if type_info.get('description'):
        result.append(f"{indent}Description: {type_info['description']}")

    if type_info.get('enum_values'):
        result.append(f"{indent}Enum Values: {', '.join(type_info['enum_values'])}")

    if type_info.get('possible_types'):
        result.append(f"{indent}Possible Types: {', '.join(type_info['possible_types'])}")

    if type_info.get('is_connection'):
        result.append(f"{indent}Pattern: GraphQL Connection (supports pagination)")

    if type_info.get('fields'):
        result.append(f"{indent}Fields:")
        for field_name, field_info in list(type_info['fields'].items())[:5]:  # Show first 5 fields
            result.append(f"{indent}  - {field_name}: {field_info.get('type', 'Unknown')}")
            if field_info.get('description'):
                result.append(f"{indent}    Description: {field_info['description']}")
            if field_info.get('deprecated'):
                result.append(f"{indent}    DEPRECATED: {field_info.get('deprecation_reason', 'No reason given')}")

        if len(type_info['fields']) > 5:
            result.append(f"{indent}  ... and {len(type_info['fields']) - 5} more fields")

    return '\n'.join(result)


def format_field_analysis(field: Dict[str, Any], field_type: str) -> str:
    """Format a single field analysis for output."""
    lines = [
        f"\n{'='*60}",
        f"{field_type.upper()}: {field['name']}",
        f"{'='*60}"
    ]

    if field['description']:
        lines.extend([
            f"Description:",
            f"  {field['description']}"
        ])

    if field['deprecated']:
        lines.extend([
            f"DEPRECATED",
            f"  Reason: {field['deprecation_reason'] or 'No reason provided'}"
        ])

    # Arguments
    if field['arguments']:
        lines.append(f"\nArguments ({len(field['arguments'])}):")
        for arg in field['arguments']:
            lines.append(f"  • {arg['name']}")
            lines.append(f"    Description: {arg['description'] or 'No description'}")
            lines.append(format_type_info(arg['type'], "    "))
            if arg['default_value'] is not None:
                lines.append(f"    Default: {arg['default_value']}")
            if arg['required']:
                lines.append("    Required: Yes")
    else:
        lines.append("\nArguments: None")

    # Return type
    lines.extend([
        f"\nReturn Type:",
        format_type_info(field['return_type'], "  ")
    ])

    return '\n'.join(lines)


def main():
    """Main execution function."""
    # File paths
    schema_file = '../versions/unstable/introspection.json'
    output_file = '../analysis/schema_analysis.txt'

    # Check if schema file exists
    if not os.path.exists(schema_file):
        print(f"Error: Schema file not found at {schema_file}")
        return

    # Load schema data
    print(f"Loading GraphQL schema from {schema_file}...")
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            introspection_data = json.load(f)
    except Exception as e:
        print(f"Error loading schema file: {e}")
        return

    # Create analyzer
    print("Analyzing schema...")
    analyzer = GraphQLSchemaAnalyzer(introspection_data)

    # Perform analysis
    queries = analyzer.analyze_queries()
    mutations = analyzer.analyze_mutations()
    stats = analyzer.get_statistics()

    # Generate report
    print(f"Generating analysis report...")
    report_lines = [
        "SHOPIFY PARTNERS API - GRAPHQL SCHEMA ANALYSIS",
        "=" * 50,
        f"Generated from: {schema_file}",
        f"Analysis Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "SUMMARY STATISTICS",
        "=" * 30,
        f"Total Types: {stats['total_types']}",
        f"Total Queries: {stats['query_count']}",
        f"Total Mutations: {stats['mutation_count']}",
        f"Connection Types: {stats['connection_types']}",
        f"Enum Types: {stats['enum_types']}",
        "",
        "Types by Kind:",
        *[f"  {kind}: {count}" for kind, count in sorted(stats['types_by_kind'].items())],
        "",
        "DETAILED ANALYSIS",
        "=" * 50
    ]

    # Add query analysis
    if queries:
        report_lines.extend([
            f"\nQUERIES ({len(queries)})",
            "=" * 20
        ])
        for query in queries:
            report_lines.append(format_field_analysis(query, "query"))

    # Add mutation analysis
    if mutations:
        report_lines.extend([
            f"\n\nMUTATIONS ({len(mutations)})",
            "=" * 20
        ])
        for mutation in mutations:
            report_lines.append(format_field_analysis(mutation, "mutation"))

    # Connection patterns summary
    if analyzer.type_analyzer.connection_types:
        report_lines.extend([
            f"\n\nCONNECTION PATTERNS",
            "=" * 30,
            "The following types implement GraphQL connection patterns for pagination:",
            *[f"  • {conn_type}" for conn_type in sorted(analyzer.type_analyzer.connection_types)]
        ])

    # Enum types summary
    if analyzer.type_analyzer.enum_types:
        report_lines.extend([
            f"\n\nENUM TYPES",
            "=" * 20,
            "Available enumeration types and their values:"
        ])
        for enum_name, enum_values in sorted(analyzer.type_analyzer.enum_types.items()):
            report_lines.extend([
                f"\n{enum_name}:",
                f"  Values: {', '.join(enum_values)}"
            ])

    # Write report
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"Analysis complete! Report saved to {output_file}")
        print(f"Found {stats['query_count']} queries and {stats['mutation_count']} mutations")

    except Exception as e:
        print(f"Error writing report: {e}")


if __name__ == "__main__":
    main()
