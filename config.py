
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_secret_key')  
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  
    DB_DIR = "/var/lib/sqlite/"  # Persistent storage in Render
    # SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}" 
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_DIR}database.db"  
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail Configuration (Now using env variables)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True 
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'pethaventeam01@gmail.com')

    
