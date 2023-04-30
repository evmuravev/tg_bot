from typing import Optional

from models.core import DateTimeModelMixin, IDModelMixin, CoreModel
from models.profile import ProfilePublic


class DateOfferBase(CoreModel):
    where: Optional[str]
    when: Optional[str]
    expectations: Optional[str]
    bill_splitting: Optional[str]
    message_id: Optional[str]


class DateOfferCreate(CoreModel):
    profile_id: int


class DateOfferUpdate(DateOfferBase):
    pass


class DateOfferInDB(IDModelMixin, DateTimeModelMixin, DateOfferBase):
    profile_id: int


class DateOfferPublic(DateOfferInDB):
    profile: Optional[ProfilePublic]
