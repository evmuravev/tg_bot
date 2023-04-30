from typing import Optional
from enum import Enum

from models.core import DateTimeModelMixin, IDModelMixin, CoreModel


class ProfileStatus(str, Enum):
    new = "new"
    partially_completed = "partially_completed"
    completed = "completed"

    # NOT USED
    waiting_for_approval = "waiting_for_approval"
    rejected = "rejected"
    approved = "approved"


class ProfileBase(CoreModel):
    name: Optional[str]
    sex: Optional[str]
    age: Optional[int]
    age_tag: Optional[str]
    city: Optional[str]
    region: Optional[str]
    image: Optional[str]
    bio: Optional[str]
    status: Optional[ProfileStatus] = ProfileStatus.new


class ProfileCreate(CoreModel):
    """
    The only field required to create a profile is the users id
    """
    user_id: int
    status: Optional[ProfileStatus] = ProfileStatus.new


class ProfileUpdate(ProfileBase):
    """
    Allow users to update any or no fields, as long as it's not user_id
    """
    pass


class ProfileInDB(IDModelMixin, DateTimeModelMixin, ProfileBase):
    user_id: int


class ProfilePublic(ProfileInDB):
    pass
