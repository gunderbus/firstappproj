from dataclasses import dataclass, field
from typing import Optional

from playerbase.integrations import ghapi


@dataclass
class Player:
    username: str
    token: str
    _id: Optional[int] = None
    dispname: Optional[str] = field(default=None)
    score: int = 0

    def __post_init__(self) -> None:
        if self.dispname is None:
            self.dispname = ghapi.get_display_name(self.username, self.token)

    def add_to_score(self, points: int) -> None:
        self.score += points

    def get_commit(self, repo: str, commit_sha: str):
        return ghapi.get_commit(self.username, repo, commit_sha, self.token)
