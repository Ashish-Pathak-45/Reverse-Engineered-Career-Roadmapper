# Skill Assessment Methodology

PATHFORGE scores answers **server-side and deterministically** (no AI involved, no randomness).

| Rule | Value |
| :-- | :-- |
| Minimum evidence for a level | 3 answered questions per skill, otherwise **"Insufficient evidence"** |
| A tier is *demonstrated* | >= 2 attempts in that tier and accuracy >= 70% |
| Level | highest demonstrated tier, only if every lower attempted tier has accuracy >= 50% |
| No tier demonstrated | overall accuracy >= 40% -> Beginner, else **Needs foundations** |
| Confidence | low (<5 answers), medium (5-7), high (>=8) |
| Adaptive difficulty | start Intermediate; 2 correct in a row at a tier -> next tier up; 2 wrong in a row -> down; otherwise unchanged |

Skills are evaluated independently (Python, Databases, Algorithms, Machine Learning). Self-reported skills are never treated as verified.

## Roadmap personalization (`POST /api/roadmaps/{id}/personalize`)
- Demonstrated skill at or above a node's tier with medium+ confidence -> node hours x0.5 (fast-track).
- Needs foundations / Beginner on an harder node -> hours x1.3 plus a practice note; downstream nodes are flagged as prerequisite gaps; completed nodes in a weak area become `needs_revision`.
- Insufficient evidence or low confidence -> no change. The call is idempotent (always recomputed from original hours).

## Endpoints
`GET /api/assessments/adaptive/skills`, `GET .../next?skill=`, `POST .../answer`, `GET .../profile` (all under `/api/assessments/adaptive`).

## Limitations
Multiple-choice quizzes measure recall and reasoning only, not communication, project work or real-world readiness. The question bank is small (6 per skill, 4 for ML) and should be expanded. Results are a learning aid, not a certification or hiring prediction.
