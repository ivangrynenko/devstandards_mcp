# This file is kept for backward compatibility
# All functionality has been moved to memory_store.py

from pathlib import Path
from .memory_store import StandardsMemoryStore

# Create a compatibility wrapper
class StandardsDatabase(StandardsMemoryStore):
    """Compatibility wrapper - now uses in-memory storage instead of SQLite"""
    
    def __init__(self, db_path: Path):
        # Ignore db_path as we're using in-memory storage
        super().__init__()
        
    def _init_database(self):
        """No-op for compatibility"""
        pass
    
    def get_connection(self):
        """No-op for compatibility"""
        class DummyConnection:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        return DummyConnection()