import subprocess
from pathlib import Path

LLAMA_CLI = Path(__file__).resolve().parents[2] / "tools" / "llama.cpp" / "llama-cli.exe"
MODEL = "lm-kit/gemma-3-270m-instruct-gguf:Q4_K_M"

def generate_text(prompt: str, max_tokens: int = 20) -> str:
    result = subprocess.run(
        [
            str(LLAMA_CLI),
            "-hf",
            MODEL,
            "-p",
            prompt,
            "-n",
            str(max_tokens),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return result.stdout.strip()