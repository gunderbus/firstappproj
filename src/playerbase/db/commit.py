from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from playerbase.integrations import ghapi


@dataclass
class Commit:
    owner: str
    repo: str
    sha: str
    token: str = field(repr=False)
    _id: Optional[int] = None
    message: str = ""
    author_name: Optional[str] = None
    author_login: Optional[str] = None
    committed_at: Optional[str] = None
    html_url: Optional[str] = None
    additions: int = 0
    deletions: int = 0
    total_changes: int = 0
    changed_files: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.message:
            return

        payload = ghapi.get_commit(self.owner, self.repo, self.sha, self.token)
        hydrated_commit = self.from_api_payload(
            owner=self.owner,
            repo=self.repo,
            token=self.token,
            payload=payload,
            db_id=self._id,
        )

        self.message = hydrated_commit.message
        self.author_name = hydrated_commit.author_name
        self.author_login = hydrated_commit.author_login
        self.committed_at = hydrated_commit.committed_at
        self.html_url = hydrated_commit.html_url
        self.additions = hydrated_commit.additions
        self.deletions = hydrated_commit.deletions
        self.total_changes = hydrated_commit.total_changes
        self.changed_files = hydrated_commit.changed_files

    @classmethod
    def fetch(
        cls,
        owner: str,
        repo: str,
        sha: str,
        token: str,
        db_id: Optional[int] = None,
    ) -> "Commit":
        payload = ghapi.get_commit(owner, repo, sha, token)
        return cls.from_api_payload(
            owner=owner,
            repo=repo,
            token=token,
            payload=payload,
            db_id=db_id,
        )

    @classmethod
    def from_api_payload(
        cls,
        owner: str,
        repo: str,
        token: str,
        payload: Dict[str, Any],
        db_id: Optional[int] = None,
    ) -> "Commit":
        commit_data = payload.get("commit", {})
        author_data = commit_data.get("author", {})
        stats = payload.get("stats", {})
        files = payload.get("files", [])

        return cls(
            owner=owner,
            repo=repo,
            sha=payload.get("sha", ""),
            token=token,
            _id=db_id,
            message=commit_data.get("message", ""),
            author_name=author_data.get("name"),
            author_login=(payload.get("author") or {}).get("login"),
            committed_at=author_data.get("date"),
            html_url=payload.get("html_url"),
            additions=stats.get("additions", 0),
            deletions=stats.get("deletions", 0),
            total_changes=stats.get("total", 0),
            changed_files=[
                file_info["filename"]
                for file_info in files
                if "filename" in file_info
            ],
        )

    @property
    def short_sha(self) -> str:
        return self.sha[:7]

    def get_id(self) -> Optional[int]:
        return self._id

    def get_owner(self) -> str:
        return self.owner

    def get_repo(self) -> str:
        return self.repo

    def get_sha(self) -> str:
        return self.sha

    def get_short_sha(self) -> str:
        return self.short_sha

    def get_token(self) -> str:
        return self.token

    def get_message(self) -> str:
        return self.message

    def get_author_name(self) -> Optional[str]:
        return self.author_name

    def get_author_login(self) -> Optional[str]:
        return self.author_login

    def get_committed_at(self) -> Optional[str]:
        return self.committed_at

    def get_html_url(self) -> Optional[str]:
        return self.html_url

    def get_additions(self) -> int:
        return self.additions

    def get_deletions(self) -> int:
        return self.deletions

    def get_total_changes(self) -> int:
        return self.total_changes

    def get_changed_files(self) -> List[str]:
        return list(self.changed_files)

    def refresh(self) -> "Commit":
        refreshed = self.fetch(
            owner=self.owner,
            repo=self.repo,
            sha=self.sha,
            token=self.token,
            db_id=self._id,
        )
        self.message = refreshed.message
        self.author_name = refreshed.author_name
        self.author_login = refreshed.author_login
        self.committed_at = refreshed.committed_at
        self.html_url = refreshed.html_url
        self.additions = refreshed.additions
        self.deletions = refreshed.deletions
        self.total_changes = refreshed.total_changes
        self.changed_files = refreshed.changed_files
        return self
