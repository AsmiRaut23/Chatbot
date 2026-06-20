from dotenv import load_dotenv
import os
import datetime
import time
import json
import sqlite3

from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

conn = sqlite3.connect("chatbot.db") #it will create a new database file named chatbot.db in the current directory if it does not exist. if it already exists then it will connect to that database.
cursor = conn.cursor() #it will create a cursor object which is used to execute SQL commands and queries on the database. it acts as a bridge between the Python code and the database, allowing you to interact with the database using Python.
cursor.execute("""
CREATE TABLE IF NOT EXISTS knowledge(
    question TEXT PRIMARY KEY,
    answer TEXT
)
""") #it will create a new table named knowledge in the database if it does not exist. the table will have two columns question and answer, where question is the primary key which means it cannot be duplicate and it will be used to identify each row uniquely.

conn.commit() #it will save the changes made to the database. it is used to commit the current transaction to the database, ensuring that all changes are saved and made permanent. without calling commit(), any changes made to the database will not be saved and will be lost when the connection is closed.



try:
    #when the program starts, it opens knowledge.json file and read its content and store it into a python variable named as knowledge
    # knowledge.json file converts into python code
    with open("knowledge.json","r") as file:
        knowledge = json.load(file)
        #print("Knowledge loaded:", knowledge)
        
    # if no data is stored in json then chatbot starts with an empty dict.
except:
    knowledge = {}

name = input("Enter your name: ")
presentHour = datetime.datetime.now().hour

if 0 <= presentHour < 12:
    print("Good morning", name)
elif 12 <= presentHour <= 16:
    print("Good afternoon", name)
elif 16 < presentHour <= 19:
    print("Good evening", name)
elif 19 < presentHour < 24:
    print("Good night", name)
    
print("Welcome to my chatbot ")
print("ask basic question to my chatbot and test it. Type 'bye' to exit")

try:
    with open("memory.json", "r") as file:
        memory = json.load(file)

except:
    memory = {}

try:
    with open("chat_history.json", "r") as file:
        chat_history = json.load(file)

except:
    chat_history = []


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

    except:
        return "Invalid calculation"

def saveMemory():
 #dump means Python obj. -> convert to JSON text -> store in file
                                 # python object(in python everything is object like name="Asmi", here Asmi is a python object(a string obj.))
        # memory -> json -> loaded again. the stored value is accessable even when the program is called. this is called persistent storage.
        
    with open("memory.json", "w") as file:
        json.dump(memory, file)

def saveKnowledge():

    with open("knowledge.json", "w") as file:
        json.dump(knowledge, file)

def saveKnowledgeToDB(question, answer):
    cursor.execute(
        "INSERT OR REPLACE INTO knowledge VALUES(?,?)",
        (question,answer)
    )
    conn.commit()

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

    cursor.execute(
        "SELECT question,answer FROM knowledge"
    )

    rows = cursor.fetchall()
    for question, answer in rows:

        if question in user_input:
            return answer
        
        if user_input in question:
            return answer

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

                Conversation:
                {chr(10).join(f"{msg['role']}: {msg['text']}" for msg in recent_history)}
                """
            )
            full_response = ""
            for chunk in response:
                text = getattr(chunk, "text", "")
                if text:
                    print(text,end="",flush=True)
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



def saveChatHIstory():
    with open("chat_history.json", "w") as file:
        json.dump(chat_history, file)

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

    if "what do you know" in user_input:
        if len(knowledge) == 0:
            return "I don't know anything yet."    
        return "\n".join(knowledge.keys()) # it will return the keys of the knowledge dict which are the questions that the chatbot knows how to answer. it will join the keys with a new line character so that each question is printed on a new line.

    if user_input.startswith("forget"):
        question = user_input.replace("forget", "").strip()
        if question in knowledge:
            del knowledge[question] # it will delete the key-value pair from the knowledge if the user write forget and the question that is stored in the knowledge.

            saveKnowledge()

            return "I forgot that."
        return "I don't know that question."
    

    '''if user_input in knowledge:  # if the input or the answer is already stored in the knowledge(from json file) then the chatbot will answer the question.
        return knowledge[user_input]'''
    
    #improved version of the above code, now it can also answer the question if the exact wording is not used but the meaning of the line is same.it check the words,if it is present in the question(key) then it will answer. example: what is python, this key is stored in the knowledge but if user input is "can you tell me what is python?" then it will also answer the question because the word "what is python" is present in the user input. and also if user input is "what is python programming language?" then it will also answer the question because the word "what is python" is present in the user input. this way it can answer more questions with different wording but same meaning.
    '''for question, answer in knowledge.items():
        if question in user_input:
            return answer
        if user_input in question:
            return answer '''

    db_answer = getKnowledgeFromDB( # in database it searches for a matching question.
        user_input.lower().strip()
    )
    if db_answer: # if answer found for the matching questionm, then it will return the answer from the db. if no answer is found then it will return None and it will continue to the next part of the code which is asking Gemini for the answer.
        return db_answer
    
    if "my name is" in user_input:
        name = user_input.replace("my name is", "").strip() #my name is will be replaced by nothing only the name will be stored in the name variable
        memory["name"] = name
        
        saveMemory() 
        return f"Nice to meet you {name}"

    if "what is my name" in user_input or"do you remember my name" in user_input:
        if "name" in memory:
            return f"Your name is {memory['name']}"
        return "I don't know your name yet"
            
    for keywords,response in responses.items(): # keyword means key of responses dict and response means the pair of the  dict 
        for keyword in keywords:
            if user_input.strip() == keyword:
                return response
    return "UNKNOWN"

# saveKnowledgeToDB(
#     "what is charger",
#     "Charger is a physical device that is used to charge the battery of electronic devices."
# )

# print(
#     getKnowledgeFromDB(
#         "what is charger"
#     )
# )
while True:
    user_input = input("Hello,Ready for conversation?: ")
    chat_history.append({
        "role": "user",
        "text": user_input
    })
    saveChatHIstory()
    reply = getResponseOfBot(user_input)
    
    if reply == "UNKNOWN":
        #print("Bot is thinking...")
        print("Bot:",end="")
        ai_answer = askGemini(user_input,chat_history)

        chat_history.append({
            "role": "assistant",
            "text": ai_answer
        })
        saveChatHIstory()

        if(
            ai_answer
            and not ai_answer.startswith("Sorry,")
            and ("what is" in user_input.lower()
                 or "explain" in user_input.lower())
        ):
            '''knowledge[user_input.lower().strip()] = ai_answer
            saveKnowledge()'''

            #if ai_answer is not empty and it does not start with "Sorry" and the user_input contains "what is", "explain" then it will save the questiona and answer in the database.
            saveKnowledgeToDB(
                user_input.lower().strip(),
                ai_answer
            )

    else:
        print("Bot:", reply)
    
    if "bye" in user_input.lower():
        break
    

            

