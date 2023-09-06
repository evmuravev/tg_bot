from databases import Database
from db.repositories.base import BaseRepository
from db.repositories.profiles import ProfilesRepository
from models.date_offer import DateOfferCreate, DateOfferPublic, DateOfferUpdate, DateOfferInDB


CREATE_DATE_OFFER_FOR_PROFILE_QUERY = """
    INSERT INTO date_offers (profile_id)
    VALUES (:profile_id)
    RETURNING *;
"""

GET_DATE_OFFER_BY_PROFILE_ID_QUERY = """
    SELECT *
    FROM date_offers
    WHERE profile_id = :profile_id
    ORDER BY _updated_at DESC
    LIMIT 1;
"""

GET_LAST_DATE_OFFER_BY_PROFILE_ID_QUERY = """
    SELECT *
    FROM date_offers
    WHERE profile_id = :profile_id
        AND message_id IS NOT NULL
    ORDER BY _updated_at DESC
    LIMIT 1;
"""

UPDATE_DATE_OFFER_QUERY = '''
    UPDATE date_offers
    SET
        "where"        = :where,
        "when"         = :when,
        expectations   = :expectations,
        bill_splitting = :bill_splitting,
        message_id     = :message_id
    WHERE id = :id

    RETURNING *;
'''


class DateOffersRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.profiles_repo = ProfilesRepository(db)

    async def create_date_offer_for_profile(
            self, *,
            date_offer_create: DateOfferCreate
    ) -> DateOfferInDB:

        created_date_offer = await self.db.fetch_one(
            query=CREATE_DATE_OFFER_FOR_PROFILE_QUERY,
            values=date_offer_create.dict()
        )

        return created_date_offer

    async def get_date_offer_by_profile_id(
            self, *,
            profile_id: int,
            populate: bool = True
    ) -> DateOfferInDB:
        date_offer_record = await self.db.fetch_one(
            query=GET_DATE_OFFER_BY_PROFILE_ID_QUERY,
            values={"profile_id": profile_id}
        )

        if date_offer_record:
            date_offer = DateOfferInDB(**date_offer_record)
            if populate:
                return await self.populate_date_offer(date_offer=date_offer)
            return date_offer

    async def get_last_date_offer_by_profile_id(
            self, *,
            profile_id: int,
            populate: bool = True
    ) -> DateOfferInDB:
        date_offer_record = await self.db.fetch_one(
            query=GET_LAST_DATE_OFFER_BY_PROFILE_ID_QUERY,
            values={"profile_id": profile_id}
        )

        if date_offer_record:
            date_offer = DateOfferInDB(**date_offer_record)
            if populate:
                return await self.populate_date_offer(date_offer=date_offer)
            return date_offer

    async def populate_date_offer(self, *, date_offer: DateOfferInDB) -> DateOfferPublic:
        return DateOfferPublic(
            **date_offer.dict(),
            # fetch the user's profile from the profiles repo
            profile=await self.profiles_repo.get_profile_by_id(
                id=date_offer.profile_id
            )
        )

    async def update_date_offer(
            self, *,
            date_offer_update: DateOfferUpdate,
            profile_id: int,
            exclude_unset=True
    ) -> DateOfferInDB:
        date_offer = await self.get_date_offer_by_profile_id(
            profile_id=profile_id, populate=False
        )
        update_params = date_offer.copy(
            update=date_offer_update.dict(exclude_unset=exclude_unset)
        )

        updated_date_offer = await self.db.fetch_one(
            query=UPDATE_DATE_OFFER_QUERY,
            values=update_params.dict(
                exclude={"created_at", "updated_at", "profile_id"}
            )
        )

        return DateOfferInDB(**updated_date_offer)
