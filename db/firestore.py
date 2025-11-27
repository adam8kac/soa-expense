import os
import json
import base64
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv

load_dotenv()

FIREBASE_CREDENTIALS_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_B64")

decoded_credentials = base64.b64decode(FIREBASE_CREDENTIALS_JSON).decode("utf-8")

cred_dict = json.loads(decoded_credentials)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()


def get_db():
    return db
