from flask import Blueprint, request, jsonify
from models import db, Task
from flask_jwt_extended import jwt_required

from utils.task_helpers import validate_priority
from utils.user_helpers import get_current_user, get_user_task

task = Blueprint("task", __name__)

@task.route('/api/my-tasks', methods=["GET"])
@jwt_required()
def get_all_user_task():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    tasks = Task.query.filter_by(user_id=user.id).all()
    return jsonify(
        [{
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "completed": t.completed,
            "priority": t.priority,
            "created_at": t.created_at
            } for t in tasks
        ])

@task.route("/api/my-completed-tasks", methods=["GET"])
@jwt_required()
def get_completed_tasks():
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    completed_tasks = Task.query.filter_by(user_id=user.id, completed=True).all()
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "completed": t.completed
        } for t in completed_tasks
    ])

@task.route('/api/create-task', methods=["POST"])
@jwt_required()
def create_task():
    data = request.get_json()

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not data:
        return jsonify(msg="Missing JSON body"), 400

    description = data.get("description")
    priority = data.get("priority", "default")

    if not description:
        return jsonify(msg="Missing field: description"), 400

    is_valid, error_msg = validate_priority(priority)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    new_task = Task(description=description, priority=priority, completed=False, user_id=user.id)
    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "id": new_task.id,
        "description": new_task.description,
        "completed": new_task.completed,
        "priority": new_task.priority,
        "created_at": new_task.created_at
    }), 201

@task.route("/api/my-tasks/<int:id>/description", methods=["PATCH"])
@jwt_required()
def update_description(id):
    data = request.get_json()

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    task = get_user_task(id, user.id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if "description" not in data:
        return jsonify({"error": "Missing field: description"}), 400

    if "description" in data:
        task.description = data["description"]

    db.session.commit()
    return jsonify({
        "message": "Task description updated",
        "updated_at": task.updated_at
    }), 200


@task.route("/api/my-tasks/<int:id>/completed-toggle", methods=["PATCH"])
@jwt_required()
def update_completed(id):
    data = request.get_json()

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    task = get_user_task(id, user.id)
    if not task:
        return jsonify({"error": "Task not found or unauthorized"}), 404

    if "completed" not in data:
        return jsonify({"error": "Missing field: completed"}), 400

    task.completed = not task.completed

    db.session.commit()
    return jsonify({
        "message": f"Task '{task.title}' marked as {'completed' if task.completed else 'incomplete'}",
        "updated_at": task.updated_at
    }), 200

@task.route("/api/my-tasks/<int:id>/title", methods=["PATCH"])
@jwt_required()
def update_title(id):
    data = request.get_json()

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    task = get_user_task(id, user.id)

    if not task:
        return jsonify({"error": "Task not found"}), 404

    if "title" not in data:
        return jsonify({"error": "Missing field: title"}), 400

    if "title" in data:
        task.title = data["title"]

    db.session.commit()
    return jsonify({
        "message": "Task title updated",
        "updated_at": task.updated_at
    }), 200


@task.route("/api/my-tasks/<int:id>/priority", methods=["PATCH"])
@jwt_required()
def update_priority(id):
    data = request.get_json()

    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    task = get_user_task(id, user.id)

    if not task:
        return jsonify({"error": "Task not found or unauthorized"}), 404

    if "priority" not in data:
        return jsonify({"error": "Missing field: priority"}), 400

    new_priority = data.get("priority")
    is_valid, error_msg = validate_priority(new_priority)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    task.priority = new_priority
    db.session.commit()

    return jsonify({
        "message": f"Task priority updated to '{new_priority}'",
        "updated_at": task.updated_at
    }), 200

@task.route('/api/delete<int:id>', methods=['DELETE'])
def delete_task(id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404

    task = get_user_task(user.id, id)
    if not task:
        return jsonify({"error": "Task not found or unauthorized"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify(msg="Task deleted")