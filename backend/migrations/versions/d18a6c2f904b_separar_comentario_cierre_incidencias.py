"""Separar comentario de cierre de las medidas registradas.

Los registros anteriores se conservan sin reinterpretar su contenido.
"""
from alembic import op
import sqlalchemy as sa

revision = 'd18a6c2f904b'
down_revision = 'c0af3fd5552a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('incidencias', sa.Column('comentario_cierre', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('incidencias', 'comentario_cierre')
