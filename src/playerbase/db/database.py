from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from playerbase.db.commit import Commit
from playerbase.db.player import Player
from playerbase.db.repo import Repo


class DatabaseService(ABC):
    @abstractmethod
    def append_to_playerlist(self, player: Player) -> Player:
        """Store a player record."""

    @abstractmethod
    def get_playerlist(self) -> List[Player]:
        """Return every stored player."""

    @abstractmethod
    def get_player_by_username(self, username: str) -> Optional[Player]:
        """Return one player by username."""

    @abstractmethod
    def append_to_repolist(self, repo: Repo) -> Repo:
        """Store a repo record."""

    @abstractmethod
    def get_repolist(self) -> List[Repo]:
        """Return every stored repo."""

    @abstractmethod
    def get_repo_by_full_name(self, full_name: str) -> Optional[Repo]:
        """Return one repo by full repo name."""

    @abstractmethod
    def append_to_commitlist(self, commit: Commit) -> Commit:
        """Store a commit record."""

    @abstractmethod
    def get_commitlist(self) -> List[Commit]:
        """Return every stored commit."""

    @abstractmethod
    def get_commit_by_sha(self, sha: str) -> Optional[Commit]:
        """Return one commit by sha."""


class InMemoryDatabaseService(DatabaseService):
    def __init__(self) -> None:
        self._players: Dict[str, Player] = {}
        self._repos: Dict[str, Repo] = {}
        self._commits: Dict[Tuple[str, str], Commit] = {}

    def append_to_playerlist(self, player: Player) -> Player:
        self._players[player.get_username()] = player
        return player

    def get_playerlist(self) -> List[Player]:
        return list(self._players.values())

    def get_player_by_username(self, username: str) -> Optional[Player]:
        return self._players.get(username)

    def append_to_repolist(self, repo: Repo) -> Repo:
        repo_key = repo.get_full_name() or f"{repo.get_owner()}/{repo.get_name()}"
        self._repos[repo_key] = repo
        return repo

    def get_repolist(self) -> List[Repo]:
        return list(self._repos.values())

    def get_repo_by_full_name(self, full_name: str) -> Optional[Repo]:
        return self._repos.get(full_name)

    def append_to_commitlist(self, commit: Commit) -> Commit:
        commit_key = (commit.get_repo(), commit.get_sha())
        self._commits[commit_key] = commit
        return commit

    def get_commitlist(self) -> List[Commit]:
        return list(self._commits.values())

    def get_commit_by_sha(self, sha: str) -> Optional[Commit]:
        for commit in self._commits.values():
            if commit.get_sha() == sha:
                return commit
        return None
