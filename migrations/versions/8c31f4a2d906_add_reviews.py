"""add reviews

Revision ID: 8c31f4a2d906
Revises: 5d281107acc7
"""
from alembic import op
import sqlalchemy as sa


revision = '8c31f4a2d906'
down_revision = '5d281107acc7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'reviews',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('review', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id']),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
        sa.PrimaryKeyConstraint('student_id', 'course_id')
    )


def downgrade():
    op.drop_table('reviews')
