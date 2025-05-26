#!/usr/bin/env python
"""Check MCP library structure"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Check what's in mcp.types
try:
    import mcp.types
    print("mcp.types contents:")
    for item in dir(mcp.types):
        if not item.startswith('_') and 'Capabilit' in item:
            print(f"  {item}")
    
    # Try to access ServerCapabilities
    if hasattr(mcp.types, 'ServerCapabilities'):
        print("\nServerCapabilities found in mcp.types")
        print(f"Fields: {mcp.types.ServerCapabilities.model_fields}")
    else:
        print("\nServerCapabilities NOT found in mcp.types")
        
except Exception as e:
    print(f"Error: {e}")

# Check server initialization
try:
    from mcp.server.models import InitializationOptions
    print("\n\nInitializationOptions fields:")
    print(InitializationOptions.model_fields)
except Exception as e:
    print(f"Error checking InitializationOptions: {e}")