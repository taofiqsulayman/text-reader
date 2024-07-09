from flask import Flask, request, jsonify, render_template
import os
import fitz  # PyMuPDF

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
                if page.get_images():
                    for item in page.get_images():
                        xref = item[0]
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n < 4:  # this is GRAY or RGB
                            pdfdata = pix.pdfocr_tobytes()
                        else:  # CMYK: convert to RGB first
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                            pdfdata = pix.pdfocr_tobytes()
                        ocrpdf = fitz.open("pdf", pdfdata)
                        text += ocrpdf[0].get_text()
                tables_found = page.find_tables()
                for table in tables_found:
                    df = table.to_pandas()
                    cleaned_table = clean_up_table(df)
                    tables.append(convert_table_to_json(cleaned_table))

        return text, tables

    except Exception as e:
        app.logger.error(f"Error extracting text/tables from PDF: {e}")
        raise

def convert_table_to_json(table):
    return table.to_json(orient='split')

def clean_up_table(df):
    df = df.dropna(how='all').dropna(axis=1, how='all')
    df = df.fillna('')
    return df

def convert_table_to_json(table):
    return table.to_json(orient='split')

def clean_up_table(df):
    df = df.dropna(how='all').dropna(axis=1, how='all')
    df = df.fillna('')
    return df

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    # Set the TESSDATA_PREFIX environment variable
    os.environ['TESSDATA_PREFIX'] = '/usr/local/Cellar/tesseract/5.4.1/share/tessdata'  # Update this path as needed
    app.run(debug=True)
