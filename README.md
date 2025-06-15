# DevStandards MCP Server

A Model Context Protocol (MCP) server that provides AI agents with access to development best practices, security guidelines, and coding standards across multiple programming languages and frameworks.

## Features

- **Plugin Architecture**: Extensible system for adding new languages and frameworks
- **In-Memory Storage**: Fast in-memory data store for instant querying
- **Dynamic CSV Loading**: Automatically loads all CSV files from plugin data directories
- **235+ Coding Standards**: Comprehensive coverage of security, accessibility, performance, and best practices
- **MCP Tools**: Four tools for querying standards:
  - `get_standards`: Filter by category, subcategory, and severity
  - `search_standards`: Full-text search across all standards
  - `get_categories`: List all available categories
  - `get_standard_by_id`: Get details for a specific standard

## Included Standards

The server currently includes 235+ Drupal coding standards across these categories:

- **Security** (80+ standards): SQL injection, XSS, CSRF, access control, file uploads, authentication
- **Coding Standards** (26+ standards): PHP standards, naming conventions, code organization
- **Best Practices** (17+ standards): Field API, dependency injection, configuration management
- **Performance** (11+ standards): Caching strategies, render optimization, database queries
- **Frontend** (16+ standards): Theme development, responsive design, CSS/JS aggregation
- **Accessibility** (8+ standards): WCAG compliance, ARIA attributes, semantic HTML
- **JavaScript** (9+ standards): Drupal behaviors, jQuery optimization, ES6 patterns
- **Testing** (7+ standards): PHPUnit, Behat, functional testing, test coverage
- **API** (6+ standards): REST, JSON:API, GraphQL best practices
- **DevOps** (6+ standards): CI/CD, deployment, environment management
- **Database** (5+ standards): Schema design, migrations, query optimization
- **Documentation** (7+ standards): Code comments, README files, API documentation
- **And more**: Git workflows, build processes, integration patterns, Twig templates

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
│   └── data/              # Data storage layer
│       ├── database.py    # Compatibility wrapper
│       └── memory_store.py # In-memory data store
├── data/                  # Standards data files
│   └── drupal/
│       └── drupal_standards.csv
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Adding New Standards

### 1. Add to Existing Plugin

Create or edit any CSV file in the plugin's data directory (`data/{plugin_name}/*.csv`). The plugin will automatically load all CSV files:

```csv
id,category,subcategory,title,description,severity,examples,references,tags,rationale,fix_guidance
NEW001,drupal_security,new_issue,New Security Issue,Description here,high,"{""good"": ""example"", ""bad"": ""example""}","[""https://example.com""]",security|new,Why this matters,How to fix it
```

**Note**: The Drupal plugin dynamically loads all CSV files from `data/drupal/`, so you can organize standards into multiple files (e.g., `security_standards.csv`, `performance_standards.csv`, etc.)

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

## MCP Client Configuration

### Claude Desktop

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

### VSCode with Continue.dev

[Continue.dev](https://continue.dev) is an AI coding assistant for VSCode that supports MCP servers.

1. Install the Continue extension in VSCode
2. Open Continue's configuration (`~/.continue/config.json`)
3. Add the MCP server configuration:

```json
{
  "models": [...],
  "mcpServers": {
    "devstandards": {
      "command": "/path/to/devstandards-mcp/devstandards-server"
    }
  }
}
```

### Cursor Editor

Cursor supports MCP servers through its AI configuration:

1. Open Cursor Settings (Cmd+, on macOS)
2. Navigate to "AI" → "Model Context Protocol"
3. Add server configuration:

```json
{
  "devstandards": {
    "command": "/path/to/devstandards-mcp/devstandards-server",
    "description": "Drupal coding standards and best practices"
  }
}
```

### Zed Editor

For Zed editor with AI assistant features:

1. Open Zed settings (`~/.config/zed/settings.json`)
2. Add to the assistant configuration:

```json
{
  "assistant": {
    "mcp_servers": {
      "devstandards": {
        "command": "/path/to/devstandards-mcp/devstandards-server"
      }
    }
  }
}
```

### Generic MCP Client Configuration

For any MCP-compatible client, use these settings:

- **Command**: `/path/to/devstandards-mcp/devstandards-server`
- **Protocol**: stdio (standard input/output)
- **Transport**: JSON-RPC over stdio
- **Initialization**: No special parameters required

### Using with Python Scripts

You can also use the MCP server programmatically:

```python
import subprocess
import json

# Start the server
proc = subprocess.Popen(
    ["/path/to/devstandards-mcp/devstandards-server"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send a request
request = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "get_standards",
        "arguments": {
            "category": "drupal_security",
            "severity": "critical"
        }
    },
    "id": 1
}

proc.stdin.write(json.dumps(request) + "\n")
proc.stdin.flush()

# Read response
response = json.loads(proc.stdout.readline())
print(response)
```

### Troubleshooting

If you encounter issues:

1. **Check logs**: Most MCP clients provide debug logs
2. **Test manually**: Run `echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}' | ./devstandards-server`
3. **Verify paths**: Ensure the executable path is correct and the file is executable (`chmod +x devstandards-server`)
4. **Python environment**: The server uses its own virtual environment, no need to activate it

## Available MCP Tools

Once connected, the following tools are available to AI assistants:

### 1. get_standards
Query coding standards with filters:
- **category**: Filter by category (e.g., "drupal_security", "drupal_performance")
- **subcategory**: Filter by subcategory (e.g., "sql_injection", "xss")
- **severity**: Filter by severity level ("critical", "high", "medium", "low", "info")
- **limit**: Maximum number of results (default: 50)

Example query: "Show me all critical security standards for Drupal"

### 2. search_standards
Full-text search across all standards:
- **query**: Search text (required)
- **categories**: List of categories to search within (optional)
- **tags**: List of tags to filter by (optional)
- **limit**: Maximum number of results (default: 50)

Example query: "Search for standards about SQL injection"

### 3. get_categories
List all available categories with descriptions and counts.

Example query: "What categories of standards are available?"

### 4. get_standard_by_id
Get detailed information about a specific standard:
- **standard_id**: The unique identifier (e.g., "DS001", "SEC001")

Example query: "Show me details for standard DS001"

## Example Prompts for AI Assistants

When using an MCP client with this server, you can ask:

- "What are the critical security standards I should follow for Drupal?"
- "Show me best practices for Drupal forms"
- "Search for standards about caching and performance"
- "How should I handle user input to prevent XSS attacks?"
- "What's the proper way to use Drupal's Database API?"
- "List all accessibility standards"
- "Show me examples of good vs bad code for SQL queries"

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Write tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details