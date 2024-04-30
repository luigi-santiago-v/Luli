from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

def add_sensor_data(client, database_name, collection_name, document_id, sensor_data):
    # Access the MongoDB database
    db = client[database_name]
    collection = db[collection_name]
    
    # Timestamp as a string in ISO format, with colons replaced by underscores
    #timestamp = datetime.utcnow().isoformat().replace('.', ':') + '+00_00'
    timestamp = datetime.now().isoformat().replace('.', ':')

    # Update the document with new sensor data at the specified timestamp
    print(f"TIMESTAMP IS: {timestamp}")
    update_result = collection.update_one(
        {"_id": document_id},
        {"$set": {f"sensor_data.{timestamp}": sensor_data}},
        upsert=True
    )
    
    # Check the result of the update
    if update_result.upserted_id is not None:
        print(f"Document was created with ID: {update_result.upserted_id}")
    elif update_result.modified_count == 1:
        print("Update successful.")
    else:
        print("Update failed or no changes made.")

# Example usage
client = MongoClient("mongodb://localhost:27017/")
database_name = 'user_data'
collection_name = 'data'
document_id = ObjectId('65fa4c38972991d86e690014')
sensor_data = {
    "temp": 25.45,
    "humidity": 63,
    "light": 25,
    "tank": 36,
    "ph": 7
}

add_sensor_data(client, database_name, collection_name, document_id, sensor_data)
