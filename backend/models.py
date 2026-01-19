from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class ProjectRequest(Base):
    __tablename__ = "project_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    project_type = Column(String(50))
    description = Column(Text)
    status = Column(String(20), default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
