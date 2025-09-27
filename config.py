import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
DB_FOLDER = os.path.join(BASE_DIR, 'db')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DB_FOLDER, exist_ok=True)

DATABASE_URI = os.path.join(DB_FOLDER, 'database.db')