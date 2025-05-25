import csv
import json
from pathlib import Path
from typing import List, Dict
from .base import StandardsPlugin, Standard

class DrupalStandardsPlugin(StandardsPlugin):
    """Plugin for Drupal coding standards and best practices"""
    
    @property
    def name(self) -> str:
        return "drupal"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Drupal security, coding standards, and best practices"
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._standards: List[Standard] = []
        self._categories = {
            "drupal_security": "Security best practices for Drupal",
            "drupal_coding_standards": "Drupal coding conventions and formatting",
            "drupal_best_practices": "Drupal development best practices",
            "drupal_performance": "Performance optimization guidelines"
        }
    
    def load_standards(self) -> List[Standard]:
        """Load standards from CSV file"""
        if self._standards:  # Return cached standards
            return self._standards
            
        csv_file = self.data_path / "drupal_standards.csv"
        if not csv_file.exists():
            return []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Parse JSON fields
                    examples = json.loads(row.get('examples', '{}'))
                    references = json.loads(row.get('references', '[]'))
                    tags = [tag.strip() for tag in row.get('tags', '').split('|')]
                    
                    standard = Standard(
                        id=row['id'],
                        category=row['category'],
                        subcategory=row['subcategory'],
                        title=row['title'],
                        description=row['description'],
                        severity=row['severity'],
                        examples=examples,
                        references=references,
                        tags=tags,
                        rationale=row.get('rationale'),
                        fix_guidance=row.get('fix_guidance')
                    )
                    
                    # Validate before adding
                    errors = self.validate_standard(standard)
                    if errors:
                        print(f"Validation errors for {row['id']}: {errors}")
                        continue
                        
                    self._standards.append(standard)
                    
                except Exception as e:
                    print(f"Error loading standard {row.get('id', 'unknown')}: {e}")
        
        return self._standards
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get all categories with descriptions"""
        return [
            {"name": name, "description": desc}
            for name, desc in self._categories.items()
        ]