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
    rank: str = "Rookie"

    def __post_init__(self) -> None:
        if self.dispname is None:
            self.dispname = ghapi.get_display_name(self.username, self.token)
    
    def __init__(self, 
    username: str, 
    token: str, 
    db_id: Optional[int] = None):
        self.username = username
        self.token = token
        self._id = db_id

    @classmethod
    def from_github(cls, username: str, token: str, db_id: Optional[int] = None) -> "Player":
        return cls(username=username, token=token, _id=db_id)

    def get_id(self) -> Optional[int]:
        return self._id

    def get_username(self) -> str:
        return self.username

    def get_token(self) -> str:
        return self.token

    def get_display_name(self) -> str:
        return self.dispname or self.username

    def set_display_name(self, display_name: str) -> None:
        if display_name:
            self.dispname = display_name

    def refresh_display_name(self) -> str:
        self.dispname = ghapi.get_display_name(self.username, self.token)
        return self.dispname

    def get_score(self) -> int:
        return self.score

    def add_to_score(self, points: int) -> None:
        self.score += points

    def get_commit(self, repo: str, commit_sha: str):
        return ghapi.get_commit(self.username, repo, commit_sha, self.token)

    def get_rank(self) -> str:
        return self.rank

    def set_rank(self, ranking: str) -> None:
        if ranking and ranking.strip():
            self.rank = ranking
