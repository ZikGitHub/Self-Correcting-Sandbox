import os
import sys

# Ensure the framework is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from self_healing_agent.services.project_writer import ProjectWriter
from self_healing_agent.services.sandbox_service import SandboxService
from self_healing_agent.services.ollama_service import OllamaService
from self_healing_agent.services.code_executor import CodeExecutor
from self_healing_agent.core.healing_orchestrator import HealingOrchestrator

def main():
    print("=== Self-Healing Agent Framework Verification ===")
    
    # 1. Configuration
    base_workspace = os.path.join(os.getcwd(), "workspaces")
    project_name = "test_project"
    writer = ProjectWriter(base_workspace)
    llm = OllamaService()
    
    # 2. Write project with intentionally broken requirements
    files = {
        "app.py": "import requests\nprint('App running successfully!')",
        "requirements.txt": "requests==2.25.1\ninvalid-package-name-123==9.9.9\n"
    }
    project_dir = writer.write_project(project_name, files)
    
    # 3. Setup Sandbox
    sandbox = SandboxService(project_dir)
    sandbox.setup_venv()
    
    # 4. Run Self-Healing Loop
    orchestrator = HealingOrchestrator(sandbox, llm)
    success = orchestrator.run_fix_loop("requirements.txt")
    
    if success:
        print("\n=== SUCCESS: Environment Restored ===")
        executor = CodeExecutor(sandbox)
        result = executor.execute("app.py")
        print(f"Final Output: {result['stdout'].strip()}")
    else:
        print("\n=== FAILURE: Could not heal environment ===")

if __name__ == "__main__":
    main()
