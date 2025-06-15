from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import asyncio
from threading import Lock

from ..plugins.base import Standard


class StandardsMemoryStore:
    """In-memory store for standards data"""
    
    def __init__(self):
        self._standards: Dict[str, Standard] = {}
        self._lock = Lock()
        self._plugin_standards: Dict[str, set] = {}  # Track which standards belong to which plugin
    
    def sync_standards(self, standards: List[Standard], plugin_name: str):
        """Sync standards from a plugin to the memory store"""
        with self._lock:
            # Remove old standards from this plugin
            if plugin_name in self._plugin_standards:
                for std_id in self._plugin_standards[plugin_name]:
                    if std_id in self._standards:
                        del self._standards[std_id]
            
            # Add new standards
            new_ids = set()
            for standard in standards:
                self._standards[standard.id] = standard
                new_ids.add(standard.id)
            
            self._plugin_standards[plugin_name] = new_ids
    
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
        with self._lock:
            results = []
            
            # Filter standards
            for standard in self._standards.values():
                # Check category filter
                if category and standard.category != category:
                    continue
                
                # Check subcategory filter
                if subcategory and standard.subcategory != subcategory:
                    continue
                
                # Check severity filter
                if severity and standard.severity != severity:
                    continue
                
                # Check plugin filter
                if plugin_name:
                    found_in_plugin = False
                    for plugin, std_ids in self._plugin_standards.items():
                        if plugin == plugin_name and standard.id in std_ids:
                            found_in_plugin = True
                            break
                    if not found_in_plugin:
                        continue
                
                # Check search filter
                if search:
                    search_lower = search.lower()
                    if not any([
                        search_lower in (standard.title or '').lower(),
                        search_lower in (standard.description or '').lower(),
                        search_lower in (standard.rationale or '').lower(),
                        search_lower in (standard.fix_guidance or '').lower()
                    ]):
                        continue
                
                results.append(standard)
            
            # Sort by severity priority (critical > high > medium > low > info), then by category and id
            severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
            results.sort(key=lambda s: (
                severity_order.get(s.severity or 'info', 5),
                s.category,
                s.id
            ))
            
            # Apply offset and limit
            return results[offset:offset + limit]
    
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
        """Async version of query_standards"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.query_standards,
            category, subcategory, severity, plugin_name, search, limit, offset
        )
    
    async def async_sync_standards(self, standards: List[Standard], plugin_name: str):
        """Async version of sync_standards"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.sync_standards, standards, plugin_name)
    
    def get_all_categories(self) -> Dict[str, int]:
        """Get all categories with counts"""
        with self._lock:
            categories = {}
            for standard in self._standards.values():
                if standard.category not in categories:
                    categories[standard.category] = 0
                categories[standard.category] += 1
            return categories
    
    def get_standard_by_id(self, standard_id: str) -> Optional[Standard]:
        """Get a specific standard by ID"""
        with self._lock:
            return self._standards.get(standard_id)
    
    def clear(self):
        """Clear all standards from memory"""
        with self._lock:
            self._standards.clear()
            self._plugin_standards.clear()