from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


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
        #"""Create a new user account and return the authenticated session."""

    @abstractmethod
    def login(self, request: LoginRequest) -> AuthResult:
        #"""Authenticate a user and return user info plus issued tokens."""

    @abstractmethod
    def logout(self, access_token: str) -> None:
        #"""Invalidate an existing authenticated session."""

    @abstractmethod
    def refresh_session(self, refresh_token: str) -> AuthTokens:
        #"""Issue fresh tokens for a valid refresh token."""

    @abstractmethod
    def validate_access_token(self, access_token: str) -> AuthenticatedUser:
        #"""Resolve and return the authenticated user for a valid access token."""

    @abstractmethod
    def get_current_user(self, access_token: str) -> AuthenticatedUser:
        #"""Return the currently authenticated user for the provided session."""

# class MockAuthService(AuthService):
#     from playerbase.db.player import Player

#     PlayerList: Player = []

#     def register(self, request: RegisterRequets) -> AuthResult:
#         # this is the beninging
#         dole = request

#         # Append dole which will be instatiated into PlayerList and then give a token to playerlist
        