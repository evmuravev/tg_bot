from typing import Optional

from models.core import DateTimeModelMixin, CoreModel
from models.profile import ProfilePublic


class DateResponseBase(CoreModel):
    inviter: int
    responder: int
    message_id: str
    is_clicked_through: Optional[bool] = False


class DateResponseCreate(DateResponseBase):
    pass


class DateResponseUpdate(DateResponseBase):
    pass


class DateResponseInDB(DateTimeModelMixin, DateResponseBase):
    pass


class DateResponsePublic(DateResponseInDB):
    inviter_profile: Optional[ProfilePublic]
    responder_profile: Optional[ProfilePublic]
