import os
import time
import requests
import pandas as pd
from datetime import datetime

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

REPOS = ["fastapi/fastapi", "langchain-ai/langchain", "vercel/next.js", "microsoft/vscode"]
LLM_KEYWORDS = ["gpt", "chatgpt", "llm", "gemini", "copilot", "ai-assisted", "openai"]

def parse_iso(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None

def fetch_pr_timeline(owner, repo, pr_number):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/timeline"
    resp = requests.get(url, headers={**HEADERS, "Accept": "application/vnd.github.mockingbird-preview+json"})
    return resp.json() if resp.status_code == 200 else []

def extract_pr_metrics(repo_full, limit=30):
    owner, repo = repo_full.split("/")
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed&per_page={limit}"
    prs = requests.get(url, headers=HEADERS).json()
    records = []
    for pr in prs:
        if not pr.get("merged_at"):
            continue
        title = pr.get("title", "")
        body = pr.get("body") or ""
        text_combined = f"{title} {body}".lower()
        is_llm = int(any(kw in text_combined for kw in LLM_KEYWORDS))
        
        created_at = parse_iso(pr["created_at"])
        merged_at = parse_iso(pr["merged_at"])
        total_hrs = round((merged_at - created_at).total_seconds() / 3600.0, 2)
        
        records.append({
            "pr_id": pr["number"],
            "repo_name": repo_full,
            "pr_title": title,
            "pr_body_comment": body[:500],
            "is_llm_assisted": is_llm,
            "time_to_merge_hrs": total_hrs
        })
    return records

if __name__ == "__main__":
    all_data = []
    for r in REPOS:
        all_data.extend(extract_pr_metrics(r, limit=30))
    pd.DataFrame(all_data).to_csv("raw_github_prs.csv", index=False)
    print(f"Collected {len(all_data)} merged PRs.")
