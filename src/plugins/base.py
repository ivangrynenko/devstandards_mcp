from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class Standard:
    """Represents a coding standard or best practice"""
    id: str
    category: str
    subcategory: str
    title: str
    description: str
    severity: str  # critical, high, medium, low, info
    examples: Dict[str, str]  # {"good": "...", "bad": "..."}
    references: List[str]
    tags: List[str]
    rationale: Optional[str] = None
    fix_guidance: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO format
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data

class StandardsPlugin(ABC):
    """Base class for all standards plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier (e.g., 'drupal', 'owasp')"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description"""
        pass
    
    @abstractmethod
    def load_standards(self) -> List[Standard]:
        """Load all standards from the plugin's data source"""
        pass
    
    @abstractmethod
    def get_categories(self) -> List[Dict[str, str]]:
        """Get all categories with descriptions"""
        pass
    
    def validate_standard(self, standard: Standard) -> List[str]:
        """Validate a standard object, return list of errors"""
        errors = []
        if not standard.id:
            errors.append("Standard ID is required")
        if not standard.title:
            errors.append("Standard title is required")
        if standard.severity not in ['critical', 'high', 'medium', 'low', 'info']:
            errors.append(f"Invalid severity: {standard.severity}")
        return errors