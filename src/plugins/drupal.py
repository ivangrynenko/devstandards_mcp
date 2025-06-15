import csv
import json
import ast
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
            "drupal_performance": "Performance optimization guidelines",
            "drupal_javascript": "JavaScript coding standards for Drupal",
            "drupal_sql": "SQL and database standards for Drupal",
            "drupal_twig": "Twig template standards for Drupal"
        }
    
    def load_standards(self) -> List[Standard]:
        """Load standards from multiple CSV files"""
        if self._standards:  # Return cached standards
            return self._standards
        
        # List of CSV files to load for Drupal standards
        csv_files = [
            "drupal_javascript_standards.csv",
            "drupal_sql_standards.csv", 
            "drupal_twig_standards.csv"
        ]
        
        for csv_filename in csv_files:
            csv_file = self.data_path / "standards" / csv_filename
            if not csv_file.exists():
                print(f"Warning: {csv_filename} not found at {csv_file}")
                continue
            
            self._load_csv_file(csv_file)
        
        return self._standards
    
    def _load_csv_file(self, csv_file: Path):
        """Load standards from a single CSV file"""
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Parse JSON and list fields with better error handling
                    try:
                        examples = json.loads(row.get('examples', '{}'))
                    except json.JSONDecodeError as e:
                        print(f"Error parsing examples for {row.get('id', 'unknown')}: {e}")
                        print(f"Examples field: {repr(row.get('examples', ''))[:200]}")
                        continue
                    
                    # References are stored as Python list strings in CSV
                    references_str = row.get('references', '[]')
                    try:
                        references = ast.literal_eval(references_str) if references_str.startswith('[') else []
                    except (ValueError, SyntaxError) as e:
                        print(f"Error parsing references for {row.get('id', 'unknown')}: {e}")
                        print(f"References field: {repr(references_str[:200])}")
                        references = []
                    
                    # Tags are stored as Python list strings in CSV
                    tags_str = row.get('tags', '[]')
                    try:
                        tags = ast.literal_eval(tags_str) if tags_str.startswith('[') else [tag.strip() for tag in tags_str.split('|') if tag.strip()]
                    except (ValueError, SyntaxError) as e:
                        print(f"Error parsing tags for {row.get('id', 'unknown')}: {e}")
                        print(f"Tags field: {repr(tags_str[:200])}")
                        tags = []
                    
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
                    print(f"Error loading standard {row.get('id', 'unknown')} from {csv_file.name}: {e}")
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get all categories with descriptions"""
        return [
            {"name": name, "description": desc}
            for name, desc in self._categories.items()
        ]