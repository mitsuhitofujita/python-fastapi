from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from models import Base


class City(Base):
    """City model representing municipalities (市区町村).

    Cities are administrative divisions within states (都道府県).
    Examples:
    - Tokyo 23 wards: "港区" (Minato-ku)
    - Designated cities: "横浜市鶴見区" (Yokohama-shi Tsurumi-ku)
    - Regular cities: "札幌市" (Sapporo-shi)
    """

    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    state_id = Column(
        Integer, ForeignKey("main.states.id", ondelete="RESTRICT"), nullable=False
    )
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Relationship
    state = relationship("State", back_populates="cities")

    def __repr__(self):
        return f"<City(id={self.id}, name='{self.name}', code='{self.code}', state_id={self.state_id}, is_active={self.is_active})>"
