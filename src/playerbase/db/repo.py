from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from playerbase.integrations import ghapi


@dataclass
class Repo:
    owner: str
    name: str
    token: str = field(repr=False)
    _id: Optional[int] = None
    full_name: Optional[str] = None
    description: Optional[str] = None
    html_url: Optional[str] = None
    default_branch: Optional[str] = None
    language: Optional[str] = None
    visibility: Optional[str] = None
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0

    def __post_init__(self) -> None:
        if self.full_name is not None:
            return

        payload = ghapi.get_repo(self.owner, self.name, self.token)
        hydrated_repo = self.from_api_payload(
            owner=self.owner,
            name=self.name,
            token=self.token,
            payload=payload,
            db_id=self._id,
        )

        self.full_name = hydrated_repo.full_name
        self.description = hydrated_repo.description
        self.html_url = hydrated_repo.html_url
        self.default_branch = hydrated_repo.default_branch
        self.language = hydrated_repo.language
        self.visibility = hydrated_repo.visibility
        self.stargazers_count = hydrated_repo.stargazers_count
        self.forks_count = hydrated_repo.forks_count
        self.open_issues_count = hydrated_repo.open_issues_count

    @classmethod
    def from_api_payload(
        cls,
        owner: str,
        name: str,
        token: str,
        payload: Dict[str, Any],
        db_id: Optional[int] = None,
    ) -> "Repo":
        return cls(
            owner=owner,
            name=payload.get("name", name),
            token=token,
            _id=db_id,
            full_name=payload.get("full_name"),
            description=payload.get("description"),
            html_url=payload.get("html_url"),
            default_branch=payload.get("default_branch"),
            language=payload.get("language"),
            visibility=payload.get("visibility"),
            stargazers_count=payload.get("stargazers_count", 0),
            forks_count=payload.get("forks_count", 0),
            open_issues_count=payload.get("open_issues_count", 0),
        )

    def get_id(self) -> Optional[int]:
        return self._id

    def get_owner(self) -> str:
        return self.owner

    def get_name(self) -> str:
        return self.name

    def get_token(self) -> str:
        return self.token

    def get_full_name(self) -> Optional[str]:
        return self.full_name

    def get_description(self) -> Optional[str]:
        return self.description

    def get_html_url(self) -> Optional[str]:
        return self.html_url

    def get_default_branch(self) -> Optional[str]:
        return self.default_branch

    def get_language(self) -> Optional[str]:
        return self.language

    def get_visibility(self) -> Optional[str]:
        return self.visibility

    def get_stargazers_count(self) -> int:
        return self.stargazers_count

    def get_forks_count(self) -> int:
        return self.forks_count

    def get_open_issues_count(self) -> int:
        return self.open_issues_count


repo = Repo
