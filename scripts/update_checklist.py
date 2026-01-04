import os

import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "canstralian/CodeTuneStudio"
CHECKLIST_PATH = "PR_REVIEW_CHECKLIST.md"

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# Fetch PRs
response = requests.get(
    f"https://api.github.com/repos/{REPO}/pulls?state=closed", headers=headers
)
response.raise_for_status()
prs = response.json()

# Open checklist file
try:
    with open(CHECKLIST_PATH) as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"Error: Checklist file '{CHECKLIST_PATH}' not found.")
    exit(1)
except OSError as e:
    print(f"Error reading checklist file '{CHECKLIST_PATH}': {e}")
    exit(1)
# Update checklist for merged PRs
for i, line in enumerate(lines):
    for pr in prs:
        if f"PR #{pr['number']}" in line and pr["merged_at"]:
            lines[i] = line.replace("[ ]", "[x]")

# Write updated checklist
try:
    with open(CHECKLIST_PATH, "w") as f:
        f.writelines(lines)
except OSError as e:
    print(f"Error writing to {CHECKLIST_PATH}: {e}")
