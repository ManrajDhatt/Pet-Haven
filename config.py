import os


class Config:
    SECRET_KEY = 'supersecretkey'
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get the absolute path of the project folder
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"  
    SQLALCHEMY_TRACK_MODIFICATIONS = False


     # Flask-Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True 
    MAIL_USERNAME = 'pethaventeam01@gmail.com'  # Replace with your email
    MAIL_PASSWORD = 'gggjnbtgehzpenqx'  # Use an App Password if using Gmail
    MAIL_DEFAULT_SENDER ="pethaventeam01@gmail.com"

    
