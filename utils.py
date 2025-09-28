import os
import time
from config import UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'mp4', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, folder='files'):
    if not file:
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{int(time.time() * 1000)}_{folder}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return f"/uploads/{filename}"  # 返回相对URL