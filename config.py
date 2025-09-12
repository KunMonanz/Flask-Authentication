from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///task.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")