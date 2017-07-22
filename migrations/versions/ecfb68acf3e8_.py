"""empty message

Revision ID: ecfb68acf3e8
Revises: 
Create Date: 2017-07-22 22:50:24.910000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecfb68acf3e8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ca',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('root_ca', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=256), nullable=True),
    sa.Column('dscr', sa.String(length=256), nullable=True),
    sa.Column('subject_dn', sa.String(length=128), nullable=True),
    sa.Column('extensions', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ca_dscr'), 'ca', ['dscr'], unique=False)
    op.create_index(op.f('ix_ca_name'), 'ca', ['name'], unique=False)
    op.create_index(op.f('ix_ca_subject_dn'), 'ca', ['subject_dn'], unique=False)
    op.create_table('templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('dscr', sa.String(length=256), nullable=True),
    sa.Column('extensions', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_templates_dscr'), 'templates', ['dscr'], unique=False)
    op.create_index(op.f('ix_templates_name'), 'templates', ['name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.Column('subject', sa.String(length=256), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)
    op.create_index(op.f('ix_users_subject'), 'users', ['subject'], unique=False)
    op.create_table('ca_keys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ca', sa.Integer(), nullable=True),
    sa.Column('private', sa.Text(), nullable=True),
    sa.Column('public', sa.Text(), nullable=True),
    sa.Column('expires_in', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['ca'], ['ca.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('certificates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ca', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('serial', sa.String(length=64), nullable=True),
    sa.Column('public', sa.Text(), nullable=True),
    sa.Column('p12', sa.Text(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('code_revoke', sa.Integer(), nullable=True),
    sa.Column('reason_revoke', sa.String(length=256), nullable=True),
    sa.Column('date_revoke', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['ca'], ['ca.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_certificates_name'), 'certificates', ['name'], unique=False)
    op.create_table('crls',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ca', sa.Integer(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('crl', sa.LargeBinary(), nullable=False),
    sa.ForeignKeyConstraint(['ca'], ['ca.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('crls')
    op.drop_index(op.f('ix_certificates_name'), table_name='certificates')
    op.drop_table('certificates')
    op.drop_table('ca_keys')
    op.drop_index(op.f('ix_users_subject'), table_name='users')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_templates_name'), table_name='templates')
    op.drop_index(op.f('ix_templates_dscr'), table_name='templates')
    op.drop_table('templates')
    op.drop_index(op.f('ix_ca_subject_dn'), table_name='ca')
    op.drop_index(op.f('ix_ca_name'), table_name='ca')
    op.drop_index(op.f('ix_ca_dscr'), table_name='ca')
    op.drop_table('ca')
    # ### end Alembic commands ###
