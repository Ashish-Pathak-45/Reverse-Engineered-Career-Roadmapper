# PATHFORGE AI — Adaptive Career Intelligence Platform

> **"Your Dream Career. Your Roadmap. Your Future."**

[![Theme](https://img.shields.io/badge/Design%20Theme-Theme%206%20Minimalist%20AI%20Professional-2563EB)](#visual-design-system)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11-16A34A)](#backend-architecture)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Vite-7C3AED)](#frontend-architecture)
[![Database](https://img.shields.io/badge/Database-SQLAlchemy%20%7C%20SQLite%20%2F%20PostgreSQL-2563EB)](#database-design)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Gemini%20Pro%20%2B%20Heuristic%20Intelligence-D97706)](#ai-engine--dual-mode)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-16A34A)](#testing)

---

## 1. Executive Summary & Vision

**PATHFORGE AI** is a full-stack, AI-powered career intelligence web platform designed to help university students and job seekers transform their career goals into personalized, practical, and achievable engineering roadmaps.

Unlike static course listicles or generic advice generators, PATHFORGE AI builds **Directed Acyclic Graphs (DAGs)** that enforce prerequisite relationships. Advanced specializations remain locked until foundational milestones are mastered and backed by code deliverables in a verified **Career Evidence Portfolio**.

---

## 2. 12 Core Platform Capabilities

1. **AI Career Roadmap Generator**: Synthesizes custom engineering roadmaps adapting to target job title, company tier, current skills, weekly study bandwidth, and timeline.
2. **Interactive Career Graph Visualization**: Interactive React Flow visual DAG supporting pan, zoom, node inspection, prerequisite lines, fit-to-screen, and a responsive timeline view.
3. **Prerequisite Dependency Engine**: Deterministic backend dependency validation enforcing that downstream milestones cannot be marked complete until all prerequisite nodes are satisfied.
4. **Adaptive Replanning Engine**: Dynamically recalibrates remaining hours and unlocks eligible milestones when students adjust weekly study hours or report newly mastered skills.
5. **Success Stories — Real Career Journeys**: Documented public career journeys of verified technology leaders (*Demis Hassabis, Andrej Karpathy, Fei-Fei Li, Mira Murati, Satya Nadella, Linus Torvalds*) backed by official university directories and citations.
6. **Success-Path Comparison**: Side-by-side comparative analysis between a student's active roadmap and a professional's documented historical milestones.
7. **Advanced Skill Gap Analyzer**: Compares baseline student proficiencies against target role benchmarks, providing estimated hours and actionable priorities.
8. **Diagnostic Assessments & Quizzes**: Structured conceptual evaluations (ML, DSA, SQL) with instant scoring, weakness topic analysis, and detailed question explanations.
9. **AI Project Architect**: Industry-grade project blueprints featuring problem statements, tech stacks, testing strategies, evaluation metrics, and interview defense questions.
10. **Career Evidence Portfolio**: Secure repository associating GitHub repositories, deployed URLs, and technical demos with roadmap skills, featuring automated link validation.
11. **Contextual AI Career Mentor**: Real-time assistant calibrated with the user's active milestone, completed nodes, and target role to deliver actionable advice.
12. **User Feedback & Protected Admin Governance**: 5-star rating and category feedback submission with a server-side protected Administrator Dashboard (`/admin/feedback`) for status tracking and metrics.

---

## 3. Visual Design System (Theme 6: Minimalist AI Professional)

The interface adheres to **Theme 6 — Minimalist AI Professional**, crafted for high-trust technology products:

| Token | Hex Value | Usage |
| :--- | :--- | :--- |
| **Primary Background** | `#FFFFFF` | Main canvas, cards, and modal sheets |
| **Secondary Background**| `#F7F9FC` | Sidebars, badges, table headers, and inputs |
| **Primary Text** | `#172033` | Headings, titles, and primary emphasis text |
| **Secondary Text** | `#667085` | Descriptions, metadata, and subtitle labels |
| **Primary Accent** | `#2563EB` | Primary buttons, active tabs, and forward progress |
| **Secondary Accent** | `#7C3AED` | Purple highlight for AI mentor and specialized badges |
| **Success** | `#16A34A` | Verified milestones, passed tests, and completed items |
| **Warning** | `#D97706` | Milestone revision notices and prerequisite alerts |
| **Border** | `#E5E7EB` | Subtle structural borders (1px) |

- **Typography**: Inter (Google Fonts) with strong visual hierarchy and compact analytics labels.
- **Micro-Animations**: Subtle CSS transitions, DAG edge animations, and celebratory milestone confetti (`canvas-confetti`).

---

## 4. System Architecture

```
                                  [ Client Browser ]
                                          |
                        +-----------------+-----------------+
                        |                                   |
              [ React 18 + Vite SPA ]             [ React Flow DAG Canvas ]
                        |                                   |
                        +-----------------+-----------------+
                                          | HTTP / JSON REST
                                          v
                              [ FastAPI Backend Router ]
                                          |
        +------------------+--------------+---------------+------------------+
        |                  |                              |                  |
  [ Auth & RBAC ]    [ Graph DAG Engine ]         [ AI Dual-Engine ]   [ Admin Governance ]
        |                  |                              |                  |
        |                  |                     +--------+--------+         |
        |                  |                     |                 |         |
        |                  |               [ Gemini API ]    [ Heuristic ]   |
        |                  |                                                 |
        +------------------+--------------+----------------------------------+
                                          | SQLAlchemy ORM
                                          v
                             [ Relational Database ]
                          (SQLite local / PostgreSQL prod)
```

---

## 5. Database Schema & Models

Normalized relational models implemented with SQLAlchemy:

1. **`users`**: User identity, hashed passwords (bcrypt), active flags, and `is_admin` role flag.
2. **`user_profiles`**: Education level, degree, graduation year, target career, technical skills, and weekly study hours.
3. **`roadmaps`**: Title, dream job, target company, timeline, weekly hours, current phase, and completion criteria.
4. **`roadmap_nodes`**: Milestone key, category, difficulty, estimated hours, lock/available/completed status, deliverable, and criteria.
5. **`roadmap_edges`**: Directed prerequisite connections connecting source and target nodes.
6. **`weekly_sprints`**: Weekly goals, daily task checklists, planned vs completed hours.
7. **`professional_profiles`**: Verified public biographies, category, summary, and verification date.
8. **`professional_milestones`**: Chronological career milestones and milestone types.
9. **`professional_skills`**: Skills categorized as `documented_role`, `public_work`, or `inferred`.
10. **`assessments` & `assessment_results`**: Question banks, scores, weak topics, and answers.
11. **`project_recommendations` & `project_evidence`**: Project blueprints and student evidence portfolio.
12. **`feedbacks` & `feedback_status_history`**: Multi-dimensional ratings, comments, and admin audit log.
13. **`resources` & `saved_resources`**: Curated educational materials with verified dates.

---

## 6. Pre-Seeded Accounts for Testing

The platform automatically seeds two ready-to-test accounts upon startup:

| Account | Email | Password | Role & Capabilities |
| :--- | :--- | :--- | :--- |
| **Demo Student** | `student@pathforge.ai` | `StudentPass123!` | Standard user: roadmaps, portfolio, quizzes |
| **Platform Administrator**| `admin@pathforge.ai` | `AdminPass123!` | Admin: full access to Admin Feedback Dashboard |

*(One-click login buttons are also available inside the Sign In modal for zero-friction evaluation!)*

---

## 7. Local Setup & Execution Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ (tested on Node v20.18.0)
- npm 9+

### Step 1: Start Backend
```powershell
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run FastAPI with Uvicorn
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API docs are immediately accessible at: `http://127.0.0.1:8000/docs`*

### Step 2: Start Frontend
```powershell
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Vite dev server
npm run dev
```
*Frontend application is immediately accessible at: `http://localhost:5173`*

---

## 8. Automated Testing

Run the comprehensive pytest suite verifying authentication, JSON schemas, prerequisite graph logic, milestone progression, and server-side admin protection:

```powershell
cd backend
python -m pytest -v app/tests
```

**Test Coverage Highlights:**
- `test_auth.py`: User registration, JWT login, profile retrieval, invalid credentials rejection.
- `test_roadmaps.py`: Structured roadmap generation, prerequisite dependency blocking (preventing locked nodes from completing), and milestone progress recalculation.
- `test_feedback.py`: Feedback submission, privacy protection (email stripped in public schema), and RBAC enforcement (ensuring non-admins receive `403 Forbidden` on admin endpoints).

---

## 9. AI Integration & Dual-Engine Operation

PATHFORGE AI features a resilient dual-mode architecture:
1. **Google Gemini LLM**: When `GEMINI_API_KEY` is provided in `.env`, the system utilizes Gemini to craft dynamic roadmaps, projects, and contextual mentor dialogues.
2. **Heuristic Career Intelligence Fallback**: If no API key is configured or an external network timeout occurs, the platform automatically engages its deterministic career taxonomy engine. This guarantees **100% operational functionality** with zero downtime or broken screens.

---

## 10. Security & Privacy Considerations

- **Server-Side Authorization**: Administrative routes check `user.is_admin` directly on the server; client-side role manipulation is rejected with HTTP 403.
- **Privacy By Default**: Student feedback comments and email addresses remain strictly confidential unless explicit consent is checked for public reviews.
- **Safe Secrets Handling**: No API keys or credentials are baked into frontend bundles; all environment variables are loaded via server-side configuration.

---

## 11. Production Deployment

A production frontend build can be compiled via:
```powershell
cd frontend
npm run build
```
The output `dist/` directory can be served via Nginx, Cloudflare Pages, or FastAPI's `StaticFiles`. The backend is container-ready for Docker, AWS ECS, or Render with PostgreSQL.
