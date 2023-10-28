from databases import Database

from db.repositories.base import BaseRepository
from db.repositories.profiles import ProfilesRepository
from models.user import UserCreate, UserPublic, UserInDB, UserUpdate


GET_USER_BY_ID = """
    SELECT *
    FROM users
    WHERE id = :id;
"""

REGISTER_NEW_USER_QUERY = """
    INSERT INTO users (
        id,
        first_name,
        last_name,
        username,
        language_code,
        is_bot,
        link,
        is_premium,
        is_banned,
        num_of_complains
    )
    VALUES (
        :id,
        :first_name,
        :last_name,
        :username,
        :language_code,
        :is_bot,
        :link,
        :is_premium,
        :is_banned,
        :num_of_complains
    )
    RETURNING *;
"""

UPDATE_USERNAME_QUERY = """
    UPDATE users
    SET username = :username
    WHERE id = :user_id
    RETURNING *;
"""

UPDATE_IS_BANNED_QUERY = """
    UPDATE users
    SET is_banned = :is_banned
    WHERE id = :user_id
    RETURNING *;
"""

UPDATE_NUM_OF_COMPLAINS_QUERY = """
    UPDATE users
    SET num_of_complains = num_of_complains + 1
    WHERE id = :user_id
    RETURNING *;
"""


class UsersRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.profiles_repo = ProfilesRepository(db)

    async def get_user_by_id(self, *,
                             id: int, populate: bool = True) -> UserPublic:
        user_record = await self.db.fetch_one(
            query=GET_USER_BY_ID, values={"id": id}
        )

        if user_record:
            user = UserInDB(**user_record)
            if populate:
                return await self.populate_user(user=user)
            return user

    async def register_new_user(self, *, new_user: UserCreate) -> UserPublic:
        user = await self.db.fetch_one(
            query=REGISTER_NEW_USER_QUERY,
            values=new_user.dict()
        )
        return await self.populate_user(user=UserInDB(**user))

    async def populate_user(self, *, user: UserInDB) -> UserPublic:
        return UserPublic(
            **user.dict(),
            # fetch the user's profile from the profiles repo
            profile=await self.profiles_repo.get_profile_by_user_id(
                user_id=user.id
            )
        )

    async def update_username(self, *, user: UserUpdate) -> UserInDB:
        updated_user = await self.db.fetch_one(
            query=UPDATE_USERNAME_QUERY,
            values={"user_id": user.id, "username": user.username},
        )
        if updated_user:
            user = UserInDB(**updated_user)
            return await self.populate_user(user=user)


    async def update_is_banned(self, *, user: UserInDB) -> UserInDB:
        updated_user = await self.db.fetch_one(
            query=UPDATE_IS_BANNED_QUERY,
            values={"user_id": user.id, "is_banned": True},
        )

        return UserInDB(**updated_user)

    async def inc_num_of_complains(self, *, user: UserPublic) -> UserInDB:
        updated_user = await self.db.fetch_one(
            query=UPDATE_NUM_OF_COMPLAINS_QUERY,
            values={"user_id": user.id},
        )

        return UserInDB(**updated_user)
