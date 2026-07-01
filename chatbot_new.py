# python -m streamlit run app.py

from dotenv import load_dotenv
import os
import datetime
import time

import sqlite3

from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

conn = sqlite3.connect("chatbot.db", check_same_thread=False) #it will create a new database file named chatbot.db in the current directory if it does not exist. if it already exists then it will connect to that database.
cursor = conn.cursor() #it will create a cursor object which is used to execute SQL commands and queries on the database. it acts as a bridge between the Python code and the database, allowing you to interact with the database using Python.
cursor.execute("""
CREATE TABLE IF NOT EXISTS knowledge(
    question TEXT PRIMARY KEY,
    answer TEXT
)
""") #it will create a new table named knowledge in the database if it does not exist. the table will have two columns question and answer, where question is the primary key which means it cannot be duplicate and it will be used to identify each row uniquely.

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_memory( 
    key TEXT PRIMARY KEY,
    value TEXT
)
""") # a table named user_memory is created having attributes key and value.


# This create a table named chat_history and stores all the conversation btw user and bot
cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        message TEXT
)
""")


conn.commit() #it will save the changes made to the database. it is used to commit the current transaction to the database, ensuring that all changes are saved and made permanent. without calling commit(), any changes made to the database will not be saved and will be lost when the connection is closed.



#chatbot memory creation
responses = {
    ("hello","hi","hey") : "Hi,How can I help you?",
    ("what is your name",): "My name is smart chatbot",
    ("what can you do?",): "I can answer simple questions of yours",
    ("great to talk to you",): "Thank you! I'm glad you're enjoying the conversation.",
    ("bye","goodbye") :" Have a nice day"
}

def getCurrentTime():
    return datetime.datetime.now().strftime("%H:%M:%S")

def getCurrentDate():
    return str(datetime.date.today())

def getCurrentDay():
    return datetime.datetime.now().strftime("%A")  # %A is used to get the full name of the day like Monday, Tuesday etc. if we use %a then it will give us the short name of the day like Mon, Tue etc.

def calculateExpression(expression):

    try:
        return str(eval(expression))

    except Exception:
        return "Invalid calculation"



def normalizeQuestion(question):
    question = question.lower()
    remove_words = [
        "what is",
        "what are",
        "tell me about",
        "can you tell me about",
        "can you tell me",
        "explain",
        "please explain",
        "tell me",
        "about"
    ]

    for word in remove_words:
        question = question.replace(word, "")
    return question.strip(" ?.!")

def saveKnowledgeToDB(question, answer):
    
    question = normalizeQuestion(question) # question is now normalized before saving in the db
    cursor.execute(
        "INSERT OR REPLACE INTO knowledge VALUES(?,?)",
        (question,answer)
    )
    conn.commit()

def saveMemoryToDB(key,value):
    cursor.execute(
        "INSERT OR REPLACE INTO user_memory VALUES (?,?)",
        (key,value)
    )

    conn.commit()

def saveChatToDB(role,message):
    cursor.execute(
        "INSERT INTO chat_history(role,message) VALUES (?,?)",
        (role, message)
    )
    conn.commit()


def loadChatHistoryFromDB():
    cursor.execute(
        "SELECT role, message FROM  chat_history ORDER BY id"
    )

    rows = cursor.fetchall()
    history = []
    for role, message in rows:
        history.append({
            "role":role,
            "text":message
        })
    return history

chat_history = loadChatHistoryFromDB() 


def getMemoryFromDB(key):
    cursor.execute(
        "SELECT value FROM user_memory WHERE key=?",
        (key,)
    )
    result = cursor.fetchone() # gets the first matching row
    if result:
        return result[0]
    
    return None



'''def getKnowledgeFromDB(user_input):
    cursor.execute(
        "SELECT answer FROM knowledge WHERE question = ?",
        (user_input,)
    )
    result = cursor.fetchone() # fetches one matching row from the query result.
    if result:
        return result[0] #if no result is found then it will return None, if a result is found then it will return the answer which is stored in the first column of the result. since we are only selecting the answer column, it will be at index 0 of the result tuple.
    return None '''

