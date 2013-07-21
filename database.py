from pymongo import MongoClient
from flask import current_app

def connect_db():
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    db = client[current_app.config['DB_DATABASE']]
    db.authenticate(current_app.config['DB_USERNAME'], current_app.config['DB_PASSWORD'])
    return db