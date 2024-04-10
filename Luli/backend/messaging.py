from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId

def follow_user(FROM_user_id, TO_user_id, mongoclient_url='mongodb://localhost:27017'):
    user_id = ObjectId(FROM_user_id)
    user_to_follow_id = ObjectId(TO_user_id)
    
    client = MongoClient(mongoclient_url)
    DATABASE = client['user_data']
    users_collection = DATABASE.credentials
    
    # Make sure users exist
    user = users_collection.find_one({'_id': user_id})
    user_to_follow = users_collection.find_one({'_id': user_to_follow_id})

    # If both users exist and the user_to_follow is not already in the followed_users list, add the user_to_follow to the user's friends list
    print(user_to_follow_id not in user.get('followed_users', []))
    if user and user_to_follow and user_to_follow_id not in user.get('followed_users', []):
        # Check if the user already has a 'followed_users' field
        if 'followed_users' in user:
            # If the 'followed_users' field exists, append the user_to_follow_id to the list
            users_collection.update_one({'_id': user_id}, {'$push': {'followed_users': user_to_follow_id}})
        else:
            # If the 'followed_users' field does not exist, create a new list with the user_to_follow_id
            users_collection.update_one({'_id': user_id}, {'$set': {'followed_users': [user_to_follow_id]}})
        return True
    elif user_to_follow_id in user.get('followed_users', []):
        return True
    return False

def message_user(FROM_user_id, TO_user_id, message, mongoclient_url='mongodb://localhost:27017'):
    user_id = ObjectId(FROM_user_id)
    user_to_message_id = ObjectId(TO_user_id)

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

def get_most_recent_message(FROM_user_id, TO_user_id, mongoclient_url='mongodb://localhost:27017'):
    user_id = ObjectId(FROM_user_id)
    user_to_message_id = ObjectId(TO_user_id)

    client = MongoClient(mongoclient_url)
    DATABASE = client['user_data']
    users_messages_collection = DATABASE.messages
    
    # Query by 'receiver_id' instead of 'user_id'
    user_messages = users_messages_collection.find({'receiver_id': user_to_message_id})
    
    user_messages_list = list(user_messages)
    if len(user_messages_list) == 0:
        return None
    return user_messages_list[-1]

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
    user_id = username_to_user_id('Liam_TEST')
    user_to_follow_id = username_to_user_id('Luigi_TEST')
    assert follow_user(user_id, user_to_follow_id) == True
    assert follow_user(user_to_follow_id, user_id) == True


def test_check_messages():
    user_id = ObjectId('6615f9b445f79acfdde258eb')  # Liam_TEST
    user_to_message_id = ObjectId('6615f98545f79acfdde258ea')  # Luigi_TEST
    message = "Hello, how are you?!!!"
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

    print("Most recent message for Luigi_TEST: ", get_most_recent_message(username_to_user_id('Liam_TEST'), username_to_user_id('Luigi_TEST')))

    print("All tests passed!")