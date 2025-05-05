import os
import uuid
import json
from flask import Flask, request, url_for, send_from_directory, render_template, jsonify

app = Flask(__name__)

# Folder to store uploaded files (use /tmp for Render.com compatibility)
UPLOAD_FOLDER = '/tmp/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# File to store the file mapping (use /tmp for Render.com compatibility)
FILE_MAPPING_PATH = '/tmp/file_mapping.json'

# Load file mapping from JSON file
if os.path.exists(FILE_MAPPING_PATH):
    if os.path.getsize(FILE_MAPPING_PATH) > 0:  # Check if the file is not empty
        with open(FILE_MAPPING_PATH, 'r') as f:
            file_mapping = json.load(f)
    else:
        file_mapping = {}
else:
    file_mapping = {}

# Save file mapping to JSON file
def save_file_mapping():
    with open(FILE_MAPPING_PATH, 'w') as f:
        json.dump(file_mapping, f)

# Route: Home page displaying the upload form
@app.route('/')
def index():
    return render_template('index.html')

# Route: Handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part in the request.", 400
    file = request.files['file']
    if file.filename == '':
        return "No file selected.", 400
    if file:
        unique_filename = f"{uuid.uuid4()}"
        file_mapping[unique_filename] = file.filename
        save_file_mapping()
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        download_url = url_for('download_file', unique_filename=unique_filename, _external=True)
        return jsonify({"download_url": download_url, "original_filename": file.filename})
    return "File upload failed.", 400

# Route: Serve the uploaded file
@app.route('/uploads/<unique_filename>')
def download_file(unique_filename):
    original_filename = file_mapping.get(unique_filename)
    if original_filename:
        return send_from_directory(app.config['UPLOAD_FOLDER'], unique_filename, as_attachment=True, download_name=original_filename)
    return "File not found.", 404

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT environment variable provided by Render
    app.run(host='0.0.0.0', port=port, debug=False)  # Bind to 0.0.0.0 for external access
