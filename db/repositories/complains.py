from typing import List
from databases import Database
from db.repositories.base import BaseRepository
from db.repositories.profiles import ProfilesRepository
from models.complain import ComplainCreate, ComplainInDB


CREATE_DATE_COMPLAIN = """
    INSERT INTO complains (complainant, accused, message_id)
    VALUES (:complainant, :accused, :message_id)
    RETURNING *;
"""


GET_COMPLAIN = """
    SELECT *
    FROM complains
    WHERE complainant = :complainant
        AND accused = :accused
    ;
"""


class ComplainRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.profiles_repo = ProfilesRepository(db)

    async def create_complain(
            self, *,
            complain_create: ComplainCreate
    ) -> ComplainInDB:

        complain = await self.db.fetch_one(
            query=CREATE_DATE_COMPLAIN,
            values=complain_create.dict()
        )

        return complain

    async def get_complain(
            self, *,
            complainant_id: int,
            accused_id: int,
    ) -> List[ComplainInDB]:
        complain = await self.db.fetch_one(
            query=GET_COMPLAIN,
            values={
                "complainant": complainant_id,
                "accused": accused_id
            }
        )
        return complain
