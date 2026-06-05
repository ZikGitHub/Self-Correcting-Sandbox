import os
from typing import Dict

class ProjectWriter:
    """Service to create workspace directories and write source files."""
    
    def __init__(self, base_path: str):
        self.base_path = os.path.abspath(base_path)

    def write_project(self, project_name: str, files: Dict[str, str]):
        project_dir = os.path.join(self.base_path, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        for filename, content in files.items():
            file_path = os.path.join(project_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        
        return project_dir
