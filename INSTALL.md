# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/devstandards-mcp.git
   cd devstandards-mcp
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

6. **Make the server executable**
   ```bash
   chmod +x devstandards-server
   ```

## Running the Server

### Option 1: Using the launcher script
```bash
./devstandards-server
```

### Option 2: Using Python directly
```bash
source venv/bin/activate  # If not already activated
python -m src.server
```

### Option 3: Using the server.py entry point
```bash
source venv/bin/activate  # If not already activated
python server.py
```

## Configuration for AI Clients

When configuring AI clients (Claude Desktop, Cursor, VSCode, etc.), use the full path to the `devstandards-server` executable:

```json
{
  "mcpServers": {
    "devstandards": {
      "command": "/full/path/to/devstandards-mcp/devstandards-server"
    }
  }
}
```

To find the full path:
```bash
cd devstandards-mcp
pwd  # This shows the full path to the project
```

Then append `/devstandards-server` to that path.

## Troubleshooting

1. **Virtual environment not found**
   - Make sure you created the venv: `python -m venv venv`
   - Check that the venv directory exists in the project root

2. **Module not found errors**
   - Ensure the virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

3. **Permission denied**
   - Make the server executable: `chmod +x devstandards-server`

4. **Server not starting**
   - Check Python version: `python --version` (should be 3.8+)
   - Try running with debug mode: `DEBUG_MCP=true ./devstandards-server`