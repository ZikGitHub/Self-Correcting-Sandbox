import os
import sys
import subprocess
import venv
from typing import List, Dict, Any

class SandboxService:
    """Provisions isolated runtimes and executes commands safely."""
    
    def __init__(self, project_dir: str):
        self.project_dir = os.path.abspath(project_dir)
        self.venv_dir = os.path.join(self.project_dir, ".venv")
        self.bin_path = os.path.join(self.venv_dir, "Scripts" if sys.platform == "win32" else "bin")
        self.python_exe = os.path.join(self.bin_path, "python" + (".exe" if sys.platform == "win32" else ""))

    def setup_venv(self):
        """Initializes a Python virtual environment."""
        if not os.path.exists(self.venv_dir):
            print(f"[*] Creating venv at {self.venv_dir}...")
            venv.create(self.venv_dir, with_pip=True)
        return self.venv_dir

    def execute(self, cmd: List[str], env: Dict[str, str] = None) -> Dict[str, Any]:
        """Executes a terminal command inside the sandbox."""
        if not cmd:
            return {"stdout": "", "stderr": "Empty command", "returncode": 1}

        # Map 'python' to the sandbox executable
        if cmd[0] == "python":
            cmd[0] = self.python_exe
        
        full_env = os.environ.copy()
        full_env["VIRTUAL_ENV"] = self.venv_dir
        full_env["PATH"] = self.bin_path + os.pathsep + full_env.get("PATH", "")
        if env:
            full_env.update(env)

        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True,
            env=full_env
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
