import subprocess
import os

key = "sk-pro...PXQA"

# Set the variable
result = subprocess.run(
    ["railway.exe", "variable", "set", "--service", "reachgtm-backend", f"OPENAI_API_KEY={key}"],
    capture_output=True, text=True, timeout=15,
    shell=True  # Use shell to find the executable
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("CODE:", result.returncode)
