from sqlalchemy import Column, Integer, String
from .database import Base

class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    project_type = Column(String)  
    project_desc = Column(String)
    status=Column(String , default="pending")
