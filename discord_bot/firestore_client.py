import json

import firebase_admin
from config import config
from firebase_admin import credentials


def initialize_firebase():
    try:
        cred_filename = config.FIREBASE_SERVICE_ACCOUNT
        with open(cred_filename, "r") as f:
            cred_json = f.read()
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        raise
