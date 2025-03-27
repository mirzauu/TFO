from pymongo import MongoClient

MONGO_URI = "mongodb+srv://ainypus:3mz1b0dZcWKPYxtZ@cluster0.ksi9c62.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["tfo"]  # Your MongoDB database
chat_collection = db["chat"]  # Collection for chat messages


print(db,chat_collection)