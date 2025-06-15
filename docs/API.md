# DevStandards MCP API Documentation

This document provides detailed information about the MCP tools available in the DevStandards server.

## Overview

The DevStandards MCP server exposes four tools through the Model Context Protocol (MCP) that allow AI assistants to query development standards, best practices, and coding guidelines.

## Available Tools

### 1. `get_standards`

Retrieve coding standards with optional filters.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `category` | string | No | null | Filter by category (e.g., 'drupal_security', 'drupal_performance') |
| `subcategory` | string | No | null | Filter by subcategory (e.g., 'sql_injection', 'xss') |
| `severity` | string | No | null | Filter by severity level. Valid values: 'critical', 'high', 'medium', 'low', 'info' |
| `limit` | integer | No | 50 | Maximum number of results to return (1-100) |

#### Response

```json
{
  "status": "success",
  "data": {
    "standards": [
      {
        "id": "DS001",
        "category": "drupal_security",
        "subcategory": "sql_injection",
        "title": "Use Database API for Queries",
        "description": "Never concatenate user input into SQL queries",
        "severity": "critical",
        "examples": {
          "good": "$query = $connection->select('users', 'u')->condition('name', $name);",
          "bad": "db_query('SELECT * FROM users WHERE name = ' . $_GET['name']);"
        },
        "references": [
          "https://www.drupal.org/docs/security/sql-injection"
        ],
        "tags": ["security", "database", "sql"],
        "rationale": "SQL injection can lead to data theft, data loss, and complete system compromise",
        "fix_guidance": "Use Drupal's Database API with placeholders or the query builder"
      }
    ],
    "metadata": {
      "total": 50,
      "version": "1.0.0",
      "plugins": [
        {
          "name": "drupal",
          "version": "1.0.0",
          "description": "Drupal security, coding standards, and best practices"
        }
      ]
    }
  }
}
```

#### Example Usage

```json
// Get all critical security standards
{
  "name": "get_standards",
  "arguments": {
    "category": "drupal_security",
    "severity": "critical",
    "limit": 10
  }
}
```

### 2. `search_standards`

Search standards using full-text search with optional filters.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search text to find in standards |
| `categories` | array[string] | No | null | Filter results to specific categories |
| `tags` | array[string] | No | null | Filter results by tags |
| `limit` | integer | No | 50 | Maximum number of results (1-100) |

#### Response

```json
{
  "status": "success",
  "data": {
    "query": "injection",
    "results": [
      {
        "id": "DS001",
        "category": "drupal_security",
        "subcategory": "sql_injection",
        "title": "Use Database API for Queries",
        "description": "Never concatenate user input into SQL queries",
        "severity": "critical",
        "examples": {...},
        "references": [...],
        "tags": ["security", "database", "sql"],
        "rationale": "...",
        "fix_guidance": "..."
      }
    ],
    "metadata": {
      "count": 7,
      "categories_searched": ["drupal_security"],
      "tags_searched": "all"
    }
  }
}
```

#### Example Usage

```json
// Search for injection-related standards in security category
{
  "name": "search_standards",
  "arguments": {
    "query": "injection",
    "categories": ["drupal_security"],
    "limit": 20
  }
}
```

### 3. `get_categories`

List all available categories with descriptions and standard counts.

#### Parameters

This tool takes no parameters.

#### Response

```json
{
  "status": "success",
  "data": {
    "categories": [
      {
        "name": "drupal_security",
        "description": "Security best practices for Drupal",
        "plugins": ["drupal"],
        "count": 80
      },
      {
        "name": "drupal_performance",
        "description": "Performance optimization guidelines",
        "plugins": ["drupal"],
        "count": 11
      }
    ],
    "metadata": {
      "total_categories": 22,
      "total_standards": 235
    }
  }
}
```

#### Example Usage

```json
{
  "name": "get_categories",
  "arguments": {}
}
```

### 4. `get_standard_by_id`

Retrieve detailed information about a specific standard.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `standard_id` | string | Yes | The unique identifier of the standard (e.g., 'DS001') |

#### Response

```json
{
  "status": "success",
  "data": {
    "standard": {
      "id": "DS001",
      "category": "drupal_security",
      "subcategory": "sql_injection",
      "title": "Use Database API for Queries",
      "description": "Never concatenate user input into SQL queries",
      "severity": "critical",
      "examples": {
        "good": "$query = $connection->select('users', 'u')->condition('name', $name);",
        "bad": "db_query('SELECT * FROM users WHERE name = ' . $_GET['name']);"
      },
      "references": [
        "https://www.drupal.org/docs/security/sql-injection",
        "https://owasp.org/www-community/attacks/SQL_Injection"
      ],
      "tags": ["security", "database", "sql"],
      "rationale": "SQL injection can lead to data theft, data loss, and complete system compromise",
      "fix_guidance": "Use Drupal's Database API with placeholders or the query builder",
      "created_at": null,
      "updated_at": null
    }
  }
}
```

#### Example Usage

```json
{
  "name": "get_standard_by_id",
  "arguments": {
    "standard_id": "DS001"
  }
}
```

## Error Responses

All tools return error responses in this format:

```json
{
  "status": "error",
  "error": "Error message describing what went wrong"
}
```

Common errors:
- `"Standard 'XYZ' not found"` - When requesting a non-existent standard ID
- `"Invalid severity level"` - When using an invalid severity filter
- `"Query parameter is required"` - When search_standards is called without a query

## Data Model

### Standard Object

Each standard contains:

- `id` (string): Unique identifier
- `category` (string): Main category (e.g., 'drupal_security')
- `subcategory` (string): Subcategory (e.g., 'sql_injection')
- `title` (string): Brief title of the standard
- `description` (string): Detailed description
- `severity` (string): One of: 'critical', 'high', 'medium', 'low', 'info'
- `examples` (object): Good and bad code examples
- `references` (array): URLs to relevant documentation
- `tags` (array): Searchable tags
- `rationale` (string): Why this standard is important
- `fix_guidance` (string): How to implement or fix the issue
- `created_at` (string|null): Creation timestamp
- `updated_at` (string|null): Last update timestamp

### Severity Levels

- **critical**: Must be fixed immediately, severe security or stability impact
- **high**: Should be fixed soon, significant impact on security or functionality
- **medium**: Should be addressed, moderate impact on quality or maintainability
- **low**: Nice to fix, minor impact on code quality
- **info**: Informational, best practice suggestion

## Usage Examples

### Find Critical Security Issues

```python
# AI Assistant query
"Show me all critical security standards for Drupal"

# MCP tool call
{
  "name": "get_standards",
  "arguments": {
    "category": "drupal_security",
    "severity": "critical"
  }
}
```

### Search for Specific Topics

```python
# AI Assistant query
"Find standards about caching and performance optimization"

# MCP tool call
{
  "name": "search_standards",
  "arguments": {
    "query": "caching",
    "categories": ["drupal_performance"]
  }
}
```

### Explore Available Standards

```python
# AI Assistant query
"What types of coding standards are available?"

# MCP tool call
{
  "name": "get_categories",
  "arguments": {}
}
```

### Get Detailed Information

```python
# AI Assistant query
"Tell me more about standard DS001"

# MCP tool call
{
  "name": "get_standard_by_id",
  "arguments": {
    "standard_id": "DS001"
  }
}
```

## Notes

1. **Data Loading**: Standards are loaded from CSV files when the first query is made
2. **Caching**: Plugin data is cached in memory for performance
3. **Dynamic Loading**: All CSV files in plugin directories are automatically loaded
4. **Extensibility**: New plugins can be added by implementing the StandardsPlugin interface