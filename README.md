# Flask-Authentication

A simple and extensible task app with an authentication system built with Flask.

## Overview

This project provides a foundation for handling user authentication and basic CRUD operations for tasks in Flask applications.

## Prerequisites

- Python 3.7+
- Flask

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KunMonanz/Flask-Authentication.git
   cd Flask-Authentication
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Configuration:**
   
   Update configuration settings in your Flask app as needed (such as secret key, database URI, etc.).

2. **Run the app:**
   ```bash
   python app.py
   ```
   The server will start on `http://127.0.0.1:5000/`.

3. **Access the app:**
   Open your browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/register) to interact with the authentication system.


## Project Structure

---

## How the Code Works: Authentication Logic Explained

### Main Components

- **app.py**: Sets up the Flask application, registers blueprints, and initializes extensions (database, JWT, migrations).
- **models.py**: Defines SQLAlchemy models for `User` and `Task`, including password hashing utilities.
- **auth.py**: Handles user registration and login endpoints.
- **config.py**: Application configuration, including secrets and database URI.
- **utils/user_helpers.py**: Helper functions for fetching users and tasks based on authentication state.

### Authentication Flow

#### 1. User Model and Password Handling

- The `User` model stores username, email, and a hashed password.
- Passwords are never stored in plain text. When a user sets a password (`set_password`), it uses `werkzeug.security.generate_password_hash` for secure hashing.
- Password verification (`check_password`) uses `werkzeug.security.check_password_hash`.

#### 2. Registration Endpoint (`/register`)

Defined in `auth.py`:
```python
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    # Validates required fields and checks for duplicates
    # Hashes password and creates a new user
    db.session.add(user)
    db.session.commit()
    return jsonify(msg="User registered"), 201
```
- Accepts JSON with `username`, `email`, and `password`.
- Checks for missing fields and existing users by username/email.
- Hashes the password before saving the user.

#### 3. Login Endpoint (`/login`)

Defined in `auth.py`:
```python
@auth_bp.route('/login', methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if user and user.check_password(data["password"]):
        token = create_access_token(identity=user.username)
        return jsonify(access_token=token)
    return jsonify(msg="Invalid credentials, user does not exist")
```
- Accepts JSON with `username` and `password`.
- Checks if the user exists and if the password matches.
- Returns a JWT access token if authenticated.

#### 4. Protecting Endpoints

- Endpoints for managing tasks (in `task.py`) use the `@jwt_required()` decorator to ensure the user is authenticated.
- Helper functions (`get_current_user`) extract the username from the JWT and fetch the user’s record.

#### 5. Using the JWT Token

- After logging in, the frontend/client must send the JWT access token in the `Authorization` header as `Bearer <token>` for all protected endpoints.

### Example Protected Endpoint (Get User Tasks)

```python
@task.route('/api/my-tasks', methods=["GET"])
@jwt_required()
def get_all_user_task():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    tasks = Task.query.filter_by(user_id=user.id).all()
    return jsonify([...])
```
- Only accessible if a valid JWT is provided.
- Returns all tasks for the authenticated user.

### Configuration (config.py)

- Uses environment variables for secrets.
- Default database is SQLite (`sqlite:///task.db`).

### Database Management

- Uses Flask-Migrate/Alembic for migrations.
- Create and apply migrations as needed for your schema (`flask db migrate`, `flask db upgrade`).

---

Would you like this explanation included in your README as a dedicated "How it Works" section? If so, I can generate a revised README for you with this material included.

## Customization

- Extend user models or authentication logic to fit your needs.
- Add features such as email confirmation, password resets, OAuth, etc.

Absolutely! Here’s a detailed explanation of how the task management functionality works in your Flask-Authentication repository:

---

## Task Management Logic Explained

### Task Model

Defined in `models.py`:
```python
class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=True)
    description = db.Column(db.String(256), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='default')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("priority IN ('high', 'medium', 'low', 'default')", name='check_priority'),
    )
```

#### Key fields:
- **title**: Optional, name of the task.
- **description**: Required, details of the task.
- **priority**: Must be one of 'high', 'medium', 'low', 'default'.
- **completed**: Boolean, true if done.
- **created_at/updated_at**: Timestamps.
- **user_id**: The user who owns the task.

---

### Task Endpoints

All routes are protected by JWT authentication (user must be logged in).

#### 1. Get All Tasks
```python
@task.route('/api/my-tasks', methods=["GET"])
@jwt_required()
def get_all_user_task():
    user = get_current_user()
    tasks = Task.query.filter_by(user_id=user.id).all()
    ...
```
- Returns all tasks belonging to the authenticated user.

#### 2. Get Completed Tasks
```python
@task.route("/api/my-completed-tasks", methods=["GET"])
@jwt_required()
def get_completed_tasks():
    user = get_current_user()
    completed_tasks = Task.query.filter_by(user_id=user.id, completed=True).all()
    ...
```
- Returns only tasks that are marked as completed.

#### 3. Create a Task
```python
@task.route('/api/create-task', methods=["POST"])
@jwt_required()
def create_task():
    user = get_current_user()
    ...
    new_task = Task(description=description, priority=priority, completed=False, user_id=user.id)
    db.session.add(new_task)
    db.session.commit()
    ...
```
- Authenticated user provides description (and optionally priority).
- New task is created for that user.

#### 4. Update Task Description/Title/Priority/Completed Status
```python
@task.route("/api/my-tasks/<int:id>/description", methods=["PATCH"])
@jwt_required()
def update_description(id):
    ...
@task.route("/api/my-tasks/<int:id>/title", methods=["PATCH"])
@jwt_required()
def update_title(id):
    ...
@task.route("/api/my-tasks/<int:id>/priority", methods=["PATCH"])
@jwt_required()
def update_priority(id):
    ...
@task.route("/api/my-tasks/<int:id>/completed-toggle", methods=["PATCH"])
@jwt_required()
def update_completed(id):
    ...
```
- All these PATCH endpoints require task ID and the relevant field in JSON.
- Only the owner can update their tasks.

#### 5. Delete Task
```python
@task.route('/api/delete<int:id>', methods=['DELETE'])
@jwt_required()
def delete_task(id):
    user = get_current_user()
    task = get_user_task(user.id, id)
    db.session.delete(task)
    db.session.commit()
    ...
```
- Only the task owner can delete their task.

---

### Validation

- **Priority**: Only accepts 'high', 'medium', 'low', 'default' (checked in `utils/task_helpers.py`).
- **Ownership**: All task operations use the authenticated user’s ID to fetch and modify only their own tasks.

---

## Summary

- Tasks are always tied to the logged-in user.
- All CRUD operations are protected by JWT authentication.
- Priority and ownership are strictly enforced.
- Changes to task fields are granular, using PATCH for updates.

---

Would you like this included in your README as a “Task Management” section? I can generate an updated README file for you if you want!

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is open source. See the LICENSE file for details.


Created by [KunMonanz](https://github.com/KunMonanz)
