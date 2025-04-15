import re
import subprocess

# Get the commit message from the GITHUB_EVENT_PATH environment variable
commit_message = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode().strip()
# print(f"Commit message: {commit_message}")
# Use regular expressions to extract the module name from the commit message
match = re.search(r'\[[^\]]+\]([a-zA-Z0-9_]+):', commit_message)

if match:
    # print(f"Module name: {match.group(1)}")
    print(match.group(1))
