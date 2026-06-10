import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Ensure the framework is in the python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from self_healing_agent.services.sandbox_service import SandboxService
from self_healing_agent.services.ollama_service import OllamaService
from self_healing_agent.core.healing_orchestrator import HealingOrchestrator
from self_healing_agent.services.code_executor import CodeExecutor

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SandboxRequest(BaseModel):
    project_path: str

@app.post("/setup")
async def setup_sandbox(request: SandboxRequest):
    if not os.path.exists(request.project_path):
        raise HTTPException(status_code=404, detail=f"Project path not found: {request.project_path}")
    
    sandbox = SandboxService(request.project_path)
    try:
        venv_path = sandbox.setup_venv()
        return {"status": "success", "venv_path": venv_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-healing")
async def run_healing(request: SandboxRequest):
    if not os.path.exists(request.project_path):
        raise HTTPException(status_code=404, detail="Project path not found")
    
    sandbox = SandboxService(request.project_path)
    # Use localhost if not in Docker
    ollama_url = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
    llm = OllamaService(base_url=ollama_url)
    orchestrator = HealingOrchestrator(sandbox, llm)
    
    try:
        # Check if requirements.txt exists (look root first, then recursive)
        req_path = os.path.join(request.project_path, "requirements.txt")
        req_name = "requirements.txt"
        
        if not os.path.exists(req_path):
            # Recursive search for requirements.txt
            found = False
            for root, dirs, files in os.walk(request.project_path):
                if "requirements.txt" in files:
                    req_path = os.path.join(root, "requirements.txt")
                    # Make it relative to project path for the orchestrator
                    req_name = os.path.relpath(req_path, request.project_path)
                    found = True
                    break
            if not found:
                return {"status": "skipped", "message": "No requirements.txt found"}
            
        success = orchestrator.run_fix_loop(req_name)
        return {"status": "success" if success else "failure", "healed": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test")
async def test_project(request: SandboxRequest):
    if not os.path.exists(request.project_path):
        raise HTTPException(status_code=404, detail="Project path not found")
    
    sandbox = SandboxService(request.project_path)
    executor = CodeExecutor(sandbox)
    
    # Target files to try running
    targets = ["app.py", "main.py"]
    target_file = None
    
    for t in targets:
        if os.path.exists(os.path.join(request.project_path, t)):
            target_file = t
            break
            
    if not target_file:
        # Recursive search for common entry points
        for root, dirs, files in os.walk(request.project_path):
            if ".venv" in root or "__pycache__" in root:
                continue
            for t in ["main.py", "app.py"]:
                if t in files:
                    target_file = os.path.relpath(os.path.join(root, t), request.project_path)
                    break
            if target_file: break

    if not target_file:
        # Look for any .py file (recursive, ignoring hidden/venv)
        py_files = []
        for root, dirs, files in os.walk(request.project_path):
            if ".venv" in root or "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".py") and not f.startswith("__"):
                    py_files.append(os.path.relpath(os.path.join(root, f), request.project_path))
        
        if py_files:
            # Prefer files not in 'tests' directory
            non_test_files = [f for f in py_files if "test" not in f.lower()]
            target_file = non_test_files[0] if non_test_files else py_files[0]
        else:
            return {"status": "error", "message": "No python files found to run"}

    try:
        result = executor.execute(target_file)
        return {"status": "success", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
