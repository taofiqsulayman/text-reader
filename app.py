from flask import Flask, request, jsonify, render_template
import os
import fitz  # PyMuPDF
import pandas as pd
import camelot
import spacy
from spacy.tokens import DocBin
from spacy.matcher import Matcher

app = Flask(__name__)

nlp = spacy.load("en_core_web_sm")

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

            extracted_info = extract_info_with_spacy(text)

            return jsonify({'extracted_text': text, 'extracted_tables': tables, 'extracted_info': extracted_info}), 200

    except Exception as e:
        app.logger.error(f"Error processing file: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

def extract_text_from_image(file_path):
    try:
        pix = fitz.Pixmap(file_path)
        if pix.n < 4:  # this is GRAY or RGB
            pdfdata = pix.pdfocr_tobytes()
        else:  # CMYK: convert to RGB first
            pix = fitz.Pixmap(fitz.csRGB, pix)
            pdfdata = pix.pdfocr_tobytes()
        ocrpdf = fitz.open("pdf", pdfdata)
        text = ocrpdf[0].get_text()
        return text
    except Exception as e:
        app.logger.error(f"Error extracting text from image: {e}")
        raise

def extract_text_and_tables_from_pdf(file_path):
    try:
        text = ""
        tables = []

        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text")
                tables_found = camelot.read_pdf(file_path, pages=str(page.number + 1))
                for table in tables_found:
                    df = table.df
                    cleaned_table = clean_up_table(df)
                    if not cleaned_table.empty:
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
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)  # Strip whitespace from strings
    df = df.replace("", pd.NA)  # Convert empty strings to NaNs
    df = df.dropna(how='all').dropna(axis=1, how='all')  # Drop rows and columns with all NaNs
    return df

def extract_info_with_spacy(text):
    doc = nlp(text)

    matcher = Matcher(nlp.vocab)

    # Define patterns for matching
    patterns = [
        {"label": "PERSON", "pattern": [{"ENT_TYPE": "PERSON"}]},
        {"label": "EMAIL", "pattern": [{"LIKE_EMAIL": True}]},
        {"label": "EDUCATION", "pattern": [{"LOWER": {"IN": ["b.a.", "m.a.", "phd", "degree", "university", "college"]}}]},
        {"label": "WORK_EXPERIENCE", "pattern": [{"LOWER": {"IN": ["experience", "work", "employment", "job", "position"]}}]},
        {"label": "URL", "pattern": [{"LIKE_URL": True}]},
        {"label": "SKILL", "pattern": [{"LOWER": {"IN": ["communication", "problem-solving", "customer service", "teamwork", "project management", "event planning", "google suite", "canva", "capcut"]}}]}
    ]

    for pattern in patterns:
        matcher.add(pattern["label"], [pattern["pattern"]])

    matches = matcher(doc)

    info = {
        "name": [],
        "email": [],
        "education": [],
        "work_experience": [],
        "links": [],
        "skills": []
    }

    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        span = doc[start:end]
        if label == "PERSON":
            info["name"].append(span.text)
        elif label == "EMAIL":
            info["email"].append(span.text)
        elif label == "EDUCATION":
            info["education"].append(span.text)
        elif label == "WORK_EXPERIENCE":
            info["work_experience"].append(span.text)
        elif label == "URL":
            info["links"].append(span.text)
        elif label == "SKILL":
            info["skills"].append(span.text)

    return info

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    # Set the TESSDATA_PREFIX environment variable
    os.environ['TESSDATA_PREFIX'] = '/usr/local/Cellar/tesseract/5.4.1/share/tessdata'  # Update this path as needed
    app.run(debug=True)
