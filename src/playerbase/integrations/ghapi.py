from pathlib import Path
import os
import subprocess
from typing import Any, Dict, List

import requests


def _github_headers(token: str) -> Dict[str, str]:
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

def get_display_name(username: str, token: str) -> str:
    url = f"https://api.github.com/users/{username}"
    try:
        response = requests.get(url, headers=_github_headers(token), timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Unable to get display name for GitHub user {username}."
        ) from exc

    data = response.json()
    return data.get("name") or data.get("login") or username


def get_repo_payload(owner: str, repo: str, token: str) -> Dict[str, Any]:
    url = f"https://api.github.com/repos/{owner}/{repo}"

    try:
        response = requests.get(url, headers=_github_headers(token), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Unable to access GitHub repo {owner}/{repo}. Check the repo name and token."
        ) from exc


def get_repo(owner: str, repo: str, token: str):
    from playerbase.db.repo import Repo

    payload = get_repo_payload(owner, repo, token)
    return Repo.from_api_payload(
        owner=owner,
        name=repo,
        token=token,
        payload=payload,
    )


def get_commit_payload(owner: str, repo: str, commit_sha: str, token: str) -> Dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"

    try:
        response = requests.get(url, headers=_github_headers(token), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Unable to access commit {commit_sha} for {owner}/{repo}."
        ) from exc

def get_commit(owner: str, repo: str, commit_sha: str, token: str):
    from playerbase.db.commit import Commit

    payload = get_commit_payload(owner, repo, commit_sha, token)
    return Commit.from_api_payload(
        owner=owner,
        repo=repo,
        token=token,
        payload=payload,
    )


def commit_list(owner: str, repo: str, token: str) -> List[Dict]:
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    try:
        response = requests.get(url, headers=_github_headers(token), timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Unable to list commits for {owner}/{repo}.") from exc


def clone_repo_to_path(owner: str, repo: str, token: str, path: str) -> Path:
    destination = Path(path).expanduser().resolve()
    clone_url = f"https://github.com/{owner}/{repo}.git"

    if destination.exists() and not destination.is_dir():
        raise ValueError(f"Destination exists but is not a directory: {destination}")

    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Destination already exists and is not empty: {destination}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "http.extraHeader"
    env["GIT_CONFIG_VALUE_0"] = f"Authorization: Bearer {token}"

    try:
        subprocess.run(
            ["git", "clone", clone_url, str(destination)],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("`git` is not installed or not available on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"Failed to clone {owner}/{repo} into {destination}: {exc.stderr.strip()}"
        ) from exc

    return destination
