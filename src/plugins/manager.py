from typing import Dict, List, Optional, Type
from pathlib import Path
import importlib
import inspect
from .base import StandardsPlugin, Standard

class PluginManager:
    """Manages loading and accessing standards plugins"""
    
    def __init__(self, plugins_dir: Path, data_dir: Path):
        self.plugins_dir = plugins_dir
        self.data_dir = data_dir
        self.plugins: Dict[str, StandardsPlugin] = {}
        self.plugin_classes: Dict[str, Type[StandardsPlugin]] = {}
        self._discover_plugins()
        self._load_plugins()
    
    def _discover_plugins(self):
        """Discover available plugin classes"""
        self.plugin_classes = {}
        
        # Import all Python files in plugins directory
        for file in self.plugins_dir.glob("*.py"):
            if file.name.startswith("_") or file.name in ["base.py", "manager.py"]:
                continue
            
            module_name = f"src.plugins.{file.stem}"
            try:
                module = importlib.import_module(module_name)
                
                # Find StandardsPlugin subclasses
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, StandardsPlugin) and 
                        obj != StandardsPlugin and
                        obj.__module__ == module_name):
                        # Create a temporary instance to get the name
                        temp_instance = obj(self.data_dir)
                        self.plugin_classes[temp_instance.name] = obj
            except Exception as e:
                print(f"Error loading plugin module {module_name}: {e}")
    
    def _load_plugins(self):
        """Instantiate all discovered plugins"""
        for plugin_name, plugin_class in self.plugin_classes.items():
            try:
                # Create data directory for plugin if it doesn't exist
                plugin_data_dir = self.data_dir / plugin_name
                plugin_data_dir.mkdir(exist_ok=True, parents=True)
                
                # Instantiate plugin
                plugin = plugin_class(plugin_data_dir)
                self.plugins[plugin.name] = plugin
                print(f"Loaded plugin: {plugin.name} v{plugin.version}")
            except Exception as e:
                print(f"Error instantiating plugin {plugin_name}: {e}")
    
    def get_all_standards(self) -> List[Standard]:
        """Get all standards from all plugins"""
        standards = []
        for plugin in self.plugins.values():
            standards.extend(plugin.load_standards())
        return standards
    
    def get_standards_by_category(self, category: str) -> List[Standard]:
        """Get standards filtered by category"""
        standards = []
        for plugin in self.plugins.values():
            plugin_standards = plugin.load_standards()
            standards.extend([s for s in plugin_standards if s.category == category])
        return standards
    
    def search_standards(self, query: str, categories: Optional[List[str]] = None,
                        tags: Optional[List[str]] = None) -> List[Standard]:
        """Search standards by query text, categories, and tags"""
        all_standards = self.get_all_standards()
        results = []
        
        query_lower = query.lower() if query else ""
        
        for standard in all_standards:
            # Filter by categories
            if categories and standard.category not in categories:
                continue
            
            # Filter by tags
            if tags and not any(tag in standard.tags for tag in tags):
                continue
            
            # Search in text fields
            if query:
                searchable_text = " ".join([
                    standard.title,
                    standard.description,
                    standard.rationale or "",
                    standard.fix_guidance or "",
                    " ".join(standard.tags)
                ]).lower()
                
                if query_lower not in searchable_text:
                    continue
            
            results.append(standard)
        
        return results
    
    def get_plugin_info(self) -> List[Dict[str, str]]:
        """Get information about loaded plugins"""
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description
            }
            for plugin in self.plugins.values()
        ]