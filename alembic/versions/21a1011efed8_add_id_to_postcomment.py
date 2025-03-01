from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# Revision identifiers
revision = '21a1011efed8'
down_revision = '7ec41f26e160'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()

    # Step 1: Add `id` column (allow NULL initially, will be auto-increment)
    op.add_column('post_comments', sa.Column('id', sa.Integer(), autoincrement=True, nullable=True))

    # Step 2: Create sequence for auto-increment if not exists
    conn.execute(text("CREATE SEQUENCE IF NOT EXISTS post_comments_id_seq START WITH 1 INCREMENT BY 1 OWNED BY post_comments.id"))
    
    # Step 3: Attach sequence to `id` column (so it auto-increments)
    conn.execute(text("ALTER TABLE post_comments ALTER COLUMN id SET DEFAULT nextval('post_comments_id_seq')"))

    # Step 4: Populate existing rows with unique values
    conn.execute(text("UPDATE post_comments SET id = nextval('post_comments_id_seq') WHERE id IS NULL"))

    # Step 5: Make `id` column NOT NULL
    op.alter_column('post_comments', 'id', nullable=False)

    # Step 6: Drop the old primary key (user_id, post_id)
    op.drop_constraint("post_comments_pkey", "post_comments", type_="primary")

    # Step 7: Set `id` as the new primary key
    op.create_primary_key("pk_post_comments", "post_comments", ["id"])

def downgrade():
    # Step 1: Restore the old primary key
    op.drop_constraint("pk_post_comments", "post_comments", type_="primary")
    op.create_primary_key("post_comments_pkey", "post_comments", ["user_id", "post_id"])

    # Step 2: Remove the `id` column
    op.drop_column('post_comments', 'id')

    # Step 3: Drop sequence if needed
    conn = op.get_bind()
    conn.execute(text("DROP SEQUENCE IF EXISTS post_comments_id_seq"))
