import requests

BASE_URL = "http://127.0.0.1:8000"

# ==========================================
# 1. COMPANIES ADD KARO
# ==========================================
companies = [
    {"name": "TCS", "role": "Software Engineer", "required_skills": "Python, SQL, Communication", "min_cgpa": 7.0},
    {"name": "Infosys", "role": "Data Analyst", "required_skills": "Python, Excel, SQL, Statistics", "min_cgpa": 7.5},
    {"name": "Wipro", "role": "Software Engineer", "required_skills": "Java, React, SQL", "min_cgpa": 6.5},
    {"name": "Accenture", "role": "Cloud Engineer", "required_skills": "AWS, Docker, Python", "min_cgpa": 7.0},
]

print("Companies add ho rahi hain...")
for c in companies:
    res = requests.post(f"{BASE_URL}/companies", json=c)
    print(f"  {c['name']} -> {res.status_code}")


# ==========================================
# 2. STUDENTS REGISTER KARO
# ==========================================
students = [
    {
        "roll_number": "STU001", "password": "pass123", "name": "Rahul Sharma",
        "cgpa": 8.2, "skills": "Python, React, SQL", "projects": "Portfolio website, E-commerce app",
        "certifications": "AWS Basics", "company_preference": "TCS", "role_preference": "Software Engineer"
    },
    {
        "roll_number": "STU002", "password": "pass123", "name": "Priya Verma",
        "cgpa": 7.8, "skills": "Python, Excel, SQL, Statistics", "projects": "Sales data dashboard",
        "certifications": "Data Analytics Certificate", "company_preference": "Infosys", "role_preference": "Data Analyst"
    },
    {
        "roll_number": "STU003", "password": "pass123", "name": "Amit Kumar",
        "cgpa": 6.9, "skills": "Java, HTML, CSS", "projects": "Simple calculator app",
        "certifications": "", "company_preference": "Wipro", "role_preference": "Software Engineer"
    },
    {
        "roll_number": "STU004", "password": "pass123", "name": "Sneha Reddy",
        "cgpa": 8.5, "skills": "AWS, Docker, Python, Linux", "projects": "Cloud deployment pipeline",
        "certifications": "AWS Solutions Architect", "company_preference": "Accenture", "role_preference": "Cloud Engineer"
    },
    {
        "roll_number": "STU005", "password": "pass123", "name": "Karan Singh",
        "cgpa": 7.2, "skills": "Python, SQL", "projects": "Student management system",
        "certifications": "", "company_preference": "TCS", "role_preference": "Software Engineer"
    },
]

print("\nStudents register ho rahe hain...")
for s in students:
    res = requests.post(f"{BASE_URL}/register", json=s)
    print(f"  {s['name']} -> {res.status_code}")


# ==========================================
# 3. QUIZ QUESTIONS ADD KARO (Role-wise)
# ==========================================
questions = [
    {"role": "Software Engineer", "question_text": "Explain OOPS concepts in your own words"},
    {"role": "Software Engineer", "question_text": "What is the difference between SQL and NoSQL databases?"},
    {"role": "Data Analyst", "question_text": "How would you handle missing data in a dataset?"},
    {"role": "Data Analyst", "question_text": "Explain the difference between mean, median, and mode"},
    {"role": "Cloud Engineer", "question_text": "What is the difference between AWS EC2 and S3?"},
]

print("\nQuiz questions add ho rahe hain...")
for q in questions:
    res = requests.post(f"{BASE_URL}/quiz/questions", params=q)
    print(f"  {q['role']} - {q['question_text'][:30]}... -> {res.status_code}")

print("\nSab kuch daal diya gaya! ✅")