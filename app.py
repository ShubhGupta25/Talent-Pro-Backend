from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
app.config['JWT_SECRET_KEY'] = 'super-secret-key'  # Change this in production
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['UPLOAD_FOLDER'] = 'uploads'
jwt = JWTManager(app)

# In-memory user store (replace with DB in production)
users = {}
sessions = set()

@app.route('/')
def hello():
    return 'TalentPro Backend Running'

@app.route('/user/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    registration_type = data.get('registrationType')
    if not all([email, password, registration_type]):
        return jsonify({'message': 'Missing fields'}), 400
    if email in users:
        return jsonify({'message': 'User already exists'}), 400
    users[email] = {
        'password': generate_password_hash(password),
        'userType': registration_type
    }
    return '', 200

@app.route('/user/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = users.get(email)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'message': 'Invalid credentials'}), 401
    token = create_access_token(identity={'email': email, 'userType': user['userType']})
    sessions.add(email)
    return jsonify({'token': token, 'userType': user['userType']})

@app.route('/user/details', methods=['POST'])
# JWT token is required for this endpoint, implement in prod
def user_details():
    print('--- /user/details called ---')
    print('Headers:', dict(request.headers))
    print('Form:', request.form)
    print('Files:', request.files)
    github_url = request.form.get('githubUrl')
    print('githubUrl:', github_url)
    file = request.files.get('file')
    print('file:', file)
    if not github_url:
        print('Error: githubUrl required')
        return jsonify({'message': 'githubUrl required'}), 400
    if file:
        filename = secure_filename(file.filename)
        print('Saving file as:', filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print('--- /user/details completed successfully ---')
    return '', 200

@app.route('/chat-engine/query', methods=['POST'])
# JWT token is required for this endpoint, implement in prod
def chat_query():
    print('--- /chat-engine/query called ---')
    print('Headers:', dict(request.headers))
    print('JSON:', request.get_json(silent=True))
    data = request.get_json()
    message = data.get('message')
    print('message:', message)
    # Dummy bot reply
    response = {'response': f'Bot reply to: {message}'}
    print('response:', response)
    print('--- /chat-engine/query completed successfully ---')
    return jsonify(response)

@app.route('/user/logout', methods=['POST'])
def logout():
    user = get_jwt_identity()
    email = user['email']
    sessions.discard(email)
    return '', 200

@app.errorhandler(422)
def handle_unprocessable_entity(err):
    print('422 Error:', err)
    return jsonify({'message': 'Unprocessable Entity', 'error': str(err)}), 422

@app.before_request
def log_request_payload():
    print(f'[{request.method}] {request.path}')
    print('Headers:', dict(request.headers))
    if request.is_json:
        print('JSON:', request.get_json(silent=True))
    else:
        print('Form:', request.form)
        print('Files:', request.files)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
