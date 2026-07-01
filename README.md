# Smart AI Chatbot

## Overview

Lumina is an AI-powered conversational assistant developed using Python, Streamlit, SQLite, and Google's Gemini API. Lumina can answer user queries, remember information, store knowledge in a database, and provide an interactive chat interface through a web application.


## Architecture

User
↓
Streamlit UI
↓
Chatbot Logic (Python)
↓
SQLite Database
↓
Gemini API


## Key Features

- AI-powered responses using Gemini API
- Interactive Streamlit web interface
- Persistent SQLite database storage
- User memory management
- Knowledge retrieval system
- Conversation history support
- Secure API key management using .env

## Tech Stack

- Python
- Streamlit
- SQLite
- Google Gemini API
- python-dotenv

## Database Design

### knowledge

| Column | Type |
|----------|---------|
| question | TEXT |
| answer | TEXT |

### user_memory

| Column | Type |
|----------|---------|
| key | TEXT |
| value | TEXT |

### chat_history

| Column | Type |
|----------|---------|
| id | INTEGER |
| role | TEXT |
| message | TEXT |

## Project Structure

```
Lumina/
│
├── app.py
├── chatbot_new.py
├── chatbot.db
├── style.css
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

## Installation

1. Clone the repository

```bash
git clone https://github.com/AsmiRaut23/Chatbot.git
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create a .env file

```env
GEMINI_API_KEY=YOUR_API_KEY
```

4. Run the application

```bash
python -m streamlit run app.py
```

## Future Scope

- ChatGPT-style conversation sidebar
- Multi-session chat support
- User authentication system
- Cloud deployment
- Semantic search for knowledge retrieval
- Voice-enabled chatbot interaction

## Author

Asmi Raut