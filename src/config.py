import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration management for the MCP server"""
    
    # Server settings
    VERSION = "1.0.0"
    SERVER_NAME = "devstandards-mcp"
    
    # Network settings
    HOST = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))
    EXTERNAL_PORT = int(os.getenv("EXTERNAL_PORT", "8001"))
    
    # Determine project root - try multiple methods
    @staticmethod
    def get_project_root():
        # Method 1: From environment variable set by the executable
        if os.environ.get("DEVSTANDARDS_PROJECT_ROOT"):
            return os.environ["DEVSTANDARDS_PROJECT_ROOT"]
        
        # Method 2: If running from the project directory
        if os.path.exists("data") and os.path.exists("src"):
            return os.getcwd()
        
        # Method 3: From the module file location
        try:
            module_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(module_dir)
            if os.path.exists(os.path.join(project_root, "data")):
                return project_root
        except:
            pass
        
        # Method 4: Check common project locations
        # Removed hardcoded paths - rely on other detection methods
        
        # Method 5: From sys.path if added by the entry script
        for path in sys.path:
            if path.endswith("devstandards_mcp") and os.path.exists(os.path.join(path, "data")):
                return path
        
        # Fallback: use current directory
        return os.getcwd()
    
    def __init__(self):
        # Get project root
        project_root = self.get_project_root()
        
        # Data settings with absolute paths
        self.DATA_DIR = os.getenv("DATA_DIR", os.path.join(project_root, "data"))
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(project_root, "data", "standards.db"))
        
        # Cache settings
        self.ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
        
        # Plugin settings
        self.PLUGINS_ENABLED = os.getenv("PLUGINS_ENABLED", "drupal,owasp").split(",")
        
        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
        
        # Debug output
        if os.getenv("DEBUG_MCP", "false").lower() == "true":
            print(f"Project root: {project_root}", file=sys.stderr)
            print(f"Data directory: {self.DATA_DIR}", file=sys.stderr)
            print(f"Database path: {self.DATABASE_PATH}", file=sys.stderr)
        
        # Ensure directories exist
        try:
            Path(self.DATA_DIR).mkdir(exist_ok=True, parents=True)
        except OSError as e:
            # If we can't create the directory, use a fallback in user's home
            fallback_dir = os.path.expanduser("~/.devstandards-mcp/data")
            print(f"Warning: Could not create data directory at {self.DATA_DIR}, using {fallback_dir}", file=sys.stderr)
            self.DATA_DIR = fallback_dir
            self.DATABASE_PATH = os.path.join(fallback_dir, "standards.db")
            Path(self.DATA_DIR).mkdir(exist_ok=True, parents=True)