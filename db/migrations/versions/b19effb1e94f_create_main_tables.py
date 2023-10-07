"""create_main_tables

Revision ID: b19effb1e94f
Revises:
Create Date: 2023-04-24 21:18:41.180889

"""
from typing import Tuple
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'b19effb1e94f'
down_revision = None
branch_labels = None
depends_on = None


def create_updated_at_trigger() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS
        $$
        BEGIN
            NEW._updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        """
    )


def timestamps(indexed: bool = False) -> Tuple[sa.Column, sa.Column]:
    return (
        sa.Column(
            "_created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
        sa.Column(
            "_updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=indexed,
        ),
    )


def create_users_table() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger, nullable=False, index=True, unique=True),
        sa.Column("first_name", sa.Text, nullable=True),
        sa.Column("last_name", sa.Text, nullable=True),
        sa.Column("username", sa.Text, nullable=True),
        sa.Column("language_code", sa.Text, nullable=False),
        sa.Column("is_bot", sa.Boolean(), nullable=False),
        sa.Column("link", sa.Text, nullable=True),
        sa.Column("is_premium", sa.Boolean(), nullable=True),
        sa.Column("is_banned", sa.Boolean(), nullable=True),
        sa.Column("num_of_complains", sa.Integer, default=0),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_user_modtime
            BEFORE UPDATE
            ON users
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def create_profiles_table() -> None:
    op.create_table(
        "profiles",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("name", sa.Text, nullable=True),
        sa.Column("sex", sa.CHAR(length=1), nullable=True),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("age_tag", sa.Text, nullable=True),
        sa.Column("city", sa.Text, nullable=True),
        sa.Column("region", sa.Text, nullable=True),
        sa.Column("image", sa.Text, nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("user_id", sa.BigInteger, sa.ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("status", sa.Text, default='new', index=True),
        sa.Column("admins_comment", sa.Text, nullable=True),
        *timestamps(),
    )
    op.execute(
        """
        CREATE TRIGGER update_profiles_modtime
            BEFORE UPDATE
            ON profiles
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def create_date_offers_table() -> None:
    op.create_table(
        "date_offers",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("profile_id", sa.BigInteger, sa.ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("where", sa.Text, nullable=True),
        sa.Column("when", sa.Text, nullable=True),
        sa.Column("expectations", sa.Text, nullable=True),
        sa.Column("bill_splitting", sa.Text, nullable=True),
        sa.Column("message_id", sa.Text, index=True, nullable=True),
        *timestamps(indexed=True),
    )
    op.execute(
        """
        CREATE TRIGGER update_date_offers_modtime
            BEFORE UPDATE
            ON date_offers
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def create_date_responses_table() -> None:
    op.create_table(
        "date_responses",
        sa.Column("inviter", sa.BigInteger, sa.ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("responder", sa.BigInteger, sa.ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("message_id", sa.Text, index=True, nullable=True),
        *timestamps(indexed=True),
    )
    op.execute(
        """
        CREATE TRIGGER update_date_responses_modtime
            BEFORE UPDATE
            ON date_responses
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def create_complains_table() -> None:
    op.create_table(
        "complains",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("complainant", sa.BigInteger, sa.ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("accused", sa.BigInteger, sa.ForeignKey("profiles.id", ondelete="CASCADE"), index=True, nullable=False),
        sa.Column("message_id", sa.Text, index=True, nullable=True),
        sa.Column("status", sa.Text, index=True, nullable=True),
        *timestamps(indexed=True),
    )
    op.execute(
        """
        CREATE TRIGGER update_complains_modtime
            BEFORE UPDATE
            ON complains
            FOR EACH ROW
        EXECUTE PROCEDURE update_updated_at_column();
        """
    )


def upgrade() -> None:
    create_updated_at_trigger()
    create_users_table()
    create_profiles_table()
    create_date_offers_table()
    create_date_responses_table()
    create_complains_table()


def downgrade() -> None:
    op.drop_table("complains")
    op.drop_table("date_responses")
    op.drop_table("date_offers")
    op.drop_table("profiles")
    op.drop_table("users")
    op.execute("DROP FUNCTION update_updated_at_column")
