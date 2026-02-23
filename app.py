import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from image_processor import process_full_pipeline

app = Flask(__name__)
UPLOAD_FOLDER = 'Input Image'
OUTPUT_FOLDER = 'Output Images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    results, original_size = process_full_pipeline(filepath, app.config['OUTPUT_FOLDER'])
    return jsonify({
        "original_filename": filename,
        "original_size_kb": round(original_size, 2),
        "results": results
    })

@app.route('/image/<type>/<filename>')
def serve_image(type, filename):
    folder = app.config['UPLOAD_FOLDER'] if type == 'original' else app.config['OUTPUT_FOLDER']
    return send_from_directory(folder, filename)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
