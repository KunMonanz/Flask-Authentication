from flask import Blueprint, request, jsonify
from models import db, User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    required_fields = ["username", "email", "password"]
    missing_fields = [field for field in required_fields if not data.get(field)]

    if missing_fields:
        return jsonify(msg=f"Missing field(s): {', '.join((missing_fields))}"), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify(msg=f"Username {data["username"]} exists"), 409

    if User.query.filter_by(email=data["email"]).first():
        return jsonify(msg=f"Email {data["email"]} exists"), 409

    user = User(
        username=data["username"],
        email=data["email"]
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.add(user)
    db.session.commit()
    return jsonify(msg="User registered"), 201

@auth_bp.route('/login', methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if user and user.check_password(data["password"]):
        token = create_access_token(identity=user.username)
        return jsonify(access_token=token)
    return jsonify(msg="Invalid credentials, user does not exist")