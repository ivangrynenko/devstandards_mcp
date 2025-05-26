import asyncio
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server.stdio import stdio_server

from .config import Config
from .plugins.manager import PluginManager
from .data.database import StandardsDatabase

# Initialize components
config = Config()
plugin_manager = PluginManager(
    Path(__file__).parent / "plugins",
    Path(config.DATA_DIR)
)
database = StandardsDatabase(Path(config.DATA_DIR) / "standards.db")

# Create MCP server
app = Server("devstandards-mcp")

# Tool functions (for direct use in tests/demos)
async def get_standards(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """Get coding standards filtered by category, subcategory, and severity."""
    # Sync standards from plugins to database
    for plugin_name, plugin in plugin_manager.plugins.items():
        standards = plugin.load_standards()
        await database.async_sync_standards(standards, plugin_name)
    
    # Query from database
    standards = await database.async_query_standards(
        category=category,
        subcategory=subcategory,
        severity=severity,
        limit=limit
    )
    
    return {
        "status": "success",
        "data": {
            "standards": [std.to_dict() for std in standards],
            "metadata": {
                "total": len(standards),
                "version": config.VERSION,
                "plugins": plugin_manager.get_plugin_info()
            }
        }
    }

async def search_standards(
    query: str,
    categories: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """Search standards by text query, categories, and tags."""
    # Use plugin manager's search (includes database FTS)
    results = plugin_manager.search_standards(query, categories, tags)
    
    # Limit results
    results = results[:limit]
    
    return {
        "status": "success",
        "data": {
            "query": query,
            "results": [std.to_dict() for std in results],
            "metadata": {
                "count": len(results),
                "categories_searched": categories or "all",
                "tags_searched": tags or "all"
            }
        }
    }

async def get_categories() -> Dict[str, Any]:
    """Get all available categories and their descriptions."""
    categories = {}
    
    # Get categories from all plugins
    for plugin in plugin_manager.plugins.values():
        for cat_info in plugin.get_categories():
            cat_name = cat_info["name"]
            if cat_name not in categories:
                categories[cat_name] = {
                    "name": cat_name,
                    "description": cat_info["description"],
                    "plugins": [],
                    "count": 0
                }
            categories[cat_name]["plugins"].append(plugin.name)
    
    # Get counts from database
    standards = await database.async_query_standards()
    for std in standards:
        if std.category in categories:
            categories[std.category]["count"] += 1
    
    return {
        "status": "success",
        "data": {
            "categories": list(categories.values()),
            "metadata": {
                "total_categories": len(categories),
                "total_standards": len(standards)
            }
        }
    }

async def get_standard_by_id(standard_id: str) -> Dict[str, Any]:
    """Get a specific standard by its ID."""
    standards = await database.async_query_standards()
    
    for std in standards:
        if std.id == standard_id:
            return {
                "status": "success",
                "data": {
                    "standard": std.to_dict()
                }
            }
    
    return {
        "status": "error",
        "error": f"Standard '{standard_id}' not found"
    }

# Register MCP handlers
@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_standards",
            description="Get coding standards filtered by category, subcategory, and severity",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category (e.g., 'drupal_security')"
                    },
                    "subcategory": {
                        "type": "string",
                        "description": "Filter by subcategory (e.g., 'sql_injection')"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low", "info"],
                        "description": "Filter by severity level"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 50)",
                        "default": 50
                    }
                }
            }
        ),
        types.Tool(
            name="search_standards",
            description="Search standards by text query, categories, and tags",
            inputSchema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search text"
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by categories"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 50
                    }
                }
            }
        ),
        types.Tool(
            name="get_categories",
            description="Get all available categories and their descriptions",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="get_standard_by_id",
            description="Get a specific standard by its ID",
            inputSchema={
                "type": "object",
                "required": ["standard_id"],
                "properties": {
                    "standard_id": {
                        "type": "string",
                        "description": "The unique identifier of the standard"
                    }
                }
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "get_standards":
            result = await get_standards(**arguments)
        elif name == "search_standards":
            result = await search_standards(**arguments)
        elif name == "get_categories":
            result = await get_categories()
        elif name == "get_standard_by_id":
            result = await get_standard_by_id(**arguments)
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
        
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({
            "status": "error",
            "error": str(e)
        }, indent=2))]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        # Create initialization options with proper capabilities
        init_options = InitializationOptions(
            server_name="devstandards-mcp",
            server_version=config.VERSION,
            capabilities={
                "tools": {}  # Indicate we support tools
            }
        )
        
        await app.run(
            read_stream,
            write_stream,
            init_options
        )

# For backwards compatibility
server = app
handle_list_tools = handle_list_tools
handle_call_tool = handle_call_tool

if __name__ == "__main__":
    asyncio.run(main())