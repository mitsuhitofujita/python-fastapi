from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models.

    All tables will be created in the 'main' schema by default.
    """
    __table_args__ = {"schema": "main"}
