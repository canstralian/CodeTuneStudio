import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "canstralian/CodeTuneStudio"
CHECKLIST_PATH = "PR_REVIEW_CHECKLIST.md"

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# Fetch PRs
response = requests.get(f"https://api.github.com/repos/{REPO}/pulls?state=closed", headers=headers)
response.raise_for_status()
prs = response.json()

# Open checklist file
with open(CHECKLIST_PATH, "r") as f:
    lines = f.readlines()

# Update checklist for merged PRs
for i, line in enumerate(lines):
    for pr in prs:
        if f"PR #{pr['number']}" in line and pr["merged_at"]:
            lines[i] = line.replace("[ ]", "[x]")

# Write updated checklist
with open(CHECKLIST_PATH, "w") as f:
    f.writelines(lines)
