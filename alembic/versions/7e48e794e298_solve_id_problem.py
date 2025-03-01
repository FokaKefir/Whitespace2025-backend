from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '7e48e794e298'
down_revision = '21a1011efed8'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the existing post_comments table
    op.drop_table("post_comments")

    # Recreate the table with an auto-incrementing primary key
    op.create_table(
        "post_comments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("post_id", sa.String(), sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # Add indexes for faster lookups
    op.create_index("ix_post_comments_user_id", "post_comments", ["user_id"])
    op.create_index("ix_post_comments_post_id", "post_comments", ["post_id"])

def downgrade():
    # Drop the newly created post_comments table
    op.drop_table("post_comments")

    # Recreate the old version without an auto-incrementing id
    op.create_table(
        "post_comments",
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("post_id", sa.String(), sa.ForeignKey("posts.id"), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

