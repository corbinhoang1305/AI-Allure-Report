"""add_allure_uuid_to_test_results

Revision ID: 002_add_allure_uuid
Revises: 001_initial_schema
Create Date: 2025-11-14 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_add_allure_uuid'
down_revision: Union[str, None] = '001'  # Matches revision ID from 001_initial_schema.py
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add allure_uuid column to test_results table
    op.add_column('test_results', 
        sa.Column('allure_uuid', sa.String(255), nullable=True))
    
    # Create index on allure_uuid for faster lookups
    op.create_index('ix_test_results_allure_uuid', 'test_results', ['allure_uuid'])


def downgrade() -> None:
    # Drop index first
    op.drop_index('ix_test_results_allure_uuid', 'test_results')
    
    # Drop column
    op.drop_column('test_results', 'allure_uuid')

