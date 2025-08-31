"""create_story_heroes_junction_table

Revision ID: 1e754f2c9b28
Revises: 4e83abfd03dd
Create Date: 2025-08-31 11:28:43.555010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e754f2c9b28'
down_revision: Union[str, Sequence[str], None] = '4e83abfd03dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create story_heroes junction table
    op.create_table(
        'story_heroes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('story_id', sa.UUID(), nullable=False),
        sa.Column('hero_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['hero_id'], ['heroes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_story_heroes_story_id', 'story_heroes', ['story_id'])
    op.create_index('ix_story_heroes_hero_id', 'story_heroes', ['hero_id'])
    op.create_index('ix_story_hero_unique', 'story_heroes', ['story_id', 'hero_id'], unique=True)
    op.create_index(op.f('ix_story_heroes_id'), 'story_heroes', ['id'])

    # Migrate data from hero_ids array to junction table
    connection = op.get_bind()
    
    # Get all stories with hero_ids
    result = connection.execute(sa.text("""
        SELECT id, hero_ids, created_at 
        FROM stories 
        WHERE hero_ids IS NOT NULL AND array_length(hero_ids, 1) > 0
    """))
    
    stories_data = result.fetchall()
    
    # Insert story-hero relationships
    for story_id, hero_ids, created_at in stories_data:
        if hero_ids:
            for hero_id in hero_ids:
                connection.execute(sa.text("""
                    INSERT INTO story_heroes (id, story_id, hero_id, created_at)
                    VALUES (gen_random_uuid(), :story_id, :hero_id, :created_at)
                """), {
                    'story_id': story_id,
                    'hero_id': hero_id,
                    'created_at': created_at
                })
    
    # Remove hero_ids column
    op.drop_column('stories', 'hero_ids')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back hero_ids column
    op.add_column('stories', sa.Column('hero_ids', sa.ARRAY(sa.UUID()), nullable=True))
    
    # Migrate data back from junction table to hero_ids array
    connection = op.get_bind()
    
    # Get story-hero relationships
    result = connection.execute(sa.text("""
        SELECT story_id, array_agg(hero_id) as hero_ids
        FROM story_heroes
        GROUP BY story_id
    """))
    
    story_heroes_data = result.fetchall()
    
    # Update stories with hero_ids arrays
    for story_id, hero_ids in story_heroes_data:
        connection.execute(sa.text("""
            UPDATE stories 
            SET hero_ids = :hero_ids 
            WHERE id = :story_id
        """), {
            'story_id': story_id,
            'hero_ids': hero_ids
        })
    
    # Drop junction table
    op.drop_index('ix_story_hero_unique', 'story_heroes')
    op.drop_index('ix_story_heroes_hero_id', 'story_heroes')
    op.drop_index('ix_story_heroes_story_id', 'story_heroes')
    op.drop_index(op.f('ix_story_heroes_id'), 'story_heroes')
    op.drop_table('story_heroes')
