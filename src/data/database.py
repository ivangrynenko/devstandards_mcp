import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from contextlib import contextmanager
import aiosqlite
import asyncio

from ..plugins.base import Standard

class StandardsDatabase:
    """SQLite database for caching and querying standards"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS standards (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT,
                    examples TEXT,
                    reference_links TEXT,
                    tags TEXT,
                    rationale TEXT,
                    fix_guidance TEXT,
                    plugin_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON standards(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_severity ON standards(severity)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_plugin ON standards(plugin_name)")
            
            conn.commit()
    
    def sync_standards(self, standards: List[Standard], plugin_name: str):
        """Sync standards from a plugin to the database"""
        with self.get_connection() as conn:
            # Mark existing standards from this plugin for potential deletion
            existing_ids = set()
            cursor = conn.execute(
                "SELECT id FROM standards WHERE plugin_name = ?", 
                (plugin_name,)
            )
            existing_ids = {row['id'] for row in cursor}
            
            # Insert or update standards
            for standard in standards:
                conn.execute("""
                    INSERT OR REPLACE INTO standards 
                    (id, category, subcategory, title, description, severity,
                     examples, reference_links, tags, rationale, fix_guidance, 
                     plugin_name, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    standard.id,
                    standard.category,
                    standard.subcategory,
                    standard.title,
                    standard.description,
                    standard.severity,
                    json.dumps(standard.examples),
                    json.dumps(standard.references),
                    json.dumps(standard.tags),
                    standard.rationale,
                    standard.fix_guidance,
                    plugin_name,
                    datetime.now()
                ))
                
                existing_ids.discard(standard.id)
            
            # Remove standards that no longer exist in the plugin
            if existing_ids:
                placeholders = ','.join('?' * len(existing_ids))
                conn.execute(
                    f"DELETE FROM standards WHERE id IN ({placeholders})",
                    list(existing_ids)
                )
            
            conn.commit()
    
    def query_standards(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        severity: Optional[str] = None,
        plugin_name: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Standard]:
        """Query standards with filters"""
        with self.get_connection() as conn:
            # Build query
            query = "SELECT * FROM standards WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if subcategory:
                query += " AND subcategory = ?"
                params.append(subcategory)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            if plugin_name:
                query += " AND plugin_name = ?"
                params.append(plugin_name)
            
            if search:
                # Simple LIKE search
                query += " AND (title LIKE ? OR description LIKE ? OR rationale LIKE ? OR fix_guidance LIKE ?)"
                search_pattern = f"%{search}%"
                params.extend([search_pattern] * 4)
            
            query += " ORDER BY severity DESC, category, id"
            query += f" LIMIT {limit} OFFSET {offset}"
            
            cursor = conn.execute(query, params)
            standards = []
            
            for row in cursor:
                standards.append(Standard(
                    id=row['id'],
                    category=row['category'],
                    subcategory=row['subcategory'],
                    title=row['title'],
                    description=row['description'],
                    severity=row['severity'],
                    examples=json.loads(row['examples']),
                    references=json.loads(row['reference_links']),
                    tags=json.loads(row['tags']),
                    rationale=row['rationale'],
                    fix_guidance=row['fix_guidance']
                ))
            
            return standards
    
    async def async_query_standards(
        self,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        severity: Optional[str] = None,
        plugin_name: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Standard]:
        """Async version of query_standards for MCP server"""
        # For now, use sync version in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.query_standards,
            category, subcategory, severity, plugin_name, search, limit, offset
        )
    
    async def async_sync_standards(self, standards: List[Standard], plugin_name: str):
        """Async version of sync_standards for MCP server"""
        # For now, use sync version in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.sync_standards, standards, plugin_name)