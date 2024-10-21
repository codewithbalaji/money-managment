import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    MONGO_URI = "mongodb+srv://snipersanthosh02:866qtqb5cqe4Egol@cluster0.eejjw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"