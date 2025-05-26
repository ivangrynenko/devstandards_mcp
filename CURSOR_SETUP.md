# Cursor AI Setup for DevStandards MCP Server

## Configuration Steps

1. **Open Cursor Settings**
   - Press `Cmd+,` (macOS) or `Ctrl+,` (Windows/Linux)
   - Navigate to "Features" → "MCP" or search for "MCP" in settings

2. **Add the MCP Server**
   
   In the MCP servers configuration, add:

   ```json
   {
     "devstandards": {
         "command": "/path-to/devstandards_mcp/devstandards-server",
         "args": [],
         "env": {},
         "enabled": true
      }
   }
   ```

3. **Restart Cursor**
   - Completely quit Cursor (Cmd+Q or File → Quit)
   - Start Cursor again

4. **Verify Connection**
   - Open the Command Palette (Cmd+Shift+P)
   - Type "MCP" and look for MCP-related commands
   - Check the status bar for MCP connection status

## Troubleshooting

### Server shows green but no tools

1. **Check Cursor Logs**
   - Open Command Palette (Cmd+Shift+P)
   - Run "Developer: Show Logs"
   - Look for MCP-related messages

2. **Test the Server Manually**
   ```bash
   # In terminal, run:
   /path/to/devstandards-mcp/devstandards-server
   ```
   
   Then type:
   ```json
   {"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"cursor","version":"1.0"}},"id":1}
   ```
   
   Press Enter, then type:
   ```json
   {"jsonrpc":"2.0","method":"tools/list","params":{},"id":2}
   ```
   
   You should see a list of 4 tools.

3. **Alternative Configuration**
   
   If the above doesn't work, try this configuration format:
   
   ```json
   {
     "mcpServers": [
       {
         "name": "devstandards",
         "command": "/path/to/devstandards-mcp/devstandards-server",
         "args": [],
         "env": {},
         "enabled": true
       }
     ]
   }
   ```

4. **Check File Permissions**
   ```bash
   ls -la /path/to/devstandards-mcp/devstandards-server
   # Should show -rwxr-xr-x (executable)
   ```

5. **Enable Debug Mode**
   
   Create a debug wrapper:
   ```bash
   #!/bin/bash
   export DEBUG_MCP=true
   exec /path/to/devstandards-mcp/devstandards-server
   ```
   
   Use this wrapper in your Cursor configuration to see debug output.

## Expected Behavior

When properly configured, you should be able to:

1. See "devstandards" in the MCP servers list (green status)
2. Use commands like:
   - "Validate my file against Drupal security standards using devstandards_mcp MCP tool"
   - "Inspect my module for SQL injection prevention using devstandards_mcp MCP tool"
   - "List all coding standard categories using devstandards_mcp MCP tool"
3. The AI assistant should have access to 4 tools:
   - get_standards
   - search_standards
   - get_categories
   - get_standard_by_id

## Known Issues

- Cursor may cache MCP server information. A full restart is often required.
- Some versions of Cursor may require the server to be in the system PATH.
- The MCP integration in Cursor is still evolving, so behavior may vary by version.