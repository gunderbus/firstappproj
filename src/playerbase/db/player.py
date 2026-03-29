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

    def add_to_score(self, points: int) -> None:
        self.score += points

    def get_commit(self, repo: str, commit_sha: str):
        try:
            return ghapi.get_commit(self.username, repo, commit_sha, self.token)
        except:
            print("interesting")
            return 0
    
    def get_rank(self) -> str:
        try:
            return self.rank
        except:
            print("uhhhhhhhhhhhhhhh")
            return "vro ts aint a rank"
    
    def set_rank(self, ranking: str) -> None:
        if(ranking != " " or ranking != "" or ranking != None):
            self.rank = ranking
        else:
            print("Brotien shake YOU NEED TO ENTER TS")
