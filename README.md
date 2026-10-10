THFORGE AI --- Career Roadmapper

Problem Statement 1: Reverse-Engineered Career Roadmapper

PATHFORGE AI helps students turn a specific career goal into a
structured learning roadmap. It brings career planning,
prerequisite-aware roadmap visualization, skill assessment, and progress
tracking into one experience.

Live demo: https://careerroadmapper.netlify.app/

GitHub repository:
https://github.com/Ashish-Pathak-45/Reverse-Engineered-Career-Roadmapper

Status note: Verify the current production backend and each UI
flow before submission. A deployed frontend alone does not prove that
backend-dependent features work in production.

The problem

Career advice is often generic. Students may know their target role but
not which skills to learn first, which prerequisites matter, how to
evaluate their current ability, or how to measure progress.

PATHFORGE AI addresses Problem Statement 1 --- Reverse-Engineered
Career Roadmapper by organizing career preparation into a more
concrete, navigable sequence of skills and milestones.

What it does

PATHFORGE AI is a career-planning application intended to connect a
student's career direction with a structured learning path. Roadmap
dependencies show which skills should be approached first. Assessment
functionality helps estimate proficiency and identify areas that need
more practice.

It aims to help students answer: 1. What should I learn for my target
career? 2. What should I work on next? 3. How can I track progress and
identify skill gaps?

Key features

The backend and project workspace have included the following
capabilities. Verify each one in the submitted build and remove or
relabel anything that is incomplete.

Interactive career roadmaps: Explore skills and milestones in a
graph-style view.

Prerequisite relationships: Represent dependencies between
roadmap skills.

Progress states: Roadmap nodes can represent states such as
available, completed, or locked, where supported by the current UI.

Skill assessments: Assess understanding of selected topics.

Adaptive difficulty logic: The backend assessment service
supports Easy, Medium, and Hard difficulty transitions and is
designed to avoid changing difficulty based on a single answer.

Skill proficiency tracking: The backend data model supports
storing attempts, correct answers, accuracy, proficiency level, and
current difficulty.

Roadmap integration: Assessment outcomes can be connected to
roadmap skills through backend logic.

Browser-based interface: The frontend is deployed at the
live-demo URL above.

Limitations to disclose

Verify that the deployed frontend is connected to the intended
production backend.

Verify that assessments, saved progress, and database-backed
features work on the public site.

Do not claim that a feature uses an LLM or a particular AI model
unless the current code actually calls it.

If Success Stories or another section is incomplete or uses
placeholder content, state that clearly.

How the assessment works

The backend has included an adaptive assessment service and question
bank. The assessment design supports this flow:

Select an available track or topic.

Receive questions appropriate to the selected track and difficulty.

Submit answers for backend evaluation.

Score performance across dimensions including conceptual
understanding, problem solving, accuracy, and consistency.

Adjust difficulty between Easy, Medium, and Hard based on
performance.

Store skill-level metrics and proficiency categories.

Connect assessment outcomes to roadmap skills where the integration
is enabled.

This describes the backend design. Confirm that the current frontend
calls these endpoints and that the production backend is connected
before describing the complete flow as verified live functionality.

Done, left, and plan

Update this section to match the exact commit submitted for judging.

Done / implemented in the project

React, TypeScript, and Vite frontend.

FastAPI backend with separate API route modules.

Roadmap-related data models and services.

Adaptive assessment logic and a question bank.

Models for roadmaps, roadmap nodes/edges, assessment results, and
skill proficiency.

Public frontend deployment at the live-demo URL.

Left to verify before submission

Confirm the latest source code is pushed to GitHub.

Confirm the production frontend calls the deployed backend, not
localhost.

Test the main flow: open a roadmap, complete an assessment, view
results, and refresh the page.

Confirm data persists across backend restarts and redeployments.

Test Success Stories and other unfinished UI areas.

Check that no secrets or private configuration values are committed.

Plan

Prioritize reliability: verify the complete deployed student flow, test
error handling and mobile layout, check basic accessibility, and keep
this README aligned with the code.

Architecture and why

Layer                   Technology              Purpose

Frontend                React 18, TypeScript,   Browser interface
Vite

Roadmap visualization   React Flow, if present  Interactive graph and
in the current frontend dependency
dependencies            visualization

Backend API             FastAPI                 Roadmap, assessment,
and related endpoints

Runtime                 Python and Uvicorn      Run the backend API

Data access             SQLAlchemy              Database models and
persistence

Validation/settings     Pydantic and Pydantic   Validate data and
Settings                manage configuration

Local database          SQLite                  Local application data

flowchart TD
    Student[Student in browser] --> UI[React + TypeScript frontend]
    UI --> API[FastAPI backend]
    API --> Routes[Roadmap and assessment routes]
    Routes --> Services[Assessment engine and application services]
    Services --> Models[SQLAlchemy models / data access]
    Models --> DB[(SQLite database)]

Separating the frontend from backend logic keeps the UI distinct from
assessment and data handling. A graph is useful for career planning
because it makes prerequisites easier to understand than a flat
checklist.

