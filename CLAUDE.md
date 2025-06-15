# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that provides AI agents with development standards and best practices. It uses a plugin architecture to support multiple programming languages/frameworks, currently focused on Drupal standards.

## Architecture

The project uses a modular architecture:
- **MCP Server**: Handles JSON-RPC protocol over stdio
- **Plugin System**: Extensible system for adding new standards (base.py → manager.py → drupal.py)
- **Data Layer**: In-memory storage for fast access (memory_store.py)
- **Dynamic CSV Loading**: All CSV files in `data/{plugin_name}/*.csv` are automatically loaded

Key flow: CSV files → Plugin dynamically loads all → Memory store → MCP tools query → AI assistant receives

## Common Development Commands

```bash
# Run tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_mcp_handlers.py -v

# Format code
black src/ tests/

# Lint code  
flake8 src/ tests/

# Type checking
mypy src/

# Run server for manual testing
./devstandards-server

# Test MCP protocol manually
python test_cursor.py

# Validate MCP server functionality
python test_mcp_validation.py

# Test specific tools directly
python -c "
import asyncio
from src.server import get_standards
asyncio.run(get_standards(category='drupal_security', limit=5))
"
```

## Running the Server

```bash
# Ensure virtual environment exists
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Make executable
chmod +x devstandards-server

# Run server
./devstandards-server
```

## Adding New Standards

1. **To existing plugin**: Add or edit any CSV file in `data/{plugin_name}/*.csv` (all CSV files are loaded automatically)
2. **New plugin**: Create plugin in `src/plugins/`, implement StandardsPlugin interface, add CSV data

### CSV Format
```csv
id,category,subcategory,title,description,severity,examples,references,tags,rationale,fix_guidance
TEST001,drupal_testing,unit_tests,Always Mock External Services,External services should be mocked in unit tests,high,"{""good"": ""$mock = $this->createMock(HttpClient::class);"", ""bad"": ""$client = new HttpClient();""}","[""https://phpunit.de/manual/current/en/test-doubles.html""]",testing|mocking|unit,Calling real external services in tests makes them flaky and slow,Use PHPUnit mocks or test doubles for external dependencies
```

## MCP Tools Available

- `get_standards`: Filter by category, subcategory, severity  
- `search_standards`: Full-text search across all standards
- `get_categories`: List all available categories
- `get_standard_by_id`: Get specific standard details

## Testing MCP Integration

### Quick Test
Use `test_cursor.py` to verify basic functionality:
```bash
python test_cursor.py
# Expected: 4 tools discovered, categories returned successfully
```

### Comprehensive Validation
Use `test_mcp_validation.py` for full testing:
```bash
python test_mcp_validation.py
# Tests: categories, standards loading, search, filtering, CSV discovery
```

### Common Issues
1. **Standards show 0 count initially**: This is normal - data loads on first query
2. **New CSV not loading**: Plugin caches data - restart server or clear `_standards` cache
3. **Category not found**: Add category to plugin's `_categories` dict

## Data Storage

Standards are stored in memory with the following structure: id, category, subcategory, title, description, severity, examples (dict), references (list), tags (list), rationale, fix_guidance. Data is organized by plugin for efficient updates.

## Environment Configuration

Copy `.env.example` to `.env`. Key settings:
- `DATA_DIR`: CSV data directory
- `PLUGINS_ENABLED`: Active plugins list
- `LOG_LEVEL`: Logging verbosity

## Entry Points

- `devstandards-server`: Bash launcher that activates venv
- `server.py`: Python entry point
- `src/server.py`: Main server implementation with MCP handlers