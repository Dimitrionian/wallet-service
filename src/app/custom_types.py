import enum


class TransactionType(enum.Enum):
    WITHDRAW = 'WITHDRAW'
    DEPOSIT = 'DEPOSIT'


ALEMBIC_SCHEME = "postgresql"

