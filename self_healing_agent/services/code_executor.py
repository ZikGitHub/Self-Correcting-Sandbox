import re
from typing import Optional
from .sandbox_service import SandboxService

class CodeExecutor:
    """Service to run application entry points and analyze crashes."""
    
    def __init__(self, sandbox: SandboxService):
        self.sandbox = sandbox

    def execute(self, entry_point: str):
        print(f"[*] Executing entry point: {entry_point}...")
        return self.sandbox.execute(["python", entry_point])

    def parse_missing_module(self, stderr: str) -> Optional[str]:
        """Detects if an error is due to a missing module."""
        match = re.search(r"ModuleNotFoundError: No module named '([^']+)'", stderr)
        if match: return match.group(1)
        match = re.search(r"ImportError: No module named ([^\s]+)", stderr)
        if match: return match.group(1)
        return None
