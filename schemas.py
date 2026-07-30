from pydantic import BaseModel
from typing import Optional

class StudentCreate(BaseModel):
    roll_number: str
    password: str
    name: str
    cgpa: float
    skills: str
    projects: str
    certifications: Optional[str] = None
    company_preference: Optional[str] = None
    role_preference: Optional[str] = None

class StudentLogin(BaseModel):
    roll_number: str
    password: str

class StudentResponse(BaseModel):
    id: int
    roll_number: str
    name: str
    cgpa: float
    skills: str
    projects: str
    certifications: Optional[str] = None
    company_preference: Optional[str] = None
    role_preference: Optional[str] = None
    quiz_score: Optional[int] = None
    interview_status: Optional[str] = None
    readiness_status: Optional[str] = None
    missing_skills: Optional[str] = None

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    cgpa: Optional[float] = None
    skills: Optional[str] = None
    projects: Optional[str] = None
    certifications: Optional[str] = None
    quiz_score: Optional[int] = None

class CompanyCreate(BaseModel):
    name: str
    role: str
    required_skills: str
    min_cgpa: float

class CompanyResponse(CompanyCreate):
    id: int

    class Config:
        from_attributes = True


class AdminCreate(BaseModel):
    username: str
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True