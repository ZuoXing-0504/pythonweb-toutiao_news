"""add concurrency constraints

Revision ID: 20261107_0002
Revises: 20261104_0001
Create Date: 2026-11-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "20261107_0002"
down_revision: Union[str, Sequence[str], None] = "20261104_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Keep the most recently viewed row before enforcing one history row per user/news.
    op.execute(
        sa.text(
            """
            DELETE FROM history
            WHERE id IN (
                SELECT id
                FROM (
                    SELECT
                        id,
                        ROW_NUMBER() OVER (
                            PARTITION BY user_id, news_id
                            ORDER BY view_time DESC, id DESC
                        ) AS duplicate_rank
                    FROM history
                ) AS duplicate_history
                WHERE duplicate_rank > 1
            )
            """
        )
    )
    # Keep the latest token if an older database already contains duplicates.
    op.execute(
        sa.text(
            """
            DELETE FROM user_token
            WHERE id IN (
                SELECT id
                FROM (
                    SELECT
                        id,
                        ROW_NUMBER() OVER (
                            PARTITION BY user_id
                            ORDER BY created_at DESC, id DESC
                        ) AS duplicate_rank
                    FROM user_token
                ) AS duplicate_token
                WHERE duplicate_rank > 1
            )
            """
        )
    )
    op.create_unique_constraint(
        "uq_history_user_news",
        "history",
        ["user_id", "news_id"],
    )
    op.create_unique_constraint(
        "uq_user_token_user_id",
        "user_token",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_user_token_user_id", "user_token", type_="unique")
    op.drop_constraint("uq_history_user_news", "history", type_="unique")
