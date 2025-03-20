from pymongo import MongoClient

MONGO_URI = "mongodb+srv://alimirsa123:a5VtspGwzNRv3m7b@cluster0.3wmvf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["tfo"]  # Your MongoDB database
chat_collection = db["chat"]  # Collection for chat messages
