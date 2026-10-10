# AptiQuiz 🎯
### Multiplayer Aptitude Quiz Platform

AptiQuiz is a web application where students can play aptitude and logical reasoning quizzes together in real time. Instead of solving questions alone, students can join a room, compete with their friends, and see their scores on a live leaderboard.

The main idea is to make aptitude practice more interesting while helping students improve their speed and accuracy for placement tests.

**Problem Statement:** 3 — AptiQuiz

---

## What does it do?

- Students can join a quiz using a room code.
- The host can create quizzes and manage questions.
- Everyone answers the same questions within a time limit.
- Points are awarded for correct answers, with faster answers earning more points.
- A live leaderboard shows the current rankings.
- Players can check their final scores and performance after the quiz.
- The platform is designed to support up to 50 players in one room.

## Current Progress

### Done
- [ ] Dashboard UI
- [ ] Navigation and page layout

### Still working on
- [ ] Creating and joining quiz rooms
- [ ] Adding and managing questions
- [ ] Real-time multiplayer functionality
- [ ] Timer and scoring system
- [ ] Live leaderboard
- [ ] Saving quiz results
- [ ] Player reconnection
- [ ] Testing with 50 players
- [ ] Deployment

I'll update this section as more features are completed.

## Tech Stack

The project uses the following technologies:

- **React** – for building the frontend
- **Tailwind CSS** – for styling and responsive layouts
- **Node.js** – for the backend
- **Express.js** – for handling API requests
- **Socket.IO** – for real-time communication
- **PostgreSQL / Supabase** – for storing questions, players, and results
- **Recharts** – for displaying performance charts

The final stack may change as development progresses.

## How it works

1. The host creates a quiz and starts a room.
2. Other players join using the room code.
3. Once the host starts the game, questions appear for everyone.
4. Players submit their answers before the timer runs out.
5. The server checks the answers and calculates the scores.
6. The leaderboard updates after each question.
7. At the end, everyone can see the final results.

## What makes it useful?

Most students prepare for aptitude tests by solving questions from books, PDFs, or practice websites. AptiQuiz adds a competitive element to this process.

The goal is to help students practise under time pressure, compare their performance with others, and find the topics they need to work on.

Some features we plan to add include:

- Topic-wise performance analysis
- Daily aptitude challenges
- College leaderboards
- Team competitions
- A dashboard for teachers to review quiz results

## Running the Project Locally

### Requirements

- Node.js and npm
- Git

### Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd aptiquiz
