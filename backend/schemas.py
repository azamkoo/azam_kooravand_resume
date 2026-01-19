from pydantic import BaseModel, EmailStr
from datetime import datetime

class ProjectRequestCreate(BaseModel):
    name: str
    email: EmailStr
    project_type: str
    description: str

class ProjectRequestResponse(ProjectRequestCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
