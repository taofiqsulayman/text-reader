from flask import Flask, request, jsonify, render_template
import pytesseract
from PIL import Image
import os
import pdfminer
from pdfminer.high_level import extract_text
import tabula

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        filename = file.filename
        file_path = os.path.join('uploads', filename)
        file.save(file_path)

        if filename.lower().endswith(('png', 'jpg', 'jpeg')):
            text = extract_text_from_image(file_path)
        elif filename.lower().endswith('pdf'):
            text, tables = extract_text_and_tables_from_pdf(file_path)
        else:
            return jsonify({'error': 'Unsupported file type'})

        os.remove(file_path)
        return jsonify({'extracted_text': text, 'extracted_tables': tables})

    return jsonify({'error': 'File upload failed'})

def extract_text_from_image(file_path):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(image)
    return text

def extract_text_and_tables_from_pdf(file_path):
    text = extract_text(file_path)
    tables = tabula.read_pdf(file_path, pages='all', multiple_tables=True)
    tables_json = [table.to_json(orient='split') for table in tables]
    return text, tables_json

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
