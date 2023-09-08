from enum import Enum
from typing import Optional

from models.core import DateTimeModelMixin, IDModelMixin, CoreModel
from models.profile import ProfilePublic


class ComplainStatus(str, Enum):
    approved = "approved"
    declined = "declined"
    new = "new"


class ComplainBase(CoreModel):
    complainant: int
    accused: int
    message_id: Optional[str]
    status: Optional[ComplainStatus] = ComplainStatus.new


class ComplainCreate(ComplainBase):
    complainant: int
    accused: int


class ComplainUpdate(IDModelMixin, ComplainBase):
    pass


class ComplainInDB(IDModelMixin, DateTimeModelMixin, ComplainBase):
    pass


class ComplainPublic(ComplainInDB):
    complainant_profile: Optional[ProfilePublic]
    accused_profile: Optional[ProfilePublic]
