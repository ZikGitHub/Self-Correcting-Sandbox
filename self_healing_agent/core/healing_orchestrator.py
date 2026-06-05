import os
from ..services.sandbox_service import SandboxService
from ..services.ollama_service import OllamaService

class HealingOrchestrator:
    """Operates the Run -> Fix circuit loop using local LLM."""
    
    def __init__(self, sandbox: SandboxService, llm: OllamaService, max_retries: int = 3):
        self.sandbox = sandbox
        self.llm = llm
        self.max_retries = max_retries

    def run_fix_loop(self, requirements_filename: str = "requirements.txt") -> bool:
        requirements_path = os.path.join(self.sandbox.project_dir, requirements_filename)
        
        for attempt in range(1, self.max_retries + 1):
            print(f"\n[*] Attempt {attempt}: Provisioning environment...")
            result = self.sandbox.execute(["python", "-m", "pip", "install", "-r", requirements_filename])
            
            if result["returncode"] == 0:
                print("[+] Environment successfully provisioned.")
                return True
            
            print(f"[-] Provisioning failed on attempt {attempt}.")
            
            if not os.path.exists(requirements_path):
                print(f"[-] {requirements_filename} not found at {requirements_path}")
                return False

            with open(requirements_path, "r") as f:
                old_reqs = f.read()
            
            print("[*] Analyzing error with LLM...")
            new_reqs = self.llm.fix_requirements(old_reqs, result["stderr"])
            
            if isinstance(new_reqs, list):
                new_reqs = "\n".join(new_reqs)
            
            print(f"[*] Suggested Requirements:\n{new_reqs}")
            
            with open(requirements_path, "w") as f:
                f.write(str(new_reqs))
            
            print("[+] Updated requirements. Retrying...")

        print("\n[!] Circuit Breaker triggered: Maximum retries reached.")
        self._generate_failure_report(result["stderr"])
        return False

    def _generate_failure_report(self, last_error: str):
        report_path = os.path.join(self.sandbox.project_dir, "TROUBLESHOOTING.md")
        report_content = f"# Troubleshooting Report\n\nFailed to compile within {self.max_retries} loops.\n\n### Last Error\n```text\n{last_error}\n```"
        with open(report_path, "w") as f:
            f.write(report_content)
        print(f"[!] Report generated at {report_path}")
