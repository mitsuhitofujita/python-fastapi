from sqlalchemy import Column, Integer, String

from models import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    code = Column(String(2), nullable=False, unique=True)

    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}', code='{self.code}')>"
