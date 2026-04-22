# MafiaVoteout

MafiaVoteout is a multiplayer social deduction game where players join a room, chat, and vote to eliminate suspected mafia members.

## Tech Stack

- **Backend:** Django, Django REST Framework, Django Channels, Redis
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **AI helper:** Google Gemini API

## Project Structure

```
MafiaVoteout/
├── backend/   # Django API + WebSocket server
└── frontend/  # Static client pages
```

## Core Features

- Create and join game rooms
- Public room listing
- Real-time lobby chat and player presence
- Real-time voting and elimination flow
- AI game helper endpoint and in-game AI mention support

## Backend Setup (Local)

1. Go to backend:
   - `cd /home/runner/work/MafiaVoteout/MafiaVoteout/backend`
2. Create and activate a virtual environment.
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Set environment variables:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `REDIS_URL`
   - `GEMINI_API_KEY`
5. Run migrations:
   - `python manage.py migrate`
6. Start the ASGI server:
   - `daphne Games.asgi:application`

## Frontend Setup (Local)

1. Go to frontend:
   - `cd /home/runner/work/MafiaVoteout/MafiaVoteout/frontend`
2. Serve the files with any static server (example):
   - `python -m http.server 5502`
3. Open `http://127.0.0.1:5502/index.html`.

> Note: frontend requests currently target the deployed backend domain in JS files. Update those URLs if you want full local backend usage.

## API Routes

Base path: `/api/v1/`

- `room/` - create/get/start/delete rooms
- `room/all` - list public rooms
- `player/` - create/list players
- `health/` - health check
- `aiagent/` - AI guide response endpoint

## WebSocket Routes

- `/ws/lobby/<code>/` - lobby updates/chat
- `/ws/voting/<code>/` - voting round updates/chat

## Running Tests

From backend:

- `python manage.py test`

If Django is not installed in your environment, install dependencies first with `pip install -r requirements.txt`.
