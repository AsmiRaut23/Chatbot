# Lumina – AI Chatbot

## Overview

Lumina is an AI-powered conversational assistant developed using Python, Streamlit, SQLite, and Google's Gemini API. Lumina can answer user queries, remember information, store knowledge in a database, and provide an interactive chat interface through a web application.
Lumina is deployed on Streamlit Community Cloud and can be accessed through the live demo below.

**Live Demo:** 
🌐 https://lumina-aichatbot.streamlit.app/

## Screeshot


## Key Features

- AI-powered responses using Google Gemini
- Responsive Streamlit web interface
- SQLite-based persistent knowledge storage
- User memory management
- Knowledge retrieval from local database
- Conversation history persistence
- Mathematical expression evaluation
- Automatic fallback to Gemini for unknown questions
- Secure API key management using .env


## How Lumina Works

- Accepts user queries through a Streamlit-based interface.
- Searches predefined responses and the SQLite knowledge base.
- Falls back to the Gemini API when no suitable local answer is available.
- Stores relevant AI-generated responses to expand its knowledge base.
- Maintains conversation history using SQLite for a continuous chat experience.


## Architecture

```text
User
   │
   ▼
Streamlit UI
   │
   ▼
Chatbot Logic
   │
   ├────────► SQLite Database
   │
   └────────► Gemini API
```


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
└── .env (create locally)
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


## Usage

The chatbot can:

- Answer general questions using Gemini AI
- Retrieve previously learned knowledge from SQLite
- Remember user information
- Store conversation history
- Perform basic mathematical calculations



## Future Scope

- Multi-session chat support
- Chat history sidebar
- Voice interaction
- Semantic search using embeddings
- File upload support
- User authentication
- RAG-based document question answering


## License

This project is licensed under the MIT License.


## Author

**Asmi Raut**

MCA Student

GitHub: https://github.com/AsmiRaut23