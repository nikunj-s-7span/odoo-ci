import sys
import re

# Get the commit message from the GITHUB_EVENT_PATH environment variable
commit_message = sys.stdin.read()

print(f"Module name: {commit_message}")

# Use regular expressions to extract the module name from the commit message
module_name = re.search(r'\[[^\]]+\]([a-zA-Z0-9_]+):', commit_message).group(1)

print(f"Module name: {module_name}")