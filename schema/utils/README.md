# Schema Analysis Utils

This directory contains Python utilities for analyzing GraphQL schema files and generating comprehensive documentation for the Shopify Partners API.

## Files

### Python Scripts

- **`analyze_schema.py`** - Original schema analysis script that generates basic schema analysis report
- **`analyze_complete_schema.py`** - Main schema analyzer that extracts types, queries, mutations, and generates comprehensive documentation
- **`build_detailed_queries.py`** - Builds detailed query examples with complete field structures and interface implementations
- **`compare_schema_versions.py`** - Compares different schema versions to identify changes and evolution

### Generated Output (in `../analysis/` directory)

- **`schema_analysis.txt`** - Basic schema analysis report (from analyze_schema.py)
- **`complete_field_structures.txt`** - Complete documentation with all types and fields
- **`detailed_query_examples.md`** - Markdown file with detailed query/mutation examples
- **`version_comparison.md`** - Version comparison report showing changes between schema versions
- **`schema_summary.txt`** - Summary statistics for each schema version
- **`evolution_summary.txt`** - Brief evolution summary across versions

## Usage

Run the scripts from within the `schema/utils/` directory:

```bash
# Change to the utils directory
cd schema/utils

# Generate basic schema analysis report
python analyze_schema.py

# Analyze complete schema structure
python analyze_complete_schema.py

# Build detailed query examples with interface implementations
python build_detailed_queries.py

# Compare schema versions to identify changes
python compare_schema_versions.py
```

## Script Details

### analyze_schema.py

**Purpose:** Basic GraphQL schema analysis and report generation

**Features:**
- Analyzes the unstable version schema structure
- Extracts queries, mutations, and type information
- Identifies connection patterns and enum types
- Generates a comprehensive text report with detailed field information
- Provides argument descriptions and return type analysis

**Output:** `../analysis/schema_analysis.txt`

### analyze_complete_schema.py

**Purpose:** Comprehensive analysis of GraphQL schema with interface implementations

**Features:**
- Loads all schema versions (2024-10, 2025-01, 2025-04, 2025-07, unstable)
- Extracts complete type definitions including interfaces and implementations
- Analyzes queries and mutations with full argument and return type information
- Generates detailed documentation with field descriptions
- Creates summary statistics

**Output:** `../analysis/complete_field_structures.txt`, `../analysis/schema_summary.txt`

### build_detailed_queries.py

**Purpose:** Generate complete GraphQL query and mutation examples

**Features:**
- Builds detailed examples for all 9 queries and 3 mutations
- Includes proper interface fragments (e.g., `... on AppOneTimeSale`)
- Shows complete field structures with nested objects
- Handles connection patterns with pagination
- Provides realistic variable examples

**Output:** `../analysis/detailed_query_examples.md`

### compare_schema_versions.py

**Purpose:** Track schema evolution across versions

**Features:**
- Compares adjacent schema versions to identify changes
- Tracks added/removed types, queries, and mutations
- Identifies modified types with added/removed fields
- Shows schema evolution timeline

**Output:** `../analysis/version_comparison.md`, `../analysis/evolution_summary.txt`

## Schema Structure

The scripts expect the following directory structure:

```
schema/
├── utils/                  # Python analysis scripts
├── analysis/              # Generated analysis files
└── versions/              # Schema version data
    ├── 2024-10/
    │   └── introspection.json
    ├── 2025-01/
    │   └── introspection.json
    ├── 2025-04/
    │   └── introspection.json
    ├── 2025-07/
    │   └── introspection.json
    └── unstable/
        └── introspection.json
```

## Requirements

- Python 3.6+
- Standard library modules: `json`, `os`, `typing`, `collections`

## Integration

These utilities were used to generate the comprehensive documentation in `docs/shopify/queries.md`, which includes:

- Complete field structures for all queries and mutations
- Interface implementations with proper GraphQL fragments
- Version-specific features and deprecations
- Realistic examples with proper variable types
- Pagination patterns and enum values

## Version History

- **2024-10 to 2025-07:** Stable schema with 8 queries and 1 mutation
- **unstable:** Added eventsink functionality (1 new query, 2 new mutations) and enhanced transaction types with processing/regulatory fees