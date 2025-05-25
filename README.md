# DevStandards MCP Server

A Model Context Protocol (MCP) server that provides AI agents with access to development best practices, security guidelines, and coding standards across multiple programming languages and frameworks.

## Features

- **Plugin Architecture**: Extensible system for adding new languages and frameworks
- **Database Backend**: SQLite database for fast querying and caching
- **CSV Data Import**: Easy-to-manage standards data in CSV format
- **31 Coding Standards**: Covering security, accessibility, performance, and best practices
- **MCP Tools**: Four tools for querying standards:
  - `get_standards`: Filter by category, subcategory, and severity
  - `search_standards`: Full-text search across all standards
  - `get_categories`: List all available categories
  - `get_standard_by_id`: Get details for a specific standard

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/devstandards-mcp.git
cd devstandards-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the environment configuration:
```bash
cp .env.example .env
```

## Running the Server

### Standalone Executable

```bash
./devstandards-server
```

### Via Python Module

```bash
source venv/bin/activate
python -m src.server
```

### Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

## Project Structure

```
devstandards-mcp/
├── src/
│   ├── server.py          # MCP server implementation
│   ├── config.py          # Configuration management
│   ├── plugins/           # Plugin system
│   │   ├── base.py        # Base plugin class
│   │   ├── manager.py     # Plugin manager
│   │   └── drupal.py      # Drupal standards plugin
│   └── data/              # Database layer
│       └── database.py    # SQLite database interface
├── data/                  # Standards data files
│   └── drupal/
│       └── drupal_standards.csv
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Adding New Standards

### 1. Add to Existing Plugin

Edit the CSV file in `data/{plugin_name}/{plugin_name}_standards.csv`:

```csv
id,category,subcategory,title,description,severity,examples,references,tags,rationale,fix_guidance
NEW001,drupal_security,new_issue,New Security Issue,Description here,high,"{""good"": ""example"", ""bad"": ""example""}","[""https://example.com""]",security|new,Why this matters,How to fix it
```

### 2. Create a New Plugin

1. Create a new plugin file in `src/plugins/`:
```python
from .base import StandardsPlugin, Standard

class MyPlugin(StandardsPlugin):
    @property
    def name(self) -> str:
        return "myplugin"
    
    # ... implement required methods
```

2. Create data directory and CSV file:
```bash
mkdir data/myplugin
# Add your CSV file with standards
```

## Claude Desktop Configuration

Add this to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "devstandards": {
      "command": "/path/to/devstandards-mcp/devstandards-server"
    }
  }
}
```

After adding the configuration, restart Claude Desktop.

## Example Usage

### Get Drupal Security Standards
```python
result = await get_standards(
    category="drupal_security",
    severity="critical",
    limit=10
)
```

### Search for SQL-related Standards
```python
result = await search_standards(
    query="SQL injection",
    categories=["drupal_security", "owasp_top_10"]
)
```

### Get All Categories
```python
result = await get_categories()
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Write tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details