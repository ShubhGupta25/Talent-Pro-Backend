# TalentPro Backend

A modern Python Flask backend for the TalentPro platform, supporting user registration, login, file upload, chat engine, and more. This backend is designed for integration with a React (TypeScript) frontend and supports role-based access, JWT authentication (optional), and file uploads.

## Features

- User registration and login
- JWT authentication (can be enabled/disabled)
- Role-based access (can be enabled/disabled)
- File upload for employee details
- Chat engine endpoint for recruiters
- CORS enabled for frontend integration
- In-memory user store (for demo; replace with DB for production)

## Endpoints

### 1. Register User

- **Endpoint:** `POST /user/register`
- **Payload:**
  ```json
  {
    "email": "user@example.com",
    "password": "yourpassword",
    "registrationType": "recruiter" | "employee"
  }
  ```
- **Response:**
  - `200 OK` on success
  - `400` if user exists or fields are missing

### 2. Login User

- **Endpoint:** `POST /user/login`
- **Payload:**
  ```json
  {
    "email": "user@example.com",
    "password": "yourpassword"
  }
  ```
- **Response:**
  ```json
  {
    "token": "<jwt-token>",
    "userType": "recruiter" | "employee"
  }
  ```
  - `401` if credentials are invalid

### 3. User Details Submission (Employee)

- **Endpoint:** `POST /user/details`
- **Payload:** `multipart/form-data`
  - `githubUrl`: string (required)
  - `file`: file (optional)
- **Response:**
  - `200 OK` on success
  - `400` if `githubUrl` is missing

### 4. Chat Engine Query (Recruiter)

- **Endpoint:** `POST /chat-engine/query`
- **Payload:**
  ```json
  {
    "message": "Your chat message here"
  }
  ```
- **Response:**
  ```json
  {
    "response": "Bot reply here"
  }
  ```

### 5. Logout

- **Endpoint:** `POST /user/logout`
- **Payload:**
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response:**
  - `200 OK` on success

## Running the App

1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
2. Start the Flask server:
   ```powershell
   python app.py
   ```
3. The API will be available at `http://localhost:8080`

## Notes

- All data is stored in memory for demonstration. Use a database for production.
- JWT authentication and role checks can be enabled/disabled in the code.
- CORS is enabled for frontend integration.
- For file uploads, files are saved in the `uploads/` directory.

## Chatbot

- The backend includes a simple rule-based chatbot method (`chatbot(message)`) that returns canned responses for queries like "hello", "help", "bye", and more. You can expand this logic as needed.
- Example usage:
  ```python
  chatbot("hello")  # returns: "Hello! How can I help you today?"
  chatbot("help")   # returns: "Sure, I'm here to help. What do you need assistance with?"
  chatbot("bye")    # returns: "Goodbye! Have a great day!"
  chatbot("random text")  # returns: "You said: random text"
  ```

## Analysis Method

- The backend provides an `analyze` method for candidate analysis:
  ```python
  analyze(github_url, github_profile, resume_path)
  ```
  - `github_url`: The candidate's GitHub profile URL
  - `github_profile`: The dict returned by the GitHub profile fetch function
  - `resume_path`: The path to the candidate's resume file
  - This method logs all inputs and is ready for custom analysis logic.

---

Made with ❤️ using Flask and modern Python best practices.
