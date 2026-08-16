# AI Placement Readiness Agent

Brainwave 2026 Hackathon — Problem Statement 3 (Open Innovation)

An AI-powered backend that helps students check their placement readiness. Students register, set their company/role preference, take a role-based quiz, and go through a text-based AI interview. The system automatically evaluates CGPA, quiz score, interview performance, and skill match to mark a student **Ready** or **Not Ready**, with a personalized AI-generated improvement plan. Admins get a batch-wide readiness summary.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL + SQLAlchemy ORM (SQLite fallback for local development)
- **AI:** Google Gemini API (`google-genai`)
- **Validation:** Pydantic
- **Auth:** Bcrypt password hashing
- **Deployment:** Render (backend + PostgreSQL)

## Features

- Student register/login with secure password hashing
- Company & role preference confirmation
- Role-based quiz with AI auto-grading
- AI-driven chat-style interview with automatic feedback
- Automatic readiness check (Ready / Not Ready + reasons)
- AI-generated personalized improvement advice (gap analysis)
- Admin dashboard summary endpoint (batch-wide Ready/Not-Ready view)
- Admin authentication, interview violation flagging, and screen-share tracking
- Automatic retry handling for AI API rate limits/overload

## Running Locally

1. Clone the repo and create a virtual environment