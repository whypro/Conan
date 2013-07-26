from pymongo import MongoClient
from flask import current_app

def connect_db():
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    db = client[current_app.config['DB_DATABASE']]
    db.authenticate(current_app.config['DB_USERNAME'], current_app.config['DB_PASSWORD'])
    return db
    
    
def connect_backup_db(db_name):
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    db = client[db_name]
    db.authenticate(current_app.config['DB_USERNAME'], current_app.config['DB_PASSWORD'])
    return db
    
def drop_db(db_name):
    client = MongoClient(current_app.config['DB_HOST'], current_app.config['DB_PORT'])
    if db_name in client.database_names():
        client.drop_database(db_name)