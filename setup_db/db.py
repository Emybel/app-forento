from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017', username="Admin", password="ForentoAdmin1055", authSource="forento", authMechanism="SCRAM-SHA-256")
db = client["forento"]
