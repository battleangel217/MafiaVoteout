# Mafia Voteout 🎭

Mafia Voteout is an engaging, multiplayer social deduction game where players work to uncover the hidden Mafia members among them before they are eliminated. Built with a robust Django backend and a responsive vanilla JavaScript frontend, it features real-time interaction, live voting, and AI-powered assistance.

## 🌟 Features

*   **Social Deduction Gameplay:** Classic Mafia/Werewolf mechanics with Villager and Mafia roles.
*   **Real-time Interaction:** Seamless live chat, voting, and game status updates using WebSockets (Django Channels).
*   **Game Rooms:** Create private rooms for friends or join public lobbies to play with anyone.
*   **Game Phases:** Automated Day (discussion & voting) and Night (mafia elimination) cycles with synchronized timers.
*   **AI Guide (Idara):** An integrated AI assistant powered by **Google Gemini** that can answer questions about the game and provide strategies during the voting phase.
*   **Cross-Link & Invite:** Simple room code system to easily invite friends.

## 🛠️ Tech Stack

### Backend
*   **Framework:** Django & Django REST Framework (DRF)
*   **Real-time:** Django Channels (with Redis) & Daphne/Uvicorn
*   **Authenticaton:** Custom player session management
*   **AI Integration:** Google Gemini API
*   **Database:** SQLite (Default) / PostgreSQL (Production ready)

### Frontend
*   **Core:** HTML5, CSS3, Vanilla JavaScript
*   **Styling:** Custom CSS with responsive design

## 🚀 Getting Started

Follow these instructions to set up the project locally.

### Prerequisites
*   Python 3.10+
*   Redis (Required for Channel Layers)
*   Google Gemini API Key (for AI features)

### Installation

1.  **Clone the repository**
    ```bash
    git clone <your-repo-url>
    cd <your-project-folder>
    ```

2.  **Set up a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    Navigate to the backend directory and install the requirements.
    ```bash
    cd backend
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the `backend` directory with the following keys:
    ```env
    SECRET_KEY=your_django_secret_key
    GEMINI_API_KEY=your_google_gemini_api_key
    ```

5.  **Apply Migrations**
    ```bash
    python manage.py migrate
    ```

6.  **Run the Server**
    Since this project uses WebSockets, use `daphne` or `python manage.py runserver` (if configured with daphne).
    ```bash
    python manage.py runserver
    ```
    The API will run at `http://127.0.0.1:8000/`.

### Running the Frontend
The frontend consists of static files. You can simply open `frontend/index.html` in your browser, or serve it using a lightweight server like "Live Server" in VS Code or Python's http server:
```bash
cd ../frontend
python -m http.server 5500
```

## 🕹️ How to Play

1.  **Create a Room:** Enter your username and choose "Public" or "Private" to generate a game room.
2.  **Invite Players:** Share the unique 6-digit Room Code with friends.
3.  **Start Game:** Once everyone is in the lobby (admin controls), start the game.
4.  **Day Phase:** Discuss in the chat who you suspect. Vote to eliminate a player.
5.  **Night Phase:** The Mafia secretly chooses a victim to eliminate.
6.  **Win Condition:**
    *   **Villagers Win:** Eliminate all Mafia members.
    *   **Mafia Wins:** Outnumber or equal the count of Villagers.

## 🤖 AI Assistant
In the game room, you can ask the AI guide for help on rules or strategies. The game uses Google's Generative AI to provide context-aware responses designated to help you catch the mafia (or hide if you are one!).

## 📄 License
[MIT License](LICENSE)
