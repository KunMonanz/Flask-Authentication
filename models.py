from datetime import datetime, timezone
from email.policy import default

from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func
from  flask_sqlalchemy import SQLAlchemy
from werkzeug.security import  generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    tasks = db.relationship("Task", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=True)
    description = db.Column(db.String(256), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='default')
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("priority IN ('high', 'medium', 'low', 'default')", name='check_priority'),
    )