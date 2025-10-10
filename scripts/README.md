# Scripts Directory

This directory contains automation scripts for the CodeTuneStudio repository.

## update_checklist.py

Automatically updates the PR review checklist by fetching merged PRs from GitHub and marking them as completed.

### Requirements

- Python 3.10+
- python-dotenv
- requests

### Setup

1. Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```

2. Add your GitHub personal access token to `.env`:
   ```
   GITHUB_TOKEN=your_github_token_here
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

Run the script manually:
```bash
python scripts/update_checklist.py
```

Or let the GitHub Actions workflow run it automatically (configured in `.github/workflows/auto-update-checklist.yml`).

### Security

- **Never commit your `.env` file** - it's already in `.gitignore`
- The script uses `python-dotenv` to securely load credentials from environment variables
- Proper error handling ensures the script fails gracefully if credentials are missing
- All functions follow PEP 8 standards with comprehensive docstrings

### Testing

Run the test suite:
```bash
python -m unittest tests.test_update_checklist -v
```

### How It Works

1. Loads environment variables from `.env` file using `python-dotenv`
2. Validates that `GITHUB_TOKEN` is set and not empty
3. Fetches closed PRs from the GitHub API
4. Reads the `PR_REVIEW_CHECKLIST.md` file
5. Updates lines containing PR numbers that have been merged
6. Writes the updated checklist back to the file

### Error Handling

The script includes comprehensive error handling for:
- Missing or empty `GITHUB_TOKEN`
- GitHub API failures
- File read/write errors
- Network timeouts

All errors result in clear error messages and proper exit codes.
