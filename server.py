from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS, cross_origin
from bson import ObjectId
import hashlib
from openai import OpenAI

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

OPEN_API_KEY = 'sk-proj-gayGEj6jPPzsFQ8NObYUT3BlbkFJ5M4zTPPQkNO2yzCGIHuR'
openAiClient = OpenAI(api_key=OPEN_API_KEY)


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
    
@app.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin()
def register():
    if request.method == 'OPTIONS':
        return jsonify({'message': 'Preflight request allowed'}), 200

    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    language = data.get('language')

    if not name or not email or not password or not language:
        return jsonify({'error': 'Invalid data. Required fields are missing.'}), 400

    # Hash password before storing
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    new_user = {
        'name': name,
        'email': email,
        'password': hashed_password,
        'language': language,
        'school': data.get('school', ''),
        'grade': data.get('grade', ''),
        'performance': data.get('performance', ''),
        'location': data.get('location', ''),
        'ambition': data.get('ambition', ''),
        'hobbies': data.get('hobbies', ''),
        'interests': []
    }

    try:
        result = users_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        return jsonify({'message': 'User registered successfully', 'userId': user_id}), 201
    except Exception as e:
        print(f"Error registering user: {e}")
        return jsonify({'error': 'Failed to register user.'}), 500


@app.route('/update_user', methods=['POST'])
@cross_origin()
def update_user():
    data = request.json
    email = data.get('email')

    updated_info = {
        'education': data.get('education'),
        'location': data.get('location'),
        'grade': data.get('grade'),
        'ambition': data.get('ambition'),
        'hobbies': data.get('hobbies'),
        'learning_capacities': data.get('learning_capacities'),
        'interests': data.get('interests')
    }

    # Update user based on email
    result = users_collection.update_one({'email': email}, {'$set': updated_info})

    if result.modified_count > 0:
        return jsonify({'message': 'User information updated successfully'}), 200
    else:
        return jsonify({'error': 'User not found or no changes applied'}), 404


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    # user_id = data.get('userId')
    message = data.get('message')

    # user = users_collection.find_one({'_id': ObjectId(user_id)})
    # if not user:
    #     return jsonify({'error': 'User not found'}), 404

    response = openAiClient.ask_question(message)
    return jsonify({'response': response}), 200

if __name__ == '__main__':
    app.run(debug=True)
