# Plugin Development Guide

This guide explains how to create plugins for the DevStandards MCP server to add support for new programming languages, frameworks, or coding standards.

## Overview

The plugin system allows you to extend the DevStandards server with new standards without modifying the core codebase. Each plugin:

- Loads standards from CSV files in its data directory
- Provides category definitions
- Validates standard data
- Integrates automatically with the MCP server

## Plugin Architecture

```
devstandards-mcp/
├── src/
│   └── plugins/
│       ├── base.py          # Base plugin interface
│       ├── manager.py       # Plugin discovery and management
│       └── drupal.py        # Example plugin implementation
└── data/
    └── drupal/              # Plugin data directory
        ├── drupal_standards.csv
        └── test_standards.csv   # Additional CSV files loaded automatically
```

## Creating a New Plugin

### Step 1: Create Plugin Class

Create a new Python file in `src/plugins/` (e.g., `javascript.py`):

```python
import csv
import json
from pathlib import Path
from typing import List, Dict
from .base import StandardsPlugin, Standard

class JavaScriptStandardsPlugin(StandardsPlugin):
    """Plugin for JavaScript/TypeScript coding standards"""
    
    @property
    def name(self) -> str:
        """Unique plugin identifier"""
        return "javascript"
    
    @property
    def version(self) -> str:
        """Plugin version"""
        return "1.0.0"
    
    @property
    def description(self) -> str:
        """Human-readable description"""
        return "JavaScript and TypeScript best practices and coding standards"
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._standards: List[Standard] = []
        self._categories = {
            "js_security": "Security best practices for JavaScript",
            "js_performance": "Performance optimization techniques",
            "js_es6": "Modern ES6+ patterns and features",
            "js_react": "React best practices",
            "js_typescript": "TypeScript specific guidelines"
        }
    
    def load_standards(self) -> List[Standard]:
        """Load standards from all CSV files in the plugin's data directory"""
        if self._standards:  # Return cached standards
            return self._standards
        
        # Load all CSV files in the data directory
        csv_files = list(self.data_path.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in {self.data_path}")
            return []
        
        for csv_file in csv_files:
            print(f"Loading standards from {csv_file.name}")
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Parse JSON fields
                        examples = json.loads(row.get('examples', '{}'))
                        references = json.loads(row.get('references', '[]'))
                        tags = [tag.strip() for tag in row.get('tags', '').split('|')]
                        
                        standard = Standard(
                            id=row['id'],
                            category=row['category'],
                            subcategory=row['subcategory'],
                            title=row['title'],
                            description=row['description'],
                            severity=row['severity'],
                            examples=examples,
                            references=references,
                            tags=tags,
                            rationale=row.get('rationale'),
                            fix_guidance=row.get('fix_guidance')
                        )
                        
                        # Validate before adding
                        errors = self.validate_standard(standard)
                        if errors:
                            print(f"Validation errors for {row['id']}: {errors}")
                            continue
                            
                        self._standards.append(standard)
                        
                    except Exception as e:
                        print(f"Error loading standard {row.get('id', 'unknown')} from {csv_file.name}: {e}")
        
        print(f"Loaded {len(self._standards)} standards from {len(csv_files)} CSV files")
        return self._standards
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get all categories with descriptions"""
        return [
            {"name": name, "description": desc}
            for name, desc in self._categories.items()
        ]
```

### Step 2: Create Data Directory

Create a directory for your plugin's data:

```bash
mkdir -p data/javascript
```

### Step 3: Add CSV Data

Create CSV files in your plugin's data directory. All CSV files will be loaded automatically.

Example `data/javascript/security_standards.csv`:

```csv
id,category,subcategory,title,description,severity,examples,references,tags,rationale,fix_guidance
JS001,js_security,xss,Sanitize User Input,Always sanitize user input before displaying in DOM,critical,"{""good"": ""element.textContent = userInput;"", ""bad"": ""element.innerHTML = userInput;""}","[""https://owasp.org/www-community/attacks/xss/""]",security|xss|dom,Unsanitized input can lead to XSS attacks,Use textContent or proper sanitization libraries
JS002,js_security,validation,Validate on Server Side,Never trust client-side validation alone,high,"{""good"": ""// Server validates all inputs"", ""bad"": ""// Only client-side validation""}","[""https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html""]",security|validation,Client-side validation can be bypassed,Implement server-side validation for all inputs
```

### Step 4: Enable Plugin

Add your plugin to the `PLUGINS_ENABLED` list in `.env`:

```bash
PLUGINS_ENABLED=drupal,javascript
```

## Plugin Interface (StandardsPlugin)

All plugins must inherit from `StandardsPlugin` and implement these properties and methods:

### Required Properties

```python
@property
def name(self) -> str:
    """Unique identifier for the plugin"""
    
@property
def version(self) -> str:
    """Plugin version (semantic versioning recommended)"""
    
@property
def description(self) -> str:
    """Human-readable description of the plugin"""
```

### Required Methods

```python
def load_standards(self) -> List[Standard]:
    """Load and return all standards from the plugin's data sources"""
    
def get_categories(self) -> List[Dict[str, str]]:
    """Return list of categories with name and description"""
```

### Inherited Methods

```python
def validate_standard(self, standard: Standard) -> List[str]:
    """Validate a standard object (inherited from base class)"""
```

## Standard Data Model

Each standard must conform to this structure:

