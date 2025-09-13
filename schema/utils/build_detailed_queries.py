#!/usr/bin/env python3
"""
Build detailed GraphQL query examples with complete field structures
including proper interface implementations like Transaction -> AppOneTimeSale
"""

import json
import os
from typing import Dict, List, Any, Set

class DetailedQueryBuilder:
    def __init__(self):
        self.schema = None
        self.type_registry = {}
        self.load_latest_schema()

    def load_latest_schema(self):
        """Load the latest (unstable) schema"""
        schema_file = "../versions/unstable/introspection.json"
        if os.path.exists(schema_file):
            with open(schema_file, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
                self.build_type_registry()

    def build_type_registry(self):
        """Build a registry of all types for easy lookup"""
        for type_info in self.schema['data']['__schema']['types']:
            name = type_info.get('name')
            if name:
                self.type_registry[name] = type_info

    def get_type_info(self, type_name: str) -> Dict:
        """Get type information from registry"""
        return self.type_registry.get(type_name, {})

    def resolve_type_string(self, type_obj: Dict) -> str:
        """Convert GraphQL type object to string representation"""
        if not type_obj:
            return "Unknown"

        kind = type_obj.get('kind', '')
        name = type_obj.get('name', '')

        if kind == 'NON_NULL':
            return f"{self.resolve_type_string(type_obj.get('ofType', {}))}!"
        elif kind == 'LIST':
            return f"[{self.resolve_type_string(type_obj.get('ofType', {}))}]"
        else:
            return name or kind

    def get_scalar_fields(self, type_name: str, visited: Set[str] = None) -> List[str]:
        """Get all scalar fields for a type"""
        if visited is None:
            visited = set()

        if type_name in visited:
            return []

        visited.add(type_name)

        type_info = self.get_type_info(type_name)
        if not type_info:
            return []

        scalar_fields = []
        fields = type_info.get('fields', [])

        for field in fields:
            if field.get('isDeprecated'):
                continue

            field_name = field['name']
            field_type = self.resolve_type_string(field['type'])
            base_type = field_type.replace('!', '').replace('[', '').replace(']', '')

            # Check if it's a scalar type
            if base_type in ['String', 'Int', 'Boolean', 'ID', 'Float', 'DateTime', 'Url', 'Money']:
                scalar_fields.append(field_name)

        return scalar_fields

    def build_interface_fragments(self, interface_name: str) -> List[str]:
        """Build inline fragments for interface implementations"""
        interface_info = self.get_type_info(interface_name)
        if not interface_info or interface_info.get('kind') != 'INTERFACE':
            return []

        fragments = []

        # Find all implementations
        implementations = []
        for type_name, type_info in self.type_registry.items():
            if type_info.get('kind') == 'OBJECT':
                interfaces = type_info.get('interfaces', [])
                for iface in interfaces:
                    if iface.get('name') == interface_name:
                        implementations.append(type_name)
                        break

        # Build fragments for each implementation
        for impl_name in implementations:
            impl_info = self.get_type_info(impl_name)
            if not impl_info:
                continue

            fragment_lines = [f"    ... on {impl_name} {{"]

            # Add scalar fields specific to this implementation
            scalar_fields = self.get_scalar_fields(impl_name)
            for field in scalar_fields:
                fragment_lines.append(f"      {field}")

            # Add some common relationship fields
            impl_fields = impl_info.get('fields', [])
            for field in impl_fields[:10]:  # Limit to first 10 fields
                if field.get('isDeprecated'):
                    continue

                field_name = field['name']
                field_type = self.resolve_type_string(field['type'])
                base_type = field_type.replace('!', '').replace('[', '').replace(']', '')

                # Skip if already added as scalar
                if field_name in scalar_fields:
                    continue

                # Add object fields with simple structure
                if base_type in self.type_registry:
                    target_type = self.get_type_info(base_type)
                    if target_type.get('kind') == 'OBJECT' and not 'Connection' in base_type:
                        fragment_lines.append(f"      {field_name} {{")

                        # Add a few scalar fields from the target type
                        target_scalars = self.get_scalar_fields(base_type)
                        for scalar in target_scalars[:3]:  # Limit to 3 fields
                            fragment_lines.append(f"        {scalar}")

                        fragment_lines.append(f"      }}")

            fragment_lines.append("    }")
            fragments.extend(fragment_lines)

        return fragments

    def build_connection_structure(self, field_name: str, field_info: Dict, indent: str = "    ") -> List[str]:
        """Build connection field structure with pagination"""
        lines = []
        args = field_info.get('args', [])

        # Start connection field with arguments
        arg_parts = []
        for arg in args:
            arg_name = arg['name']
            arg_type = self.resolve_type_string(arg['type'])

            # Use realistic argument examples
            if 'first' in arg_name:
                arg_parts.append(f"{indent}  {arg_name}: 10")
            elif 'types' in arg_name or 'Type' in arg_type:
                # Find enum values if available
                base_arg_type = arg_type.replace('!', '').replace('[', '').replace(']', '')
                enum_info = self.get_type_info(base_arg_type)
                if enum_info and enum_info.get('kind') == 'ENUM':
                    enum_values = enum_info.get('enumValues', [])
                    if enum_values:
                        example_value = enum_values[0]['name']
                        if '[' in arg_type:
                            arg_parts.append(f"{indent}  {arg_name}: [{example_value}]")
                        else:
                            arg_parts.append(f"{indent}  {arg_name}: {example_value}")
            elif arg_name in ['shopId', 'appId', 'chargeId']:
                gid_type = arg_name.replace('Id', '').title()
                arg_parts.append(f"{indent}  {arg_name}: \"gid://partners/{gid_type}/123\"")
            elif 'Id' in arg_name:
                arg_parts.append(f"{indent}  {arg_name}: $id")
            elif 'DateTime' in arg_type:
                arg_parts.append(f"{indent}  {arg_name}: \"2024-01-01T00:00:00Z\"")
            else:
                arg_parts.append(f"{indent}  {arg_name}: ${arg_name}")

        # Build the connection structure
        if arg_parts:
            lines.append(f"{indent}{field_name}(")
            lines.extend(arg_parts)
            lines.append(f"{indent}) {{")
        else:
            lines.append(f"{indent}{field_name} {{")

        lines.append(f"{indent}  edges {{")
        lines.append(f"{indent}    cursor")
        lines.append(f"{indent}    node {{")

        # Determine node type
        field_type = self.resolve_type_string(field_info['type'])
        if 'Connection' in field_type:
            # Extract the base type (e.g., AppEventConnection -> AppEvent)
            node_type = field_type.replace('Connection', '').replace('!', '')
            node_info = self.get_type_info(node_type)

            if node_info:
                if node_info.get('kind') == 'INTERFACE':
                    # Add common interface fields
                    interface_fields = self.get_scalar_fields(node_type)
                    for field in interface_fields[:5]:  # Limit fields
                        lines.append(f"{indent}      {field}")

                    # Add interface fragments
                    fragments = self.build_interface_fragments(node_type)
                    if fragments:
                        lines.extend([f"    {line}" for line in fragments])
                else:
                    # Regular object type
                    scalar_fields = self.get_scalar_fields(node_type)
                    for field in scalar_fields[:8]:  # Limit to 8 fields
                        lines.append(f"{indent}      {field}")

        lines.append(f"{indent}    }}")
        lines.append(f"{indent}  }}")
        lines.append(f"{indent}  pageInfo {{")
        lines.append(f"{indent}    hasNextPage")
        lines.append(f"{indent}    hasPreviousPage")
        lines.append(f"{indent}    startCursor")
        lines.append(f"{indent}    endCursor")
        lines.append(f"{indent}  }}")
        lines.append(f"{indent}}}")

        return lines

    def build_detailed_query(self, query_name: str) -> Dict[str, Any]:
        """Build a detailed query example with complete field structure"""
        # Find query type
        schema_info = self.schema['data']['__schema']
        query_type_name = schema_info['queryType']['name']
        query_type = self.get_type_info(query_type_name)

        if not query_type:
            return {}

        # Find the specific query field
        query_field = None
        for field in query_type.get('fields', []):
            if field['name'] == query_name:
                query_field = field
                break

        if not query_field:
            return {}

        # Build query structure
        query_lines = []
        variables = []

        # Process arguments
        args = query_field.get('args', [])
        arg_calls = []

        for arg in args:
            arg_name = arg['name']
            arg_type = self.resolve_type_string(arg['type'])
            arg_desc = arg.get('description', '')

            variables.append(f"${arg_name}: {arg_type}")
            arg_calls.append(f"{arg_name}: ${arg_name}")

        # Query signature
        if variables:
            query_lines.append(f"query {query_name.title()}Query({', '.join(variables)}) {{")
        else:
            query_lines.append(f"query {query_name.title()}Query {{")

        # Query field call
        if arg_calls:
            query_lines.append(f"  {query_name}({', '.join(arg_calls)}) {{")
        else:
            query_lines.append(f"  {query_name} {{")

        # Get return type and build field structure
        return_type = self.resolve_type_string(query_field['type'])
        base_return_type = return_type.replace('!', '').replace('[', '').replace(']', '')

        return_type_info = self.get_type_info(base_return_type)

        if return_type_info:
            if return_type_info.get('kind') == 'INTERFACE':
                # Handle interface return types (like Transaction)
                scalar_fields = self.get_scalar_fields(base_return_type)
                for field in scalar_fields:
                    query_lines.append(f"    {field}")

                # Add interface fragments
                fragments = self.build_interface_fragments(base_return_type)
                for line in fragments:
                    query_lines.append(line)

            elif 'Connection' in base_return_type:
                # Handle connection types
                connection_lines = self.build_connection_structure(query_name, query_field, "")
                # Remove the field name line since we already have it
                query_lines.extend(connection_lines[1:])  # Skip first line

            else:
                # Handle regular object types
                fields = return_type_info.get('fields', [])

                for field in fields:
                    if field.get('isDeprecated'):
                        continue

                    field_name = field['name']
                    field_type = self.resolve_type_string(field['type'])
                    base_field_type = field_type.replace('!', '').replace('[', '').replace(']', '')

                    if base_field_type in ['String', 'Int', 'Boolean', 'ID', 'Float', 'DateTime', 'Url', 'Money']:
                        query_lines.append(f"    {field_name}")
                    elif 'Connection' in base_field_type:
                        # Handle nested connections
                        connection_lines = self.build_connection_structure(field_name, field, "    ")
                        query_lines.extend(connection_lines)
                    elif base_field_type in self.type_registry:
                        # Handle nested objects
                        nested_type = self.get_type_info(base_field_type)
                        if nested_type and nested_type.get('kind') == 'OBJECT':
                            query_lines.append(f"    {field_name} {{")

                            # Add scalar fields from nested object
                            nested_scalars = self.get_scalar_fields(base_field_type)
                            for scalar in nested_scalars[:5]:  # Limit nested fields
                                query_lines.append(f"      {scalar}")

                            query_lines.append(f"    }}")

        query_lines.append("  }")
        query_lines.append("}")

        # Build variable documentation
        var_docs = []
        for arg in args:
            arg_name = arg['name']
            arg_type = self.resolve_type_string(arg['type'])
            arg_desc = arg.get('description', 'No description provided')
            default_val = arg.get('defaultValue')

            var_doc = {
                "name": f"${arg_name}",
                "type": arg_type,
                "description": arg_desc,
                "required": "!" in arg_type,
                "default": default_val
            }
            var_docs.append(var_doc)

        return {
            "name": query_name,
            "description": query_field.get('description', ''),
            "deprecated": query_field.get('isDeprecated', False),
            "deprecation_reason": query_field.get('deprecationReason'),
            "query": "\n".join(query_lines),
            "variables": var_docs,
            "return_type": return_type,
            "return_type_info": return_type_info
        }

    def build_detailed_mutation(self, mutation_name: str) -> Dict[str, Any]:
        """Build a detailed mutation example"""
        # Find mutation type
        schema_info = self.schema['data']['__schema']
        mutation_type_name = schema_info.get('mutationType', {}).get('name', '')
        if not mutation_type_name:
            return {}

        mutation_type = self.get_type_info(mutation_type_name)
        if not mutation_type:
            return {}

        # Find the specific mutation field
        mutation_field = None
        for field in mutation_type.get('fields', []):
            if field['name'] == mutation_name:
                mutation_field = field
                break

        if not mutation_field:
            return {}

        # Build mutation structure
        mutation_lines = []
        variables = []

        # Process arguments
        args = mutation_field.get('args', [])
        arg_calls = []

        for arg in args:
            arg_name = arg['name']
            arg_type = self.resolve_type_string(arg['type'])

            variables.append(f"${arg_name}: {arg_type}")
            arg_calls.append(f"{arg_name}: ${arg_name}")

        # Mutation signature
        if variables:
            mutation_lines.append(f"mutation {mutation_name.title()}Mutation({', '.join(variables)}) {{")
        else:
            mutation_lines.append(f"mutation {mutation_name.title()}Mutation {{")

        # Mutation field call
        if arg_calls:
            mutation_lines.append(f"  {mutation_name}({', '.join(arg_calls)}) {{")
        else:
            mutation_lines.append(f"  {mutation_name} {{")

        # Get return type and build field structure
        return_type = self.resolve_type_string(mutation_field['type'])
        base_return_type = return_type.replace('!', '').replace('[', '').replace(']', '')

        return_type_info = self.get_type_info(base_return_type)

        if return_type_info:
            fields = return_type_info.get('fields', [])

            for field in fields:
                field_name = field['name']
                field_type = self.resolve_type_string(field['type'])
                base_field_type = field_type.replace('!', '').replace('[', '').replace(']', '')

                if base_field_type in ['String', 'Int', 'Boolean', 'ID', 'Float', 'DateTime', 'Url', 'Money']:
                    mutation_lines.append(f"    {field_name}")
                elif base_field_type in self.type_registry:
                    # Handle nested objects
                    nested_type = self.get_type_info(base_field_type)
                    if nested_type and nested_type.get('kind') == 'OBJECT':
                        mutation_lines.append(f"    {field_name} {{")

                        # Add scalar fields from nested object
                        nested_scalars = self.get_scalar_fields(base_field_type)
                        for scalar in nested_scalars[:8]:  # More fields for mutations
                            mutation_lines.append(f"      {scalar}")

                        mutation_lines.append(f"    }}")

        mutation_lines.append("  }")
        mutation_lines.append("}")

        # Build variable documentation
        var_docs = []
        for arg in args:
            arg_name = arg['name']
            arg_type = self.resolve_type_string(arg['type'])
            arg_desc = arg.get('description', 'No description provided')
            default_val = arg.get('defaultValue')

            var_doc = {
                "name": f"${arg_name}",
                "type": arg_type,
                "description": arg_desc,
                "required": "!" in arg_type,
                "default": default_val
            }
            var_docs.append(var_doc)

        return {
            "name": mutation_name,
            "description": mutation_field.get('description', ''),
            "deprecated": mutation_field.get('isDeprecated', False),
            "deprecation_reason": mutation_field.get('deprecationReason'),
            "mutation": "\n".join(mutation_lines),
            "variables": var_docs,
            "return_type": return_type,
            "return_type_info": return_type_info
        }

    def generate_all_examples(self):
        """Generate detailed examples for all queries and mutations"""
        # Get all queries
        schema_info = self.schema['data']['__schema']
        query_type_name = schema_info['queryType']['name']
        query_type = self.get_type_info(query_type_name)

        queries = []
        if query_type:
            for field in query_type.get('fields', []):
                query_example = self.build_detailed_query(field['name'])
                if query_example:
                    queries.append(query_example)

        # Get all mutations
        mutations = []
        mutation_type_name = schema_info.get('mutationType', {}).get('name', '')
        if mutation_type_name:
            mutation_type = self.get_type_info(mutation_type_name)
            if mutation_type:
                for field in mutation_type.get('fields', []):
                    mutation_example = self.build_detailed_mutation(field['name'])
                    if mutation_example:
                        mutations.append(mutation_example)

        return {
            "queries": queries,
            "mutations": mutations
        }

def main():
    builder = DetailedQueryBuilder()

    if not builder.schema:
        print("Failed to load schema!")
        return

    print("Building detailed query and mutation examples...")
    examples = builder.generate_all_examples()

    # Generate markdown documentation
    md_lines = []
    md_lines.append("# Shopify Partners API - Complete Query and Mutation Examples")
    md_lines.append("")
    md_lines.append("Generated from the latest GraphQL schema with complete field structures and interface implementations.")
    md_lines.append("")

    # Document queries
    md_lines.append("## QUERIES")
    md_lines.append("=" * 50)
    md_lines.append("")

    for query in examples["queries"]:
        md_lines.append(f"### {query['name']}")
        md_lines.append("")

        if query.get('description'):
            md_lines.append(f"**Description:** {query['description']}")
            md_lines.append("")

        if query.get('deprecated'):
            md_lines.append(f"**⚠️ DEPRECATED:** {query.get('deprecation_reason', 'This field is deprecated')}")
            md_lines.append("")

        md_lines.append("**Complete Query Example:**")
        md_lines.append("```graphql")
        md_lines.append(query['query'])
        md_lines.append("```")
        md_lines.append("")

        if query['variables']:
            md_lines.append("**Variables:**")
            for var in query['variables']:
                md_lines.append(f"- `{var['name']}`: `{var['type']}`")
                md_lines.append(f"  - {var['description']}")
                if var.get('default'):
                    md_lines.append(f"  - Default: `{var['default']}`")
                md_lines.append("")

        md_lines.append("**Return Type:** `" + query['return_type'] + "`")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    # Document mutations
    md_lines.append("## MUTATIONS")
    md_lines.append("=" * 50)
    md_lines.append("")

    for mutation in examples["mutations"]:
        md_lines.append(f"### {mutation['name']}")
        md_lines.append("")

        if mutation.get('description'):
            md_lines.append(f"**Description:** {mutation['description']}")
            md_lines.append("")

        md_lines.append("**Complete Mutation Example:**")
        md_lines.append("```graphql")
        md_lines.append(mutation['mutation'])
        md_lines.append("```")
        md_lines.append("")

        if mutation['variables']:
            md_lines.append("**Variables:**")
            for var in mutation['variables']:
                md_lines.append(f"- `{var['name']}`: `{var['type']}`")
                md_lines.append(f"  - {var['description']}")
                if var.get('default'):
                    md_lines.append(f"  - Default: `{var['default']}`")
                md_lines.append("")

        md_lines.append("**Return Type:** `" + mutation['return_type'] + "`")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    # Write to file
    output_file = "../analysis/detailed_query_examples.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))

    print(f"Detailed examples written to {output_file}")
    print(f"Generated {len(examples['queries'])} queries and {len(examples['mutations'])} mutations")

if __name__ == "__main__":
    main()
