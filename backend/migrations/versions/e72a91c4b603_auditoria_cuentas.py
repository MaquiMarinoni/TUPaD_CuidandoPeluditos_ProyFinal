"""Registrar cambios administrativos de estado de cuentas.

Los cambios anteriores no se reconstruyen ni se atribuyen a un actor ficticio.
"""
from alembic import op
import sqlalchemy as sa

revision = 'e72a91c4b603'
down_revision = 'd18a6c2f904b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('auditoria_cuentas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('administrador_id', sa.Integer(), nullable=False),
        sa.Column('activo_anterior', sa.Boolean(), nullable=False),
        sa.Column('activo_nuevo', sa.Boolean(), nullable=False),
        sa.Column('motivo', sa.String(1000), nullable=False),
        sa.Column('fecha_cambio', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['administrador_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'))
    op.create_index('ix_auditoria_cuentas_usuario_id', 'auditoria_cuentas', ['usuario_id'])


def downgrade():
    op.drop_index('ix_auditoria_cuentas_usuario_id', table_name='auditoria_cuentas')
    op.drop_table('auditoria_cuentas')
