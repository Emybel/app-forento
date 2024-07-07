from pymongo import MongoClient

def check_schema():
    client = MongoClient('mongodb://Admin:ForentoAdmin1055@localhost:27017/forento')
    db = client.forento
    
    # Check users collection schema
    users_info = db.command("listCollections", filter={"name": "users"})
    print("Users Collection Schema:")
    print(users_info)
    
    # Check fly_detections collection schema
    detections_info = db.command("listCollections", filter={"name": "fly_detections"})
    print("Fly Detections Collection Schema:")
    print(detections_info)

check_schema()
