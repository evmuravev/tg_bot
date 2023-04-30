from db.repositories.base import BaseRepository
from models.profile import ProfileCreate, ProfileUpdate, ProfileInDB


CREATE_PROFILE_FOR_USER_QUERY = """
    INSERT INTO profiles (user_id, status)
    VALUES (:user_id, :status)
    RETURNING *;
"""

GET_PROFILE_BY_USER_ID_QUERY = """
    SELECT *
    FROM profiles
    WHERE user_id = :user_id
        AND status != 'rejected';
"""

GET_PROFILE_BY_ID_QUERY = """
    SELECT *
    FROM profiles
    WHERE id = :id;
"""

UPDATE_PROFILE_QUERY = """
    UPDATE profiles
    SET
        id       = :id,
        name     = :name,
        sex      = :sex,
        age      = :age,
        age_tag  = :age_tag,
        city     = :city,
        region   = :region,
        image    = :image,
        bio      = :bio,
        status   = :status
    WHERE user_id = :user_id
        AND status != 'rejected'
    RETURNING *;
"""


class ProfilesRepository(BaseRepository):
    async def create_profile_for_user(
            self, *,
            profile_create: ProfileCreate
    ) -> ProfileInDB:

        created_profile = await self.db.fetch_one(
            query=CREATE_PROFILE_FOR_USER_QUERY,
            values=profile_create.dict()
        )

        return created_profile

    async def get_profile_by_user_id(self, *, user_id: int) -> ProfileInDB:
        profile_record = await self.db.fetch_one(
            query=GET_PROFILE_BY_USER_ID_QUERY,
            values={"user_id": user_id}
        )

        if not profile_record:
            return None

        return ProfileInDB(**profile_record)

    async def get_profile_by_id(self, *, id: int) -> ProfileInDB:
        profile_record = await self.db.fetch_one(
            query=GET_PROFILE_BY_ID_QUERY,
            values={"id": id}
        )

        if not profile_record:
            return None

        return ProfileInDB(**profile_record)

    async def update_profile(self, *,
                             profile_update: ProfileUpdate,
                             user_id: int,
                             exclude_unset=True) -> ProfileInDB:
        profile = await self.get_profile_by_user_id(user_id=user_id)
        update_params = profile.copy(
            update=profile_update.dict(exclude_unset=exclude_unset)
        )

        updated_profile = await self.db.fetch_one(
            query=UPDATE_PROFILE_QUERY,
            values=update_params.dict(
                exclude={"created_at", "updated_at"}
            ),
        )

        return ProfileInDB(**updated_profile)
