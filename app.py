from flask import Flask, request, jsonify, render_template
import os
import cv2
import pytesseract
import pandas as pd
import camelot
import fitz

app = Flask(__name__)

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
                text, tables = extract_text_and_tables_from_image(file_path)
            elif filename.lower().endswith('pdf'):
                text, tables = extract_text_and_tables_from_pdf(file_path)
            else:
                return jsonify({'error': 'Unsupported file type'}), 400

            os.remove(file_path)
            return jsonify({'extracted_text': text, 'extracted_tables': tables}), 200

    except Exception as e:
        app.logger.error(f"Error processing file: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

def extract_text_and_tables_from_image(file_path):
    try:
        img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        inverted_thresh = cv2.bitwise_not(thresh)

        # Detect lines in the image
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        detect_horizontal = cv2.morphologyEx(inverted_thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        detect_vertical = cv2.morphologyEx(inverted_thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

        mask = detect_horizontal + detect_vertical

        # Find contours and filter out table contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        table_contours = [c for c in contours if cv2.contourArea(c) > 1000]

        tables = []
        for contour in table_contours:
            x, y, w, h = cv2.boundingRect(contour)
            table_image = img[y:y+h, x:x+w]
            table_text = pytesseract.image_to_string(table_image, config='--psm 6')
            tables.append(table_text)

        # TODO: this method is not very accurate, need to improve it....

        text = pytesseract.image_to_string(img)

        return text, tables

    except Exception as e:
        app.logger.error(f"Error extracting text/tables from image: {e}")
        raise

def extract_text_and_tables_from_pdf(file_path):
    try:
        text = ""
        tables = []

        # Extract text from PDF
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text")

        # Extract tables using Camelot
        camelot_tables = camelot.read_pdf(file_path, pages='all')
        for table in camelot_tables:
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

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    # Set the TESSDATA_PREFIX environment variable
    os.environ['TESSDATA_PREFIX'] = '/usr/local/Cellar/tesseract/5.4.1/share/tessdata'  # Update this path as needed depending on the version installed
    app.run(debug=True)
