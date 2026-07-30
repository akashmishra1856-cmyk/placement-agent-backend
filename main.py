from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas
from database import engine, SessionLocal

from passlib.context import CryptContext
import ai_agent
from ai_agent import analyze_gap

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Backend chal raha hai!"}


# ==========================================
# STUDENT REGISTER
# ==========================================
@app.post("/register", response_model=schemas.StudentResponse)
def register_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # Check karo ki roll number pehle se toh nahi hai
    existing = db.query(models.Student).filter(models.Student.roll_number == student.roll_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Roll number already registered")

    student_data = student.dict()
    student_data["password"] = hash_password(student_data["password"])
    new_student = models.Student(**student_data)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


# ==========================================
# STUDENT LOGIN
# ==========================================
@app.post("/login", response_model=schemas.StudentResponse)
def login_student(credentials: schemas.StudentLogin, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(
        models.Student.roll_number == credentials.roll_number
    ).first()
    if not student:
        raise HTTPException(status_code=401, detail="Invalid roll number or password")
    if not verify_password(credentials.password, student.password):
        raise HTTPException(status_code=401, detail="Invalid roll number or password")
    return student


# ==========================================
# SABHI STUDENTS DEKHNE KE LIYE (Admin ke kaam aayega)
# ==========================================
@app.get("/students", response_model=list[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

# ==========================================
# COMPANY ADD KARNA (Admin Ke Liye)
# ==========================================
@app.post("/companies", response_model=schemas.CompanyResponse)
def create_company(company: schemas.CompanyCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Company).filter(models.Company.name == company.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Company already exists")
    new_company = models.Company(**company.dict())
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company

# ==========================================
# SABHI COMPANIES DEKHNA
# ==========================================
@app.get("/companies", response_model=list[schemas.CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    return db.query(models.Company).all()
# ==========================================
# ---- PREFERENCE CONFIRM ----
@app.put("/students/{student_id}/confirm-preference", response_model=schemas.StudentResponse)
def confirm_preference(student_id: int, company_preference: str, role_preference: str, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.company_preference = company_preference
    student.role_preference = role_preference
    db.commit()
    db.refresh(student)
    return student

@app.delete("/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(models.Company).filter(models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    db.delete(company)
    db.commit()
    return {"message": f"Company '{company.name}' deleted successfully"}

# QUIZ QUESTION ADD KARNA (Admin Ke Liye)
# ==========================================
@app.post("/quiz/questions")
def add_quiz_question(role: str, question_text: str, db: Session = Depends(get_db)):
    new_question = models.QuizQuestion(role=role, question_text=question_text)
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question


# ==========================================
# EK ROLE KE SAARE QUESTIONS DEKHNA (Student Ke Liye)
# ==========================================
@app.get("/quiz/questions/{role}")
def get_quiz_questions(role: str, db: Session = Depends(get_db)):
    questions = db.query(models.QuizQuestion).filter(
        func.lower(models.QuizQuestion.role) == func.lower(role)
    ).all()
    return questions


# ==========================================
# STUDENT APNA ANSWER SUBMIT KARE
# ==========================================
from ai_agent import grade_quiz_answer

@app.post("/quiz/submit")
def submit_quiz_answer(student_id: int, question_id: int, answer_text: str, db: Session = Depends(get_db)):
    question = db.query(models.QuizQuestion).filter(models.QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    score = grade_quiz_answer(question.question_text, answer_text)

    new_response = models.QuizResponse(
        student_id=student_id,
        question_id=question_id,
        answer_text=answer_text,
        ai_score=score
    )
    db.add(new_response)
    db.commit()
    db.refresh(new_response)

    # Result ko pehle hi capture kar lo (double-commit bug se bachne ke liye)
    result = {
        "id": new_response.id,
        "student_id": new_response.student_id,
        "question_id": new_response.question_id,
        "answer_text": new_response.answer_text,
        "ai_score": new_response.ai_score,
    }

    return result

# ==========================================
# INTERVIEW START KARNA
# ==========================================
@app.post("/interview/start")
def start_interview(student_id: int, db: Session = Depends(get_db)):
    new_interview = models.Interview(
        student_id=student_id,
        status="in_progress"
    )
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)
    return new_interview


# ==========================================
# TRANSCRIPT UPDATE KARNA (Baatcheet Save Karna)
# ==========================================
@app.put("/interview/{interview_id}/update")
def update_interview(interview_id: int, transcript: str, camera_verified: bool, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview.transcript = transcript
    interview.camera_verified = camera_verified
    db.commit()
    db.refresh(interview)
    return interview


# ==========================================
# INTERVIEW KHATAM KARNA (Final Status Set Karna)
# ==========================================
@app.put("/interview/{interview_id}/complete")
def complete_interview(interview_id: int, status: str, ai_feedback: str, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    interview.status = status          # "completed" ya "disqualified"
    interview.ai_feedback = ai_feedback
    student = db.query(models.Student).filter(models.Student.id == interview.student_id).first()
    if student:
        student.interview_status = status
    db.commit()
    db.refresh(interview)
    return interview

# ---- READINESS CHECK ----
@app.put("/students/{student_id}/check-readiness")
def check_readiness(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    reasons = []



    # Company dhundo jo student ne prefer kiya hai
    company = db.query(models.Company).filter(
        models.Company.name == student.company_preference
    ).first()

    if not company:
        student.readiness_status = "Not Ready"
        student.missing_skills = "Company preference not set or company not found"
        db.commit()
        db.refresh(student)
        return student

    # 1. CGPA check
    if student.cgpa < company.min_cgpa:
        reasons.append(f"CGPA below required {company.min_cgpa}")

    # 2. Quiz score check (60% threshold)
    if student.quiz_score is None or student.quiz_score < 60:
        reasons.append("Quiz score below 60%")

    # 3. Interview check
    if student.interview_status != "completed":
        reasons.append("Interview not completed")

    # 4. Skills check
    required_skills = [s.strip().lower() for s in company.required_skills.split(",")]
    student_skills = [s.strip().lower() for s in student.skills.split(",")]
    missing = [s for s in required_skills if s not in student_skills]
    if missing:
        reasons.append(f"Missing skills: {', '.join(missing)}")

    # Final decision
    if reasons:
        student.readiness_status = "Not Ready"
        student.missing_skills = "; ".join(reasons)
    else:
        student.readiness_status = "Ready"
        student.missing_skills = None

    db.commit()
    db.refresh(student)
    return student
# ---- STUDENT PROFILE UPDATE ----
@app.put("/students/{student_id}/update-profile", response_model=schemas.StudentResponse)
def update_student_profile(student_id: int, updates: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)

    db.commit()
    db.refresh(student)
    return student

# ==========================================
# READINESS CHECK - AUTOMATIC LOGIC
# ==========================================
def run_readiness_check(student_id: int, db: Session):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student or not student.company_preference:
        return None

    company = db.query(models.Company).filter(
        models.Company.name == student.company_preference
    ).first()
    if not company:
        return None

    # Quiz ke saare answers ka average score nikaalo
    quiz_responses = db.query(models.QuizResponse).filter(
        models.QuizResponse.student_id == student_id
    ).all()
    scores = [r.ai_score for r in quiz_responses if r.ai_score is not None]
    avg_quiz_score = sum(scores) / len(scores) if scores else 0
    student.quiz_score = int(avg_quiz_score)

    # Skills compare karo
    student_skills = set(s.strip().lower() for s in (student.skills or "").split(",") if s.strip())
    required_skills = set(s.strip().lower() for s in (company.required_skills or "").split(",") if s.strip())
    missing = required_skills - student_skills

    cgpa_ok = (student.cgpa or 0) >= (company.min_cgpa or 0)
    quiz_ok = avg_quiz_score >= 5
    interview_ok = student.interview_status == "completed"
    skills_ok = len(missing) == 0

    if cgpa_ok and quiz_ok and interview_ok and skills_ok:
        student.readiness_status = "Ready"
        student.missing_skills = None
    else:
        reasons = []
        if not cgpa_ok:
            reasons.append(f"CGPA kam hai (required: {company.min_cgpa})")
        if missing:
            reasons.append(f"Missing skills: {', '.join(missing)}")
        if not quiz_ok:
            reasons.append("Quiz score kam hai")
        if not interview_ok:
            reasons.append("Interview complete nahi hua")
        student.readiness_status = "Not Ready"
        student.missing_skills = "; ".join(reasons)

    db.commit()
    db.refresh(student)
    return student

# ---- AI GAP ANALYSIS ----
@app.get("/students/{student_id}/gap-analysis")
def get_gap_analysis(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    company = db.query(models.Company).filter(
        models.Company.name == student.company_preference
    ).first()

    if not company:
        raise HTTPException(status_code=400, detail="Company preference not set or company not found")

    advice = analyze_gap(
        student_skills=student.skills,
        required_skills=company.required_skills,
        cgpa=student.cgpa,
        min_cgpa=company.min_cgpa,
        quiz_score=student.quiz_score,
        interview_status=student.interview_status
    )

    return {"student_id": student_id, "advice": advice}

from ai_agent import generate_interview_question, generate_interview_feedback


# ==========================================
# INTERVIEW - AGLA SAWAL LENA (Chat Jaisa)
# ==========================================
@app.post("/interview/{interview_id}/next-question")
def get_next_question(interview_id: int, student_answer: str = "", db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    student = db.query(models.Student).filter(models.Student.id == interview.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Ab tak ki transcript nikaalo (agar hai)
    existing_transcript = interview.transcript or ""

    # Agar student ne answer diya hai, usse transcript mein jodo
    if student_answer:
        existing_transcript += f"\nCandidate: {student_answer}"

    # AI se agla sawal lo
    next_question = generate_interview_question(
        role=student.role_preference or "General",
        student_skills=student.skills,
        conversation_history=existing_transcript
    )

    # Naya sawal transcript mein jodo aur save karo
    updated_transcript = existing_transcript + f"\nInterviewer: {next_question}"
    interview.transcript = updated_transcript
    db.commit()
    db.refresh(interview)

    return {"interview_id": interview_id, "question": next_question}


# ==========================================
# INTERVIEW COMPLETE KARNA (Feedback Automatic)
# ==========================================
@app.put("/interview/{interview_id}/finish")
def finish_interview(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    feedback = generate_interview_feedback(interview.transcript or "")

    interview.status = "completed"
    interview.ai_feedback = feedback
    db.commit()
    db.refresh(interview)

    # Pehle hi poora data ek dictionary mein capture kar lo, return karne ke liye
    result = {
        "id": interview.id,
        "student_id": interview.student_id,
        "status": interview.status,
        "camera_verified": interview.camera_verified,
        "transcript": interview.transcript,
        "ai_feedback": interview.ai_feedback,
    }

    # Ab student ka interview_status update karo
    student = db.query(models.Student).filter(models.Student.id == interview.student_id).first()
    if student:
        student.interview_status = "completed"
        db.commit()

    # NAYI LINE - Interview complete hote hi automatically readiness check karo
    run_readiness_check(interview.student_id, db)

    # Pehle se capture kiya hua data return karo, expired object nahi
    return result

# ==========================================
# ADMIN - POORE BATCH KI READINESS SUMMARY
# ==========================================
@app.get("/admin/readiness-summary")
def get_readiness_summary(db: Session = Depends(get_db)):
    all_students = db.query(models.Student).all()

    ready_list = []
    not_ready_list = []
    not_evaluated_list = []

    for student in all_students:
        student_data = {
            "id": student.id,
            "roll_number": student.roll_number,
            "name": student.name,
            "cgpa": student.cgpa,
            "company_preference": student.company_preference,
            "role_preference": student.role_preference,
            "quiz_score": student.quiz_score,
            "interview_status": student.interview_status,
            "missing_skills": student.missing_skills,
        }

        if student.readiness_status == "Ready":
            ready_list.append(student_data)
        elif student.readiness_status == "Not Ready":
            not_ready_list.append(student_data)
        else:
            # Jinka gap-analysis abhi tak chala hi nahi
            not_evaluated_list.append(student_data)

    return {
        "total_students": len(all_students),
        "ready_count": len(ready_list),
        "not_ready_count": len(not_ready_list),
        "not_evaluated_count": len(not_evaluated_list),
        "ready_students": ready_list,
        "not_ready_students": not_ready_list,
        "not_evaluated_students": not_evaluated_list,
    }

# ==========================================
# ADMIN REGISTER (naya admin banane ke liye)
# ==========================================
@app.post("/admin/register", response_model=schemas.AdminResponse)
def register_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Admin).filter(models.Admin.username == admin.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin username already exists")

    new_admin = models.Admin(
        username=admin.username,
        password=hash_password(admin.password)
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

# ==========================================
# ADMIN LOGIN
# ==========================================
@app.post("/admin/login", response_model=schemas.AdminResponse)
def login_admin(credentials: schemas.AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(models.Admin.username == credentials.username).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not verify_password(credentials.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return admin

# ==========================================
# INTERVIEW - VIOLATION FLAG (Auto-Reject)
# ==========================================
@app.put("/interview/{interview_id}/flag-violation")
def flag_violation(interview_id: int, reason: str, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview.status = "disqualified"
    interview.violation_reason = reason
    interview.ai_feedback = f"Interview disqualified automatically. Reason: {reason}"

    student = db.query(models.Student).filter(models.Student.id == interview.student_id).first()
    if student:
        student.interview_status = "disqualified"

    db.commit()
    db.refresh(interview)

    return {
        "id": interview.id,
        "student_id": interview.student_id,
        "status": interview.status,
        "violation_reason": interview.violation_reason,
    }

# ==========================================
# INTERVIEW - SCREEN SHARE STATUS UPDATE KARNA
# ==========================================
@app.put("/interview/{interview_id}/screen-share-status")
def update_screen_share(interview_id: int, screen_shared: bool, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview.screen_shared = screen_shared
    db.commit()
    db.refresh(interview)

    return {
        "id": interview.id,
        "screen_shared": interview.screen_shared,
    }

# ============================================
# INTERVIEW - SCREEN SHARE STATUS UPDATE
# ============================================
@app.put("/interview/{interview_id}/screen-share")
def update_screen_share(interview_id: int, screen_shared: bool, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    interview.screen_shared = screen_shared
    db.commit()
    db.refresh(interview)

    return {
        "id": interview.id,
        "screen_shared": interview.screen_shared
    }


# ============================================
# INTERVIEW - SUBMIT ANSWER (AI-check + Evaluation)
# ============================================
@app.post("/interview/{interview_id}/submit-answer")
def submit_answer(interview_id: int, question_text: str, student_answer: str, db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Step 1: AI-generated check
    is_suspicious = ai_agent.detect_ai_generated_answer(question_text, student_answer)

    if is_suspicious:
        interview.status = "disqualified"
        interview.violation_reason = "AI-generated answer detected"
        db.commit()
        db.refresh(interview)
        return {
            "id": interview.id,
            "status": interview.status,
            "violation_reason": interview.violation_reason,
            "score": None
        }

    # Step 2: Genuine answer -> evaluate correctness
    score = ai_agent.evaluate_interview_answer(question_text, student_answer)

    interview.total_score = (interview.total_score or 0) + score
    interview.answers_count = (interview.answers_count or 0) + 1
    db.commit()
    db.refresh(interview)

    return {
        "id": interview.id,
        "status": interview.status,
        "answer_score": score,
        "total_score": interview.total_score,
        "answers_count": interview.answers_count
    }

# ==========================================
# ADMIN - VIOLATIONS / DISQUALIFIED LIST
# ==========================================
@app.get("/admin/violations")
def get_violations(db: Session = Depends(get_db)):
    disqualified_interviews = db.query(models.Interview).filter(
        models.Interview.status == "disqualified"
    ).all()

    violations_list = []
    for interview in disqualified_interviews:
        student = db.query(models.Student).filter(
            models.Student.id == interview.student_id
        ).first()

        violations_list.append({
            "interview_id": interview.id,
            "student_id": interview.student_id,
            "student_name": student.name if student else "Unknown",
            "roll_number": student.roll_number if student else "Unknown",
            "violation_reason": interview.violation_reason,
            "screen_shared": interview.screen_shared,
            "camera_verified": interview.camera_verified,
        })

    return {
        "total_disqualified": len(violations_list),
        "violations": violations_list,
    }