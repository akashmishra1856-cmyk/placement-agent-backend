from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    
    # Login ke liye
    roll_number = Column(String, unique=True, index=True)
    password = Column(String)
    
    # Basic profile (student khud form se bharega)
    name = Column(String)
    cgpa = Column(Float)
    skills = Column(String)
    projects = Column(String)
    certifications = Column(String, nullable=True)
    
    # Preferences
    company_preference = Column(String, nullable=True)
    role_preference = Column(String, nullable=True)
    
    # Quiz aur Interview status
    quiz_score = Column(Integer, nullable=True)
    interview_status = Column(String, nullable=True)
    
    # Final result
    readiness_status = Column(String, nullable=True)
    missing_skills = Column(String, nullable=True)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)              # jaise "Software Engineer", "Data Analyst"
    required_skills = Column(String)   # comma separated
    min_cgpa = Column(Float)

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String)              # jaise "Software Engineer", "Data Analyst"
    question_text = Column(String)     # asli sawal
    

class QuizResponse(Base):
    __tablename__ = "quiz_responses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)       # kaunsa student
    question_id = Column(Integer)      # kaunsa sawal
    answer_text = Column(String)       # student ne kya likha
    ai_score = Column(Integer, nullable=True)   # AI ne kitne number diye (0-10 jaisa)

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)                    # kaunsa student
    
    camera_verified = Column(Boolean, default=False) # camera on tha ya nahi
    transcript = Column(String, nullable=True)        # poori baatcheet (AI + student)
    
    status = Column(String, default="pending")         # "pending", "completed", "disqualified"
    ai_feedback = Column(String, nullable=True)         # AI ka overall feedback interview pe
    violation_reason = Column(String, nullable=True)   # kyu reject hua (jaise "Face not visible for 60+ seconds")
    screen_shared = Column(Boolean, default=False)      # screen share on tha ya nahi
    total_score = Column(Integer, default=0)
    answers_count = Column(Integer, default=0)


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

total_score = Column(Integer, default=0)
answers_count = Column(Integer, default=0)