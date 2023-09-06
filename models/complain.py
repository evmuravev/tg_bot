from typing import Optional

from models.core import DateTimeModelMixin, IDModelMixin, CoreModel
from models.profile import ProfilePublic


class ComplainBase(CoreModel):
    complainant: int
    accused: int
    message_id: Optional[str]


class ComplainCreate(ComplainBase):
    complainant: int
    accused: int


class ComplainUpdate(ComplainBase):
    pass


class ComplainInDB(IDModelMixin, DateTimeModelMixin, ComplainBase):
    pass


class ComplainPublic(ComplainInDB):
    complainant_profile: Optional[ProfilePublic]
    accused_profile: Optional[ProfilePublic]
