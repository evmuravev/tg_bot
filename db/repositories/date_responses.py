from typing import List
from databases import Database
from db.repositories.base import BaseRepository
from db.repositories.profiles import ProfilesRepository
from models.date_response import DateResponseCreate, DateResponsePublic, DateResponseInDB


CREATE_DATE_RESPONSE = """
    INSERT INTO date_responses (inviter, responder, message_id)
    VALUES (:inviter, :responder, :message_id)
    RETURNING *;
"""


GET_DATE_RESPONSES_BY_RESPONDER_QUERY = """
    SELECT *
    FROM date_responses
    WHERE responder = :responder
        AND message_id = :message_id

    ;
"""

UPDATE_DATE_RESPONSE_QUERY = '''
    UPDATE date_responses
    SET "is_clicked_through" = TRUE,
    WHERE
        inviter  = :inviter_id
        responder  = :responder_id
        message_id  = :message_id
    RETURNING *;
'''


class DateResponseRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.profiles_repo = ProfilesRepository(db)

    async def create_date_response(
            self, *,
            date_response_create: DateResponseCreate
    ) -> DateResponseInDB:

        created_date_response = await self.db.fetch_one(
            query=CREATE_DATE_RESPONSE,
            values=date_response_create.dict()
        )

        return created_date_response

    async def get_date_responses_by_responder(
            self, *,
            responder: int,
            message_id: str,
            populate: bool = True
    ) -> List[DateResponseInDB]:
        date_response_record = await self.db.fetch_one(
            query=GET_DATE_RESPONSES_BY_RESPONDER_QUERY,
            values={
                "responder": responder,
                "message_id": message_id
            }
        )

        if date_response_record:
            date_response = DateResponseInDB(**date_response_record)
            if populate:
                return await self.populate_date_response(date_response=date_response)
            return date_response

    async def populate_date_response(self, *, date_response: DateResponseInDB) -> DateResponsePublic:
        return DateResponsePublic(
            **date_response.dict(),
            # fetch the user's profile from the profiles repo
            inviter_profile=await self.profiles_repo.get_profile_by_id(
                id=date_response.inviter
            ),
            responder_profile=await self.profiles_repo.get_profile_by_id(
                id=date_response.responder
            )
        )

    async def set_is_clicked_through(
        self, *,
        inviter_id: int,
        responder_id: int,
        message_id: str,
    ) -> DateResponseInDB:

        updated_date_response = await self.db.fetch_one(
            query=UPDATE_DATE_RESPONSE_QUERY,
            values={
                "inviter_id": inviter_id,
                "responder_id": responder_id,
                "message_id": message_id,
            },
        )

        return DateResponseInDB(**updated_date_response)
