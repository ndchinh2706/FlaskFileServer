from flask import Flask, request, jsonify, send_file
import os
import random
import string
from werkzeug.utils import secure_filename
from unidecode import unidecode

app = Flask(__name__)

# Predefined token for authentication
AUTH_TOKEN = 'your-predefined-token'

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploaded'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_random_string(length=7):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Processing Vietnamese filename
def clean_filename(filename):
    cleaned_filename = unidecode(filename)
    cleaned_filename = cleaned_filename.replace(' ', '-')
    return cleaned_filename

# Handle duplicate filename
def handle_duplicate_filename(filename):
    name, ext = os.path.splitext(filename)
    cleaned_name = clean_filename(name)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{cleaned_name}{ext}")
    while os.path.exists(file_path):
        cleaned_name_with_random = f"{cleaned_name}-{generate_random_string()}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{cleaned_name_with_random}{ext}")
    
    return file_path

# Validating token
def validate_token(request):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header == f"{AUTH_TOKEN}":
        return True
    return False

# POST route
@app.route('/upload', methods=['POST'])
def upload_file():
    if not validate_token(request):
        return jsonify({"msg": "Unauthorized"}), 401
    
    if 'file' not in request.files:
        return jsonify({"msg": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    file_path = handle_duplicate_filename(filename)
    
    file.save(file_path)
    
    return jsonify({"msg": "File uploaded successfully", "filename": os.path.basename(file_path)}), 201

# GET route
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    if not validate_token(request):
        return jsonify({"msg": "Unauthorized"}), 401
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"msg": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
