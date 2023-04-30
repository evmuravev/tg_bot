from typing import Optional

from models.core import DateTimeModelMixin, IDModelMixin, CoreModel
from models.profile import ProfilePublic


class UserBase(CoreModel):
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    language_code: str
    is_bot: bool
    link: Optional[str]
    is_premium: Optional[bool]


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    id: int
    username: str


class UserInDB(DateTimeModelMixin, UserBase):
    pass


class UserPublic(IDModelMixin, DateTimeModelMixin, UserBase):
    profile: Optional[ProfilePublic]