Production note: SQLite is convenient for local development. On a
hosted service, ensure the database uses persistent storage or migrate
to a managed database; an ephemeral container filesystem can lose data
during redeploys or restarts.

Project structure

The backend paths below reflect the project structure previously
inspected. Update this tree if the current repository differs.

Reverse-Engineered-Career-Roadmapper/
├── frontend/
│   ├── package.json
│   └── src/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── tests/
│   └── pathforge.db       # Local database, if present; do not commit private data
├── .gitignore
└── README.md

frontend/: web application and frontend dependencies.

backend/app/main.py: FastAPI entry point, based on the previously
inspected structure.

backend/app/api/: API route modules.

backend/app/models/: database and application models.

backend/app/services/: application and assessment logic.

backend/app/tests/: backend tests, if present.

backend/pathforge.db: local SQLite database, if present. Do not
commit personal or private data.

Run locally

Prerequisites

Git

Node.js and npm

Python 3.11 or 3.12, subject to the backend's configured version

1. Clone the repository

git clone https://github.com/Ashish-Pathak-45/Reverse-Engineered-Career-Roadmapper.git
cd Reverse-Engineered-Career-Roadmapper

2. Start the backend

cd backend
python -m venv .venv

Activate on Windows PowerShell:

.\.venv\Scripts\Activate.ps1

Activate on macOS/Linux:

source .venv/bin/activate

Install the dependency file present in backend/. If it contains
requirements.txt:

python -m pip install -r requirements.txt

If backend/app/main.py exposes app = FastAPI(...), a typical command
from the backend/ directory is:

uvicorn app.main:app --reload

Check the actual entry point and configuration before relying on this
example command.

3. Start the frontend

Open a second terminal:

cd frontend
npm install
npm run dev

Open the local URL printed by Vite, commonly http://localhost:5173.

If the frontend uses an environment variable for its API URL, set it to
the local backend origin using the exact variable name defined in the
source code. Do not commit secrets.

Configuration and security

Keep API keys, passwords, tokens, and credentials out of source
control.

Use .env.example with placeholder values only.

Configure the production frontend to use the deployed backend URL,
not localhost.

Configure backend CORS for the intended frontend origin.

Do not commit .env files or a database containing personal/private
data.

Verify the actual environment-variable names in the frontend API
client and backend settings.

Example placeholder only (verify the variable name in code before using
it):

VITE_API_BASE_URL=http://127.0.0.1:8000

API documentation

The backend has included route groups for authentication, roadmaps,
assessments, professionals, projects, feedback, and mentoring-related
functionality. Confirm the current routers and prefixes in
backend/app/main.py before relying on this list.

When the backend is running, the default FastAPI documentation URLs are
usually:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

These pages are available only if the application has not disabled or
changed the default documentation routes. Inspect the route modules or
OpenAPI page for exact methods and request schemas.

Testing

Run the tests available in the current checkout. If the backend uses
pytest:

python -m pytest

Inspect frontend/package.json for the available scripts. A typical
Vite production build is:

npm run build

Report test counts and successful results only after running the
commands against the submitted commit.

Deployment

Frontend: https://careerroadmapper.netlify.app/

Source repository:
https://github.com/Ashish-Pathak-45/Reverse-Engineered-Career-Roadmapper

Backend: Add the verified public backend URL once deployed and
tested.

For production: 1. Build the frontend using the script in
frontend/package.json. 2. Configure its API base URL to the verified
backend URL. 3. Configure backend CORS to allow the deployed frontend
origin. 4. Configure persistent database storage or use a managed
database. 5. Store secrets in the hosting provider's environment
settings. 6. Test the main student flow, error cases, and page refresh
on the public site.

A successful frontend deployment does not prove backend-dependent
features are working. Verify the full browser-to-API-to-database flow.

Tools and AI used

The project uses a React/TypeScript frontend and a Python/FastAPI
backend. The backend contains adaptive assessment logic and a question
bank.

Before submission, add or correct the exact AI models, external APIs,
libraries, and AI-assisted development tools used in the current
project. Explain how users are informed when content is AI-generated, if
applicable. Do not claim a particular model powers a feature unless the
code actually calls it. Adaptive rules alone do not prove that an LLM is
used.

Who it is for

PATHFORGE AI is intended for college students and early-career learners
who have a target role in mind but need help turning it into a practical
learning sequence. It can help them plan what to study, evaluate
proficiency, and return to a roadmap to track progress.

Future improvements

Depending on what remains incomplete, potential improvements include:

Verify and strengthen the assessment-to-roadmap workflow.

Improve recommendations using assessment evidence and explicit skill
gaps.

Ensure reliable persistence for profiles, results, and progress.

Improve mobile usability, keyboard navigation, and accessible
labels.

Explain proficiency estimates and recommendations transparently.

Expand learning resources and project suggestions for each
milestone.

Add end-to-end tests for the most important student journeys.

Built as a student-focused hackathon project for Problem Statement 1:
Reverse-Engineered Career Roadmapper.
