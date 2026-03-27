import requests

def get_repo(owner: str, repo: str, token: str) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        print("Unable to access github to get the repo, check code and token.")

def get_commit(repo: dict, commit_id: str) -> dict:
     # work here    