from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import datetime

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
    email = request.form.get('email')
    print('githubUrl:', github_url)
    print('email:', email)
    file = request.files.get('file')
    print('file:', file)
    if not github_url:
        print('Error: githubUrl required')
        return jsonify({'message': 'githubUrl required'}), 400
    file_path = None
    if file:
        # Generate a unique filename using email and datetime
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        base = email if email else 'resume'
        ext = os.path.splitext(secure_filename(file.filename))[1]
        filename = f"{base}_{timestamp}{ext}"
        print('Saving file as:', filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
    # Fetch and log GitHub profile details
    github_profile = get_github_full_profile(github_url)
    print('GitHub profile data:', github_profile)
    print('--- /user/details completed successfully ---')
    analyze(github_url, github_profile, file_path)
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
    response = {'response': chatbot(message)}
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

def get_github_full_profile(github_url):
    """
    Given a GitHub profile URL, fetch all public repos, languages, and commit counts for the user.
    Returns a dict with username, repos, languages, and commit details.
    """
    import requests
    from urllib.parse import urlparse
    try:
        # Robust username extraction
        parsed = urlparse(github_url)
        path_parts = [p for p in parsed.path.split('/') if p]
        username = path_parts[0] if path_parts else ''
        print(f'Extracted username: {username}')
        if not username:
            raise ValueError('Could not extract username from URL')
        repos_url = f'https://api.github.com/users/{username}/repos'
        print(f'Calling GitHub API: {repos_url}')
        repos_resp = requests.get(repos_url)
        print(f'Repos API status: {repos_resp.status_code}, body: {repos_resp.text[:500]}')
        if repos_resp.status_code != 200:
            print('Error fetching repos:', repos_resp.text)
            return {'error': f'GitHub API error: {repos_resp.status_code} {repos_resp.text}'}
        repos = repos_resp.json()
        print(f'Found {len(repos)} repos')
        repo_data = []
        all_languages = set()
        user_commit_count = 0
        user_languages = set()
        for repo in repos:
            repo_name = repo['name']
            print(f'Processing repo: {repo_name}')
            # Languages
            lang_resp = requests.get(repo['languages_url'])
            print(f'Languages API status: {lang_resp.status_code}, body: {lang_resp.text[:200]}')
            languages = lang_resp.json() if lang_resp.status_code == 200 else {}
            print(f'Languages for {repo_name}: {list(languages.keys())}')
            all_languages.update(languages.keys())
            # Commits
            commits_url = f'https://api.github.com/repos/{username}/{repo_name}/commits'
            commits_resp = requests.get(commits_url)
            print(f'Commits API status: {commits_resp.status_code}, body: {commits_resp.text[:200]}')
            if commits_resp.status_code != 200:
                print('Error fetching commits:', commits_resp.text)
                commit_count = 0
            else:
                commits = commits_resp.json()
                commit_count = 0
                for commit in commits:
                    author = commit.get('commit', {}).get('author', {}).get('name', '')
                    if author.lower() == username.lower():
                        commit_count += 1
            print(f'User commit count for {repo_name}: {commit_count}')
            user_commit_count += commit_count
            user_languages.update(languages.keys())
            repo_data.append({
                'repo': repo_name,
                'languages': list(languages.keys()),
                'user_commit_count': commit_count
            })
        github_info = {
            'username': username,
            'repos': repo_data,
            'all_languages': list(all_languages),
            'user_languages': list(user_languages),
            'user_total_commits': user_commit_count
        }
    except Exception as e:
        print('GitHub API error:', e)
        github_info = {'error': str(e)}
    print('GitHub full profile:', github_info)
    return github_info

def analyze(github_url, github_profile, resume_path):
    """
    Analyze a candidate using their GitHub URL, GitHub profile data, and resume file path.
    - github_url: The GitHub profile URL (string)
    - github_profile: The dict returned by get_github_full_profile
    - resume_path: The path to the resume file (string)
    """
    print(f'Analyzing candidate:')
    print(f'GitHub URL: {github_url}')
    print(f'GitHub Profile: {github_profile}')
    print(f'Resume Path: {resume_path}')
    # Add your custom analysis logic here (e.g., scoring, matching, etc.)
    # This method returns void (no return statement)
    pass

def chatbot(message):
    """
    Simple rule-based chatbot for demo purposes.
    Returns canned responses for 'help', 'hello', 'bye', etc.
    """
    if not message or not isinstance(message, str):
        return "Sorry, I didn't understand that."
    msg = message.lower().strip()
    if 'hello' in msg or 'hi' in msg:
        return "Hello! How can I help you today?"
    elif 'help' in msg:
        return "Sure, I'm here to help. What do you need assistance with?"
    elif 'bye' in msg or 'goodbye' in msg:
        return "Goodbye! Have a great day!"
    elif 'thanks' in msg or 'thank you' in msg:
        return "You're welcome!"
    else:
        return f"You said: {message}"

if __name__ == '__main__':
    app.run(debug=True, port=8080)
