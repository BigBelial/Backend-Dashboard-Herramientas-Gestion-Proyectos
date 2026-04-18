from dataclasses import dataclass


@dataclass
class RegisterDTO:
    email: str
    password: str


@dataclass
class LoginDTO:
    email: str
    password: str


@dataclass
class TokenDTO:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@dataclass
class RefreshTokenDTO:
    refresh_token: str


@dataclass
class LogoutDTO:
    access_token: str
