import os
import cloudinary
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_secret_key')  
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"  
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True 
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'pethaventeam01@gmail.com')

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL") 
if CLOUDINARY_URL:
    from urllib.parse import urlparse

    parsed_url = urlparse(CLOUDINARY_URL)
    cloud_name = parsed_url.hostname.split('.')[0]
    api_key = parsed_url.username
    api_secret = parsed_url.password

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret
    )
