"""Bring databases created by early project versions up to the current schema.

Revision ID: b7c91f4d02ab
Revises: aaf8ad2bb972
"""
from alembic import op
import sqlalchemy as sa


revision = "b7c91f4d02ab"
down_revision = "aaf8ad2bb972"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    tables = set(inspector.get_table_names())

    if "usuario" in tables:
        columns = {column["name"] for column in inspector.get_columns("usuario")}
        additions = [
            # Users from the pre-confirmation schema already had working accounts.
            ("confirmado", sa.Boolean(), False, "true"),
            ("data_confirmacao", sa.DateTime(), True, None),
            ("codigo_confirmacao", sa.String(length=6), False, "'000000'"),
            ("foto_perfil", sa.String(length=50), False, "'default.jpg'"),
            ("cursos", sa.String(length=500), False, "'Nao Informado'"),
        ]
        for name, column_type, nullable, default in additions:
            if name not in columns:
                op.add_column(
                    "usuario",
                    sa.Column(name, column_type, nullable=nullable, server_default=sa.text(default) if default else None),
                )

    if "token_redefinicao" not in tables and "usuario" in tables:
        op.create_table(
            "token_redefinicao",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("token", sa.String(length=255), nullable=False, unique=True),
            sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id"), nullable=False),
            sa.Column("data_expiracao", sa.DateTime(timezone=True), nullable=False),
            sa.Column("usado", sa.Boolean(), nullable=False, server_default=sa.false()),
        )


def downgrade():
    # This compatibility migration may add defaults to live legacy data;
    # removing those columns could discard user information, so downgrade is a no-op.
    pass
