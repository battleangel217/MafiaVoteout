# 🎭 Mafia Voteout

> A real-time multiplayer social deduction game — built with WebSockets, Redis, Django, and an AI agent that helps players hunt the mafia.

**[▶ Play Live](https://mafiavoteout.onrender.com)** | **[How to Play](https://mafiavoteout.onrender.com/how-to-play.html)**

---

## What is this?

Mafia Voteout is an online multiplayer version of the classic Mafia/Werewolf party game. Players join rooms, get assigned secret roles (Mafia or Villager), and must vote out the mafia before the mafia eliminates the town.

The twist: an AI agent named **@idara** lives inside the game chat. Players can summon it during voting to get AI-powered suspicion analysis — though it's not always right, which keeps things interesting.

---

## Features

- 🔴 **Real-time multiplayer** — WebSocket-powered gameplay with live phase transitions, voting, and elimination
- 🤖 **In-game AI agent** — type `@idara` in the voting arena to get AI-driven mafia suspicion analysis (Gemini 2.0 Flash)
- 💬 **AI Guide chatbot** — floating assistant on the How to Play page answers rules questions
- 🏠 **Public & Private rooms** — public rooms are browsable; private rooms need a code
- 👑 **Admin controls** — room creator manages game start and lobby
- ⏱️ **Timed phases** — Day phase (2 min voting), Night phase (1 min mafia kill)
- 🎭 **Role assignment** — mafia badge and kill button appear only for mafia players
- 📋 **Available rooms list** — browse and join open public lobbies

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django, Django Channels |
| Real-time | WebSockets (Django Channels) |
| Cache / Pub-Sub | Redis |
| Database | PostgreSQL |
| AI Integration | Google Gemini 2.0 Flash |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Hosting | Render |

---

## Architecture Overview

```
Client (Browser)
     │
     │  WebSocket connection
     ▼
Django Channels (ASGI)
     │
     ├── Redis (channel layer / pub-sub for room state)
     │
     ├── PostgreSQL (persistent game data)
     │
     └── Gemini API (AI agent responses on @idara mention)
```

Game state (phases, votes, players, roles) is managed server-side and broadcast to all room members in real time. Role assignment happens server-side on game start and is never exposed to the wrong client.

---

## Game Flow

```
Players join lobby
       │
  Admin starts game
       │
  Roles assigned secretly
       │
  ┌────▼─────────────────┐
  │     DAY PHASE (2min) │ ← All players discuss & vote
  │  @idara AI available │
  └────────┬─────────────┘
           │ Player with most votes eliminated
  ┌────────▼─────────────┐
  │   NIGHT PHASE (1min) │ ← Mafia picks a target
  └────────┬─────────────┘
           │ Innocent eliminated
           │
  Repeat until:
  - All mafia eliminated → Town wins 🏆
  - Mafia = Innocents → Mafia wins 🔪
```

---

## Local Development

```bash
# Clone the repo
git clone https://github.com/battleangel217/MafiaVoteout.git
cd MafiaVoteout

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Fill in: SECRET_KEY, DATABASE_URL, REDIS_URL, GEMINI_API_KEY

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

> Make sure Redis is running locally (`redis-server`) before starting.

---

## Environment Variables

```env
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379
GEMINI_API_KEY=your_gemini_api_key
DEBUG=True
```

---

## Origin Story

This project started as a terminal-based Python game — players typed commands in the CLI to vote and eliminate. Over time it evolved into a full web application with real-time multiplayer, persistent game state, and AI integration. The core game logic remained the same; the infrastructure around it grew into something genuinely production-grade.

---

## Author

**Idaraobong Joseph** — Full Stack Developer  
[Portfolio](https://idaraobong.vercel.app) · [LinkedIn](https://linkedin.com/in/idaraobong-etim-998328295) · [Twitter/X](https://x.com/idaraobong217)

---

## License

MIT