def getKnowledgeFromDB(user_input):
    user_input = normalizeQuestion(user_input)
    cursor.execute(
        "SELECT question,answer FROM knowledge"
    )

    rows = cursor.fetchall()

    STOP_WORDS = {
    "in", "of", "the", "a", "an", "is", "are", "what", "who"
}

    #first check exacgt match. 
    for question, answer in rows:
        if normalizeQuestion(question) == user_input:
            return answer
        
    #if no exact match is found then check partial matches.
    
    best_answer = None
    best_score = 0
    best_length = 999999
    user_words = {
        word
        for word in user_input.split()
        if word not in STOP_WORDS
    }

    for question, answer in rows:
        question_words = {
            word
            for word in question.split()
            if word not in STOP_WORDS
        }
        score = len(user_words.intersection(question_words))

        extra_words = len(question_words - user_words)

        if score > best_score or (
            score == best_score and extra_words < best_length
        ):
            best_score = score
            best_answer = answer
            best_length = len(question) 

        elif score == best_score and score > 0:
            if len(question) < best_length:
                best_answer = answer
                best_length = len(question)

    if best_score >= 2: 
        return best_answer
    return None
        


def askGemini(question,history,retries=3):
    for attempt in range(retries):

        try:
            recent_history = history[-10:] # Get the last 10 messages from the chat history
            response = client.models.generate_content_stream(
                model="gemini-flash-lite-latest",
                
                contents=f"""
                You are a helpful chatbot.

                Rules:
                - Answer in plain text.
                - Keep answers under 100 words unless asked otherwise.
                - Do not use markdown.
                - Be conversational.
                - If the current question is related to previous conversation, use the conversation context.
                - If the current question is not related to previous conversation, answer normally without forcing context.
                Current User Question:
                {question}

                Conversation:
                {chr(10).join(f"{msg['role']}: {msg['text']}" for msg in recent_history)}
                """
            )
            full_response = ""
            for chunk in response:
                text = getattr(chunk, "text", "")
                if text:
                    full_response += text
            print()
            return full_response



        except Exception as e:
            print("\nDEBUG ERROR:", e)
            
            print(f"\nAttempt {attempt+1} failed: {e}")
            
            if attempt < retries - 1:
                print("Retrying in 2 seconds...")
                time.sleep(2)
                continue

            return "Sorry, the AI is busy right now. Please try again later."
        #return "Sorry, I encountered an error while processing your request."



def getResponseOfBot(user_input):
    user_input = user_input.lower()
    
    if "time" in user_input:
        return getCurrentTime()

    if "date" in user_input:
        return getCurrentDate()

    if "day" in user_input:
        return getCurrentDay()
    
    #if user_input.startswith("calculate"):
    if "calculate" in user_input:
        expression = user_input.replace("calculate", "").strip()
        return calculateExpression(expression)


    db_answer = getKnowledgeFromDB( # in database it searches for a matching question.
        user_input.lower().strip()
    )


    if db_answer: # if answer found for the matching questionm, then it will return the answer from the db. if no answer is found then it will return None and it will continue to the next part of the code which is asking Gemini for the answer.
        return db_answer
    
    if "my name is" in user_input:
        name = user_input.replace("my name is", "").strip(" .!?") #my name is will be replaced by "" and the name will be stored in the name variable
        saveMemoryToDB("name", name.title()) # .title() capitalizes the first letter of each word
        
        return f"Nice to meet you {name}"

    if ("what is my name" in user_input or"do you remember my name" in user_input):
        stored_name = getMemoryFromDB("name")
        if stored_name:
            return f"Your name is {stored_name}"
        return "I don't know your name yet"
            
    for keywords,response in responses.items(): # keyword means key of responses dict and response means the pair of the  dict 
        for keyword in keywords:
            if user_input.strip() == keyword:
                return response
    return "UNKNOWN"

def getBotReply(user_input):
    chat_history.append({
        "role": "user",
        "text": user_input
    })

    saveChatToDB("user", user_input)

    reply = getResponseOfBot(user_input)
    if reply != "UNKNOWN":
        return reply
    
    ai_answer = askGemini(user_input,chat_history)
    chat_history.append({
        "role": "assistant",
        "text": ai_answer
    })
    saveChatToDB("assistant", ai_answer)
    if("what is" in user_input.lower() # only "what is, who is, explain" type of questions and ans will be saved in the knowledge db. 
       or "what are" in user_input.lower()
       or "who is" in user_input.lower()
       or "explain" in user_input.lower()
       or "tell me about" in user_input.lower()
    ):
       saveKnowledgeToDB(user_input, ai_answer)

    return ai_answer

