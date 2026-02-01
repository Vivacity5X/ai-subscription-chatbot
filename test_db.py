import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="chatbot",
    password="chatbot123",
    database="subscription_chatbot"
)

print("Connected successfully!")
