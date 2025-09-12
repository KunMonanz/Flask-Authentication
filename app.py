from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import Config
from models import db
from auth import auth_bp
from task import task

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(task)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
