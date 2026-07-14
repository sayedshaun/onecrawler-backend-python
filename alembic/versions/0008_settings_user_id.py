"""Add user_id to crawl_settings_templates and provider_api_keys so both are scoped to
their owner, matching crawl_jobs.

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-11

NOTE: this adds NOT NULL foreign keys with no default. If either table
already has rows, this migration will fail — there is no way to attribute
existing templates/keys to a user after the fact. Truncate both tables or
backfill user_id by hand before running this against a database with
existing data.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "crawl_settings_templates",
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
    )
    op.create_foreign_key(
        "fk_crawl_settings_templates_user_id_users",
        "crawl_settings_templates",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "crawl_settings_templates_name_key", "crawl_settings_templates", type_="unique"
    )
    op.create_unique_constraint(
        "uq_crawl_settings_templates_user_id_name",
        "crawl_settings_templates",
        ["user_id", "name"],
    )

    op.add_column(
        "provider_api_keys",
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
    )
    op.drop_constraint("provider_api_keys_pkey", "provider_api_keys", type_="primary")
    op.create_primary_key(
        "provider_api_keys_pkey", "provider_api_keys", ["user_id", "provider"]
    )
    op.create_foreign_key(
        "fk_provider_api_keys_user_id_users",
        "provider_api_keys",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_provider_api_keys_user_id_users", "provider_api_keys", type_="foreignkey"
    )
    op.drop_constraint("provider_api_keys_pkey", "provider_api_keys", type_="primary")
    op.create_primary_key("provider_api_keys_pkey", "provider_api_keys", ["provider"])
    op.drop_column("provider_api_keys", "user_id")

    op.drop_constraint(
        "uq_crawl_settings_templates_user_id_name",
        "crawl_settings_templates",
        type_="unique",
    )
    op.create_unique_constraint(
        "crawl_settings_templates_name_key", "crawl_settings_templates", ["name"]
    )
    op.drop_constraint(
        "fk_crawl_settings_templates_user_id_users",
        "crawl_settings_templates",
        type_="foreignkey",
    )
    op.drop_column("crawl_settings_templates", "user_id")
