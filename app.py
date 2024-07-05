from flask import Flask, request, jsonify, render_template
import os
import pdfplumber
from paddleocr import PaddleOCR
import pandas as pd
import camelot

app = Flask(__name__)
ocr = PaddleOCR(use_angle_cls=True)  # Initialize the PaddleOCR

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file:
            filename = file.filename
            file_path = os.path.join('uploads', filename)
            file.save(file_path)

            if filename.lower().endswith(('png', 'jpg', 'jpeg')):
                text = extract_text_from_image(file_path)
                tables = []  # No tables to extract from images
            elif filename.lower().endswith('pdf'):
                text, tables = extract_text_and_tables_from_pdf(file_path)
            else:
                return jsonify({'error': 'Unsupported file type'}), 400

            os.remove(file_path)
            return jsonify({'extracted_text': text, 'extracted_tables': tables}), 200

    except Exception as e:
        app.logger.error(f"Error processing file: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

def extract_text_from_image(file_path):
    try:
        result = ocr.ocr(file_path, cls=True)
        text = "\n".join([line[1][0] for line in result[0]])
        return text
    except Exception as e:
        app.logger.error(f"Error extracting text from image: {e}")
        raise

def extract_text_and_tables_from_pdf(file_path):
    try:
        text = ""
        tables = []

        # Use pdfplumber for text extraction
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text()

        # Use Camelot for table extraction
        tables_pdf = camelot.read_pdf(file_path, pages='all')
        for table_pdf in tables_pdf:
            df = table_pdf.df
            cleaned_table = clean_up_table(df)
            tables.append(convert_table_to_json(cleaned_table))

        return text, tables

    except Exception as e:
        app.logger.error(f"Error extracting text/tables from PDF: {e}")
        raise

def convert_table_to_json(table):
    # Convert DataFrame to JSON
    return table.to_json(orient='split')

def clean_up_table(df):
    df = df.dropna(how='all').dropna(axis=1, how='all')
    df = df.fillna('')
    return df

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
