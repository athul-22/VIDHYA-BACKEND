from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

uri = "mongodb+srv://vidhya:vidhya@cluster0.vur3oa1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client.get_database('database') 

users_collection = db.users

try:
    client.admin.command('ping')
    print("DB CONNECTED SUCCESSFULLY 🚀")
except Exception as e:
    print(e)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email, 'password': password})
    if user:
        return jsonify({'message': 'Login successful', 'userId': str(user['_id'])}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401
    
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    language = data.get('language')

    if users_collection.find_one({'email':email}):
        return jsonify({'error':'User already exists!'}), 400
    
    new_user = {
        'name': name,
        'email': email,
        'password': password,
        'language': language,
        'education': '',
        'location': '',
        'state': '',
        'grade': '',
        'ambition': '',
        'hobbies': '',
        'learning_capacities': '',
        'interests': []
    } 

    result = users_collection.insert_one(new_user)
    user_id = str(result.inserted_id) 
    return jsonify({'message': 'User registered successfully', 'userId': user_id}), 201


@app.route('/update_user', methods=['POST'])
def update_user():
    data = request.json
    email = data.get('email')

    updated_info = {
        'education': data.get('education'),
        'location': data.get('location'),
        'state': data.get('state'),
        'grade': data.get('grade'),
        'ambition': data.get('ambition'),
        'hobbies': data.get('hobbies'),
        'learning_capacities': data.get('learning_capacities'),
        'interests': data.get('interests')
    }


    result = users_collection.update_one({'email': email}, {'$set': updated_info})

    if result.modified_count > 0:
        return jsonify({'message': 'User information updated successfully'}), 200
    else:
        return jsonify({'error': 'User not found or no changes applied'}), 404


if __name__ == '__main__':
    app.run(debug=True)
