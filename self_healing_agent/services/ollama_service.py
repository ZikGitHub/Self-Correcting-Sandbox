import requests
import json
from typing import Optional

class OllamaService:
    """Manages API connections to local Ollama service."""
    
    def __init__(self, model: str = "qwen2.5-coder:1.5b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.api_url = f"{base_url}/api/generate"

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        if system:
            payload["system"] = system

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            return json.dumps({"error": str(e)})

    def fix_requirements(self, requirements_content: str, error_log: str) -> str:
        system_prompt = (
            "You are a Python dependency expert. Your job is to fix the requirements.txt file based on the error log. "
            "If a package does not exist, REMOVE it. If there is a version conflict, change the version. "
            "Return a JSON object: {\"requirements\": \"your fixed requirements here\"}"
        )
        prompt = f"### Current Requirements:\n{requirements_content}\n\n### Error Log:\n{error_log}\n\n### Task:\nFix the requirements. Provide the JSON output."
        
        response_text = self.generate(prompt, system=system_prompt)
        print(f"[*] Raw LLM Response: {response_text}")
        try:
            data = json.loads(response_text)
            return data.get("requirements", requirements_content)
        except:
            # Try a simple regex or string split if JSON fails
            if '"requirements":' in response_text:
                try:
                    # Very crude extraction
                    part = response_text.split('"requirements":')[1]
                    # handle both start and end quotes
                    return part.strip().strip('"').strip("'").strip('}').strip()
                except:
                    pass
            return requirements_content
