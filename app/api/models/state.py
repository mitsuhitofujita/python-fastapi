from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models import Base


class State(Base):
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, autoincrement=True)
    country_id = Column(
        Integer, ForeignKey("main.countries.id", ondelete="RESTRICT"), nullable=False
    )
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False, unique=True)

    # Relationship
    cities = relationship("City", back_populates="state")

    def __repr__(self):
        return f"<State(id={self.id}, name='{self.name}', code='{self.code}', country_id={self.country_id})>"
