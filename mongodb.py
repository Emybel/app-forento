from pymongo import MongoClient

client = MongoClient("localhost", 27017)

db = client.forento

detection = db.flyDetectionData

for data in detection.find():
    print(data)