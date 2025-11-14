"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enums
    op.execute("""
        CREATE TYPE teststatus AS ENUM ('passed', 'failed', 'broken', 'skipped', 'unknown');
        CREATE TYPE userrole AS ENUM ('admin', 'developer', 'viewer');
        CREATE TYPE analysistype AS ENUM ('root_cause', 'flaky_detection', 'visual_analysis', 'predictive', 'bug_triage');
    """)
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255)),
        sa.Column('role', ENUM('admin', 'developer', 'viewer', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'), onupdate=sa.text('NOW()'))
    )
    
    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('description', sa.Text),
        sa.Column('repository_url', sa.String(500)),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('metadata', JSONB)
    )
    
    # Test suites table
    op.create_table(
        'test_suites',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, index=True),
        sa.Column('path', sa.String(500)),
        sa.Column('description', sa.Text),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'))
    )
    
    # Test runs table
    op.create_table(
        'test_runs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('suite_id', UUID(as_uuid=True), sa.ForeignKey('test_suites.id'), nullable=False),
        sa.Column('run_id', sa.String(255), nullable=False, index=True),
        sa.Column('status', ENUM('passed', 'failed', 'broken', 'skipped', 'unknown', name='teststatus'), nullable=False),
        sa.Column('started_at', sa.DateTime, nullable=False, index=True),
        sa.Column('finished_at', sa.DateTime),
        sa.Column('duration_ms', sa.Integer),
        sa.Column('environment', sa.String(100)),
        sa.Column('build_number', sa.String(100)),
        sa.Column('branch', sa.String(255)),
        sa.Column('metadata', JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'))
    )
    
    # Test results table
    op.create_table(
        'test_results',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('run_id', UUID(as_uuid=True), sa.ForeignKey('test_runs.id'), nullable=False, index=True),
        sa.Column('test_name', sa.String(500), nullable=False, index=True),
        sa.Column('full_name', sa.Text),
        sa.Column('status', ENUM('passed', 'failed', 'broken', 'skipped', 'unknown', name='teststatus'), nullable=False, index=True),
        sa.Column('duration_ms', sa.Integer),
        sa.Column('error_message', sa.Text),
        sa.Column('error_trace', sa.Text),
        sa.Column('description', sa.Text),
        sa.Column('labels', JSONB),
        sa.Column('parameters', JSONB),
        sa.Column('attachments', JSONB),
        sa.Column('history_id', sa.String(255), index=True),
        sa.Column('retry_count', sa.Integer, default=0),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'))
    )
    
    # AI analyses table
    op.create_table(
        'ai_analyses',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('test_result_id', UUID(as_uuid=True), sa.ForeignKey('test_results.id'), nullable=False, index=True),
        sa.Column('analysis_type', ENUM('root_cause', 'flaky_detection', 'visual_analysis', 'predictive', 'bug_triage', name='analysistype'), nullable=False, index=True),
        sa.Column('result', JSONB, nullable=False),
        sa.Column('confidence', sa.Float),
        sa.Column('prompt_used', sa.Text),
        sa.Column('model_used', sa.String(100)),
        sa.Column('similar_issues', JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'), index=True)
    )
    
    # Flaky tests table
    op.create_table(
        'flaky_tests',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('test_name', sa.String(500), nullable=False, index=True),
        sa.Column('history_id', sa.String(255), nullable=False, index=True),
        sa.Column('total_runs', sa.Integer, default=0),
        sa.Column('passed_runs', sa.Integer, default=0),
        sa.Column('failed_runs', sa.Integer, default=0),
        sa.Column('flakiness_score', sa.Float),
        sa.Column('first_detected', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('last_detected', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('failure_patterns', JSONB),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, server_default=sa.text('NOW()'))
    )
    
    # Attachments table
    op.create_table(
        'attachments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('test_result_id', UUID(as_uuid=True), sa.ForeignKey('test_results.id'), nullable=False),
        sa.Column('filename', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(100)),
        sa.Column('mime_type', sa.String(100)),
        sa.Column('file_size', sa.Integer),
        sa.Column('storage_path', sa.String(1000), nullable=False),
        sa.Column('storage_bucket', sa.String(255)),
        sa.Column('created_at', sa.DateTime, server_default=sa.text('NOW()'))
    )
    
    # Create indexes
    op.create_index('idx_test_results_history', 'test_results', ['history_id', 'created_at'])
    op.create_index('idx_flaky_tests_project', 'flaky_tests', ['project_id', 'is_active'])


def downgrade() -> None:
    op.drop_table('attachments')
    op.drop_table('flaky_tests')
    op.drop_table('ai_analyses')
    op.drop_table('test_results')
    op.drop_table('test_runs')
    op.drop_table('test_suites')
    op.drop_table('projects')
    op.drop_table('users')
    
    op.execute('DROP TYPE IF EXISTS analysistype')
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS teststatus')