```python
@dataclass
class Standard:
    id: str                    # Unique identifier (e.g., "JS001")
    category: str              # Main category (e.g., "js_security")
    subcategory: str           # Subcategory (e.g., "xss")
    title: str                 # Brief title
    description: str           # Detailed description
    severity: str              # critical|high|medium|low|info
    examples: dict = field(default_factory=dict)     # Code examples
    references: list = field(default_factory=list)   # Reference URLs
    tags: list = field(default_factory=list)         # Searchable tags
    rationale: Optional[str] = None                  # Why it matters
    fix_guidance: Optional[str] = None               # How to fix
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

## CSV Format

CSV files must include these columns:

```csv
id,category,subcategory,title,description,severity,examples,references,tags,rationale,fix_guidance
```

### Field Formats

- **id**: Unique string identifier
- **category**: Must match a category defined in the plugin
- **subcategory**: Logical grouping within category
- **title**: Brief, descriptive title
- **description**: Detailed explanation
- **severity**: One of: critical, high, medium, low, info
- **examples**: JSON object with "good" and "bad" code examples
- **references**: JSON array of reference URLs
- **tags**: Pipe-separated list (e.g., "security|validation|input")
- **rationale**: Why this standard is important
- **fix_guidance**: How to implement or fix

### Example CSV Entry

```csv
JS003,js_performance,optimization,Use const/let over var,Prefer const and let for better scoping and performance,medium,"{""good"": ""const value = 42;"", ""bad"": ""var value = 42;""}","[""https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const""]",es6|scoping|performance,Block scoping prevents bugs and enables optimizations,Replace var with const for immutable values and let for mutable ones
```

## Best Practices

### 1. Dynamic CSV Loading

The plugin automatically loads all `*.csv` files from its data directory:

```python
csv_files = list(self.data_path.glob("*.csv"))
```

This allows you to organize standards into multiple files:
- `security_standards.csv`
- `performance_standards.csv`
- `react_standards.csv`
- etc.

### 2. Category Management

Define all categories in the plugin's `__init__` method:

```python
self._categories = {
    "js_security": "Security best practices",
    "js_performance": "Performance guidelines",
    # Add all categories your standards will use
}
```

### 3. Error Handling

Always handle parsing errors gracefully:

```python
try:
    # Parse standard
except Exception as e:
    print(f"Error loading standard {row.get('id', 'unknown')}: {e}")
    continue  # Skip problematic entries
```

### 4. Validation

Use the inherited `validate_standard` method to ensure data quality:

```python
errors = self.validate_standard(standard)
if errors:
    print(f"Validation errors for {row['id']}: {errors}")
    continue
```

### 5. Caching

Cache loaded standards to avoid repeated file I/O:

```python
if self._standards:  # Return cached standards
    return self._standards
```

## Testing Your Plugin

### 1. Unit Test

Create a test file `test_plugin.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.plugins.javascript import JavaScriptStandardsPlugin

# Test plugin loading
plugin = JavaScriptStandardsPlugin(Path("data/javascript"))
standards = plugin.load_standards()
print(f"Loaded {len(standards)} standards")

# Test categories
categories = plugin.get_categories()
print(f"Categories: {[c['name'] for c in categories]}")
```

### 2. Integration Test

Use the validation script:

```bash
python test_mcp_validation.py
```

### 3. MCP Test

Test through MCP tools:

```python
import asyncio
from src.server import get_standards

async def test():
    result = await get_standards(category="js_security")
    print(result)

asyncio.run(test())
```

## Plugin Discovery

The `PluginManager` automatically discovers plugins by:

1. Scanning `src/plugins/*.py` files
2. Finding classes that inherit from `StandardsPlugin`
3. Instantiating each plugin with its data directory
4. Loading standards when first queried

## Troubleshooting

### Plugin Not Loading

1. Check the plugin file is in `src/plugins/`
2. Verify the class inherits from `StandardsPlugin`
3. Ensure all required properties/methods are implemented
4. Check for syntax errors in the plugin file

### Standards Not Found

1. Verify CSV files exist in `data/{plugin_name}/`
2. Check CSV format matches the expected columns
3. Look for parsing errors in console output
4. Ensure categories in CSV match plugin's `_categories`

### Validation Errors

Common validation issues:
- Invalid severity level (must be: critical/high/medium/low/info)
- Missing required fields (id, category, title, etc.)
- Malformed JSON in examples or references fields
- Category not defined in plugin's `_categories`

## Example Plugins

### Minimal Plugin

```python
from .base import StandardsPlugin, Standard

class MinimalPlugin(StandardsPlugin):
    @property
    def name(self) -> str:
        return "minimal"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Minimal example plugin"
    
    def load_standards(self) -> List[Standard]:
        # Load from CSV files
        return []
    
    def get_categories(self) -> List[Dict[str, str]]:
        return [{"name": "example", "description": "Example category"}]
```

### Advanced Plugin Features

You can extend plugins with additional features:

- Custom validation rules
- Multiple data sources (CSV, JSON, API)
- Dynamic category generation
- Standard generation from code analysis
- Integration with external tools

## Contributing

When contributing a new plugin:

1. Follow the naming convention: `{language}_standards.py`
2. Include comprehensive CSV data
3. Add tests for your plugin
4. Update documentation
5. Submit a pull request

## Summary

Creating a plugin involves:

1. **Create plugin class** inheriting from `StandardsPlugin`
2. **Implement required properties** (name, version, description)
3. **Implement load_standards()** to load CSV files
4. **Implement get_categories()** to define categories
5. **Create data directory** and add CSV files
6. **Enable plugin** in configuration
7. **Test** the plugin works correctly

The plugin system makes it easy to extend DevStandards with new languages and frameworks while maintaining a consistent interface for AI assistants.