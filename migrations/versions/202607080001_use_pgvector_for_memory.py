"""use pgvector for memory

Revision ID: 202607080001
Revises: 202607070006
Create Date: 2026-07-08
"""

from collections.abc import Sequence

from alembic import op

revision: str = "202607080001"
down_revision: str | Sequence[str] | None = "202607070006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("ALTER TABLE memories ALTER COLUMN vector TYPE vector USING vector::text::vector")
    op.execute(
        """
        CREATE INDEX memories_vector_8_hnsw_cosine_idx
        ON memories
        USING hnsw ((vector::vector(8)) vector_cosine_ops)
        WHERE dimensions = 8
        """
    )
    op.execute(
        """
        CREATE INDEX memories_vector_1536_hnsw_cosine_idx
        ON memories
        USING hnsw ((vector::vector(1536)) vector_cosine_ops)
        WHERE dimensions = 1536
        """
    )


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return

    op.execute("DROP INDEX IF EXISTS memories_vector_1536_hnsw_cosine_idx")
    op.execute("DROP INDEX IF EXISTS memories_vector_8_hnsw_cosine_idx")
    op.execute("ALTER TABLE memories ALTER COLUMN vector TYPE json USING vector::text::json")
