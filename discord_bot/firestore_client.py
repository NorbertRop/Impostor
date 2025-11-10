import json

import firebase_admin
from config import config
from firebase_admin import credentials, firestore


def initialize_firebase():
    try:
        cred_json = config.FIREBASE_SERVICE_ACCOUNT
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        raise


db = None


def get_db():
    global db
    if db is None:
        db = firestore.client()
    return db

