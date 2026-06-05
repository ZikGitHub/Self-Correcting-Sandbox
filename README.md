# Self-Healing Agent Framework

A modular, LLM-powered framework for autonomous project writing and environment management.

## 🚀 Features
- **Project Writing:** Programmatic creation of directory structures and files.
- **Isolated Sandboxing:** Automated Python Virtual Environment (venv) provisioning.
- **Agentic Healing:** Local SLM (Qwen2.5-Coder) integration to fix dependency conflicts in real-time.
- **Verification Loop:** Automatic "Run -> Fix" state machine for resilient deployment.

## 📂 Structure
```text
self_healing_agent/
├── core/
│   └── healing_orchestrator.py # State machine logic
└── services/
    ├── project_writer.py    # File system management
    ├── sandbox_service.py   # Venv & execution
    ├── ollama_service.py    # LLM (Ollama) bridge
    └── code_executor.py     # Runtime analysis
main.py                      # Orchestration entry point
workspaces/                  # (Generated) Active project environments
```

## 🛠️ Usage
1. Ensure [Ollama](https://ollama.com/) is running with `qwen2.5-coder:1.5b`.
2. Run the main verification script:
   ```bash
   python main.py
   ```

## 🛡️ Safety
Executes all generated code inside isolated virtual environments, preventing host system pollution.
