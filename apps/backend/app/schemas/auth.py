from uuid import UUID

from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=6, max_length=128)


class UserLoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class UserProfile(BaseModel):
    id: UUID
    username: str
    email: str | None = None
    status: str


class AdminProfile(BaseModel):
    id: UUID
    username: str
    display_name: str
    status: str


class TokenPayload(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLoginData(TokenPayload):
    user: UserProfile


class AdminLoginData(TokenPayload):
    admin: AdminProfile
