#!/usr/bin/env python3
"""Close stale GitHub issues older than a cutoff until max-open target is reached."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

GITHUB_API = "https://api.github.com"


def parse_repo(repo: str) -> tuple[str, str]:
    if "/" not in repo:
        raise ValueError("Repository must be in owner/name format")
    owner, name = repo.split("/", 1)
    return owner, name


def api_request(url: str, token: str | None, method: str = "GET", body: dict[str, Any] | None = None) -> Any:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "codex-triage-script"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, headers=headers, method=method, data=data)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def list_open_issues(token: str | None, owner: str, repo: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    page = 1
    while True:
        query = urllib.parse.urlencode({"state": "open", "per_page": 100, "page": page, "sort": "updated", "direction": "asc"})
        url = f"{GITHUB_API}/repos/{owner}/{repo}/issues?{query}"
        batch_raw = api_request(url, token)
        batch = [i for i in batch_raw if "pull_request" not in i]
        if not batch:
            break
        issues.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return issues


def close_issue(token: str | None, owner: str, repo: str, number: int, reason: str) -> None:
    url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{number}"
    api_request(url, token, method="PATCH", body={"state": "closed", "state_reason": reason})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="canstralian/CodeTuneStudio")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--max-open", type=int, default=20)
    parser.add_argument("--state-reason", default="not_planned", choices=["completed", "not_planned", "reopened"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    owner, repo = parse_repo(args.repo)
    all_open = list_open_issues(token, owner, repo)

    now = dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(days=args.days)
    stale = []
    for issue in all_open:
        updated = dt.datetime.fromisoformat(issue["updated_at"].replace("Z", "+00:00"))
        if updated < cutoff:
            stale.append(issue)

    need_to_close = max(0, len(all_open) - args.max_open)
    candidates = stale[:need_to_close]

    print(f"Open issues: {len(all_open)}")
    print(f"Stale candidates (>{args.days} days inactivity): {len(stale)}")
    print(f"Need to close to reach <= {args.max_open}: {need_to_close}")

    if not candidates:
        print("No issues selected for closure.")
        return 0

    for i in candidates:
        print(f"#{i['number']} updated {i['updated_at']} - {i['title']}")
        if not args.dry_run:
            close_issue(token, owner, repo, i["number"], args.state_reason)

    print("Dry run complete. No issues were closed." if args.dry_run else f"Closed {len(candidates)} issues.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        print(f"GitHub API error: HTTP {exc.code}: {payload}", file=sys.stderr)
        raise
