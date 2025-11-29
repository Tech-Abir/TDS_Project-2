from google import genai
import subprocess
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
from google.genai import types

load_dotenv()

# IMPORTANT: pass API key here
client = genai.Client(api_key=os.getenv("AIPIPE_API_KEY"))

def strip_code_fences(code: str) -> str:
    code = code.strip()
    if code.startswith("```"):
        code = code.split("\n", 1)[1]
    if code.endswith("```"):
        code = code.rsplit("\n", 1)[0]
    return code.strip()

@tool
def run_code(code: str) -> dict:
    """
    Executes Python code safely inside a temporary file using UV.
    """
    try:
        filename = "runner.py"
        os.makedirs("LLMFiles", exist_ok=True)

        with open(os.path.join("LLMFiles", filename), "w") as f:
            f.write(code)

        proc = subprocess.Popen(
            ["uv", "run", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="LLMFiles"
        )
        stdout, stderr = proc.communicate()

        if len(stdout) >= 10000:
            stdout = stdout[:10000] + "...truncated due to large size"
        if len(stderr) >= 10000:
            stderr = stderr[:10000] + "...truncated due to large size"

        return {
            "stdout": stdout,
            "stderr": stderr,
            "return_code": proc.returncode
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }
