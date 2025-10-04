from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from models import Base


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    request_method = Column(String(10), nullable=False)
    request_path = Column(String(500), nullable=False)
    request_body = Column(Text, nullable=True)
    user_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.current_timestamp())
    status_code = Column(Integer, nullable=True)
    processing_status = Column(String(20), nullable=False, server_default="completed")
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<EventLog(id={self.id}, event_type='{self.event_type}', entity_type='{self.entity_type}', entity_id={self.entity_id})>"
