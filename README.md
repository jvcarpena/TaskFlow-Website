# Flask Task Management App

## Overview
This is a simple **Flask-based Task Management App** that allows users to **register, log in, and manage their tasks**. The app includes user authentication, task management functionalities, and a Bootstrap-styled interface for a smooth user experience.

## Features
- **User Authentication** (Register, Login, Logout)
- **Task Management** (Create, Edit, Delete Tasks)
- **Task Status Management** (Mark as Completed/In Progress)
- **CSRF Protection** with Flask-WTF
- **Password Hashing** using Werkzeug for Security
- **Bootstrap Integration** for UI Enhancement
- **Gravatar Support** for User Avatars
- **SQLite Database** for Storing User and Task Data

## Installation

### Prerequisites
Ensure you have **Python 3.x** installed on your machine.

### 1. Clone the Repository
```sh
git clone https://github.com/jvcarpena/to-do-app.git
cd to-do-app
```

### 2. Create a Virtual Environment (Optional but Recommended)
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the root directory and add the following variables:
```ini
FLASK_KEY=your_secret_key
SQLITE_DB_URI=sqlite:///to-do-app.db
```

### 5. Initialize the Database
```sh
python -c 'from app import db; db.create_all()'
```

### 6. Run the Application
```sh
python app.py
```
The app will be accessible at **http://127.0.0.1:5000/**.

## Project Structure
```
flask-task-manager/
│-- templates/          # HTML Templates
│-- static/             # Static files (CSS, JS)
│-- forms.py            # WTForms for user input
│-- app.py              # Main Flask application
│-- models.py           # Database models
│-- .env                # Environment variables
│-- requirements.txt    # Dependencies
│-- README.md           # Documentation
```

## Routes
| Route | Method | Description |
|---|---|---|
| `/` | GET | Home Page |
| `/register` | GET, POST | User Registration |
| `/login` | GET, POST | User Login |
| `/logout` | GET | User Logout |
| `/dashboard` | GET, POST | Task Dashboard |
| `/delete/<task_id>` | GET | Delete a Task |
| `/mark-as-completed/<task_id>` | GET, POST | Mark Task as Completed |
| `/mark-as-in-progress/<task_id>` | GET, POST | Mark Task as In Progress |

## Contributing
Feel free to fork this repository and submit pull requests for improvements!

---
**Happy Coding! 🚀**

