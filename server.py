#!/usr/bin/env python
"""Entry point for the DevStandards MCP Server"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the server
from src.server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())