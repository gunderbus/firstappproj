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

def get_commit(owner: str, repo: str, commit_sha: str, token: str) -> dict:
     # work here    

    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }
    
    parker = requests.get(url, headers=headers, timeout=10)
    parker.raise_for_status()
    return parker.json()

def commit_list(owner: str, repo: str, token: str) -> dict:

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
    }

    kanye = requests.get(url, headers=headers, timeout=10)
    kanye.raise_for_status()
    return kanye.json()

