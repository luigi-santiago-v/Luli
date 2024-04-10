from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId

def follow_user(user_id, user_to_follow_id, mongoclient_url='mongodb://localhost:27017'):
    user_id = ObjectId(user_id)
    user_to_follow_id = ObjectId(user_to_follow_id)
    
    client = MongoClient(mongoclient_url)
    DATABASE = client['user_data']
    users_collection = DATABASE.credentials
    users_friends_collection = DATABASE.friends
    
    # Make sure users exist
    user = users_collection.find_one({'_id': user_id})
    user_to_follow = users_collection.find_one({'_id': user_to_follow_id})

    # If both users exist, add the user_to_follow to the user's friends list
    if user and user_to_follow:
        users_friends_collection.insert_one({'user_id': user_id, 'followed_user_id': user_to_follow_id})
        return True
    return False

def message_user(user_id, user_to_message_id, message, mongoclient_url='mongodb://localhost:27017'):
    user_id = ObjectId(user_id)
    user_to_message_id = ObjectId(user_to_message_id)

    client = MongoClient(mongoclient_url)
    DATABASE = client['user_data']
    users_collection = DATABASE.credentials
    users_messages_collection = DATABASE.messages
    
    # Make sure users exist
    user = users_collection.find_one({'_id': user_id})
    user_to_message = users_collection.find_one({'_id': user_to_message_id})

    # If both users exist, add the message to the database
    if user and user_to_message:
        users_messages_collection.insert_one({
            'sender_id': user_id,
            'receiver_id': user_to_message_id,
            'message': message
        })
        return True
    return False


def user_id_to_username(user_id, mongoclient_url='mongodb://localhost:27017'):
    user_id = ObjectId(user_id)
    
    client = MongoClient(mongoclient_url)
    DATABASE = client['user_data']
    users_collection = DATABASE.credentials
    
    user = users_collection.find_one({'_id': user_id})
    if user:
        return user['username']
    return None

def username_to_user_id(username, mongoclient_url='mongodb://localhost:27017'):
    client = MongoClient(mongoclient_url)
    DATABASE = client['user_data']
    users_collection = DATABASE.credentials
    
    userid = users_collection.find_one({'username': username})
    if userid:
        return userid['_id']


def test_follow_user():
    user_id = '6615f9b445f79acfdde258eb' # Liam_TEST
    user_to_follow_id = '6615f98545f79acfdde258ea' # Luigi_TEST
    assert follow_user(user_id, user_to_follow_id) == True


def test_check_messages():
    user_id = ObjectId('6615f9b445f79acfdde258eb')  # Liam_TEST
    user_to_message_id = ObjectId('6615f98545f79acfdde258ea')  # Luigi_TEST
    message = "Hello, how are you?"
    message_user(user_id, user_to_message_id, message)
    client = MongoClient()
    DATABASE = client['user_data']
    
    users_messages_collection = DATABASE.messages
    # Query by 'receiver_id' instead of 'user_id'
    user_messages = users_messages_collection.find({'receiver_id': user_to_message_id})
    
    user_messages_list = list(user_messages)
    assert len(user_messages_list) != 0
    assert message in [user_message['message'] for user_message in user_messages_list]
    

if __name__ == "__main__":
    test_follow_user()
    test_check_messages()
    

    assert user_id_to_username(username_to_user_id('Liam_TEST')) == 'Liam_TEST'
    client = MongoClient()
    DATABASE = client['user_data']
    
    messages = DATABASE.messages.find({'receiver_id': ObjectId(username_to_user_id('Luigi_TEST'))})
    message_values = [message['message'] for message in messages]
    print("Messages for Luigi_TEST to read: ", message_values)

    messages = DATABASE.messages.find({'receiver_id': ObjectId(username_to_user_id('Liam_TEST'))})
    message_values = [message['message'] for message in messages]
    print("Messages for Liam_TEST to read: ", message_values)

    print("All tests passed!")