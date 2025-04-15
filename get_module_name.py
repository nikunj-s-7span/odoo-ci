import re
import subprocess

# Get the commit message from the GITHUB_EVENT_PATH environment variable
commit_message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode().strip()

print(f"Module name: {commit_message}")

# Use regular expressions to extract the module name from the commit message
module_name = re.search(r'\[[^\]]+\]([a-zA-Z0-9_]+):', commit_message).group(1)

print(f"Module name: {module_name}")
