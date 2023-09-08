from typing import List
from databases import Database
from db.repositories.base import BaseRepository
from db.repositories.profiles import ProfilesRepository
from models.complain import ComplainCreate, ComplainInDB, ComplainUpdate


CREATE_DATE_COMPLAIN = """
    INSERT INTO complains (complainant, accused, message_id, status)
    VALUES (:complainant, :accused, :message_id, :status)
    RETURNING *;
"""


GET_NEW_COMPLAIN = """
    SELECT *
    FROM complains
    WHERE complainant = :complainant
        AND accused = :accused
        AND status = 'new'
    ;
"""


UPDATE_COMPLAIN_STATUS = """
    UPDATE complains
    SET status = :status
    WHERE id = :id
    RETURNING *;
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

        return ComplainInDB(**complain)

    async def get_complain(
            self, *,
            complainant_id: int,
            accused_id: int,
    ) -> ComplainInDB:
        complain = await self.db.fetch_one(
            query=GET_NEW_COMPLAIN,
            values={
                "complainant": complainant_id,
                "accused": accused_id
            }
        )
        if complain:
            return ComplainInDB(**complain)

    async def update_status_complain(
            self, *,
            complain_update: ComplainUpdate,
    ) -> ComplainInDB:
        complain = await self.db.fetch_one(
            query=UPDATE_COMPLAIN_STATUS,
            values={
                "id": complain_update.id,
                "status": complain_update.status
            }
        )
        return ComplainInDB(**complain)
