
# OCR and PDF Table Extraction Web App

This application allows users to upload images and PDF files to extract text, tables, and specific information such as names, emails, education, work experience, and skills. It uses OCR for images and PDF parsing libraries to extract text and tables from PDF files.

## This version focuses on getting information from CVs and Resumes

## Table of Contents

- [About the App](#about-the-app)
- [Requirements](#requirements)
- [Setting Up the Environment](#setting-up-the-environment)
- [Running the App](#running-the-app)
- [Libraries Used](#libraries-used)

## About the App

This application allows users to upload images and PDF files to extract text, tables, and specific information such as names, emails, education, work experience, and skills. It uses OCR for images and PDF parsing libraries to extract text and tables from PDF files.

## Requirements

- Python 3.7+
- pip (Python package installer)

## Setting Up the Environment

1. **Clone the repository**:
   ```
   git clone git@github.com:taofiqsulayman/text-reader.git
   cd text-reader
   ```

   switch to v4 branch

2. **Create and activate a virtual environment**:

   - On macOS and Linux:
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```

   - On Windows:
     ```
     python -m venv venv
     .\venv\Scripts\activate
     ```

3. **Install the required packages**:
   ```
   pip install -r requirements.txt
   ```

   If `requirements.txt` does not exist yet, you can manually install the required packages:


   Then, create `requirements.txt`:
   ```
   pip freeze > requirements.txt
   ```

## Running the App

1. **Ensure the virtual environment is activated**:
   ```
   source venv/bin/activate  # On macOS and Linux
   .\venv\Scripts\activate  # On Windows
   ```

2. **Run the Flask app**:
   ```
   python app.py
   ```

3. **Open a web browser and navigate to**:
   ```
   http://127.0.0.1:5000/
   ```

   You should see the upload form where you can upload images or PDF files to extract text and tables.

## Libraries Used

 **Flask**: A micro web framework for Python.
- **PyMuPDF (fitz)**: A library for PDF processing.
- **pandas**: A data manipulation and analysis library.
- **camelot-py**: A library for extracting tables from PDFs.
- **spacy**: A library for Natural Language Processing in Python.
- **OpenCV**: A library for computer vision tasks.
- **pytesseract**: A Python wrapper for Google's Tesseract-OCR Engine.


## Project Structure

```
├── app.py               # Main application file
├── templates
│   └── index.html       # HTML template for the web interface
├── static
│   ├── styles.css       # CSS file for styling (optional)
│   └── script.js        # JavaScript file for handling frontend logic
├── uploads              # Directory where uploaded files are temporarily stored
├── requirements.txt     # File listing all required Python packages
└── README.md            # This README file
```

## Example Usage

1. Upload an image (PNG, JPG, JPEG) or PDF file containing a CV/Resume through the web interface.
2. The application will extract text, tables, and specific information such as names, emails, education, work experience, and skills from the uploaded file and display the results.

## Troubleshooting

- **Camelot Dependencies**: Camelot requires additional dependencies like `ghostscript` and `opencv-python`. Ensure these are installed correctly. For macOS, you might need to install `ghostscript` using Homebrew:
  ```bash
  brew install ghostscript
  ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue if you encounter any bugs or have feature requests.

