from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from playerbase.db.database import DatabaseService, InMemoryDatabaseService
from playerbase.db.player import Player


@dataclass(frozen=True)
class LoginRequest:
    username: str
    password: str


@dataclass(frozen=True)
class RegisterRequest:
    username: str
    password: str
    email: Optional[str] = None


@dataclass(frozen=True)
class AuthTokens:
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    username: str
    display_name: Optional[str] = None


@dataclass(frozen=True)
class AuthResult:
    user: AuthenticatedUser
    tokens: AuthTokens


class AuthService(ABC):
    @abstractmethod
    def register(self, request: RegisterRequest) -> AuthResult:
        """Create a new user account and return the authenticated session."""

    @abstractmethod
    def login(self, request: LoginRequest) -> AuthResult:
        """Authenticate a user and return user info plus issued tokens."""

    @abstractmethod
    def logout(self, access_token: str) -> None:
        """Invalidate an existing authenticated session."""

    @abstractmethod
    def refresh_session(self, refresh_token: str) -> AuthTokens:
        """Issue fresh tokens for a valid refresh token."""

    @abstractmethod
    def validate_access_token(self, access_token: str) -> AuthenticatedUser:
        """Resolve and return the authenticated user for a valid access token."""

    @abstractmethod
    def get_current_user(self, access_token: str) -> AuthenticatedUser:
        """Return the currently authenticated user for the provided session."""


class MockAuthService(AuthService):
    def __init__(self, database: Optional[DatabaseService] = None) -> None:
        self.database = database or InMemoryDatabaseService()

    def register(self, request: RegisterRequest) -> AuthResult:
        existing_player = self.database.get_player_by_username(request.username)
        if existing_player is not None:
            raise ValueError(f"Username already exists: {request.username}")

        access_token = f"mock-access-{uuid4().hex}"
        refresh_token = f"mock-refresh-{uuid4().hex}"
        player_id = len(self.database.get_playerlist()) + 1

        player = Player(
            username=request.username,
            password=request.password,
            token=access_token,
            db_id=player_id,
            dispname=request.username,
        )
        player.set_display_name(request.username)
        self.database.append_to_playerlist(player)

        return AuthResult(
            user=AuthenticatedUser(
                user_id=str(player.get_id()),
                username=player.get_username(),
                display_name=player.get_display_name(),
            ),
            tokens=AuthTokens(
                access_token=access_token,
                refresh_token=refresh_token,
            ),
        )

    def login(self, request: LoginRequest) -> AuthResult:
        access_token = f"mock-access-{uuid4().hex}"
        refresh_token = f"mock-refresh-{uuid4().hex}"
        player = self.database.get_player_by_username(request.username)
        if player is None:
            raise ValueError(f"Player does not exist: {request.username}")

        if player.get_password() != request.password:
            raise ValueError("The entered username or password is not correct.")

        player.set_token(access_token)

        return AuthResult(
            user=AuthenticatedUser(
                user_id=str(player.get_id()),
                username=player.get_username(),
                display_name=player.get_display_name(),
            ),
            tokens=AuthTokens(
                access_token=access_token,
                refresh_token=refresh_token,
            ),
        )


    def logout(self, access_token: str) -> None:
        raise NotImplementedError("MockAuthService.logout is not implemented yet.")

    def refresh_session(self, refresh_token: str) -> AuthTokens:
        raise NotImplementedError("MockAuthService.refresh_session is not implemented yet.")

    def validate_access_token(self, access_token: str) -> AuthenticatedUser:
        raise NotImplementedError(
            "MockAuthService.validate_access_token is not implemented yet."
        )

    def get_current_user(self, access_token: str) -> AuthenticatedUser:
        raise NotImplementedError(
            "MockAuthService.get_current_user is not implemented yet."
        )
