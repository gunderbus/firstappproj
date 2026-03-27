import requests

def get_repo(owner: str, repo: str, token: str) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()

def get_commit(repo: dict, commit_id: str) -> dict:
     # work here