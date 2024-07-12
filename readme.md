# OCR and PDF Text Extraction App

## Table of Contents

- [About the App](#about-the-app)
- [Requirements](#requirements)
- [Setting Up the Environment](#setting-up-the-environment)
- [Running the App](#running-the-app)
- [Libraries Used](#libraries-used)

## About the App

This application allows users to upload images and PDF files to extract text and tables. It uses OCR for images and PDF parsing libraries to extract text and tables from PDF files.

## Requirements

- Python 3.x
- Flask
- pytesseract
- Pillow
- pdfminer.six
- tabula-py

## Setting Up the Environment

1. Clone the repository:
    ```bash
    git clone https://github.com/taofiqsulayman/text-reader.git
    ```
2. Navigate to the project directory:
    ```bash
    cd text-reader
    ```
3. Create a virtual environment:
    ```bash
    python -m venv venv
    ```
4. Activate the virtual environment:

    - On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    - On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
5. Install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```

## Running the App

1. Navigate to the project directory (if not already there):
    ```bash
    cd yourproject
    ```
2. Ensure the `uploads` directory exists:
    ```bash
    mkdir uploads
    ```
3. Run the app:
    ```bash
    python app.py
    ```
4. Open your browser and go to `http://127.0.0.1:5000/` to access the application.

## Libraries Used

- **Flask**: A micro web framework for Python.
- **pytesseract**: A Python wrapper for Google's Tesseract-OCR Engine.
- **Pillow**: The Python Imaging Library fork, adds image processing capabilities to your Python interpreter.
- **pdfminer.six**: A PDF parser and analyzer.
- **tabula-py**: A library for reading tables in PDF files.

## Example Usage

1. Start the application by running:
    ```bash
    python app.py
    ```
2. Upload an image (PNG, JPG, JPEG) or PDF file through the web interface.
3. The application will extract text and tables from the uploaded file and display the results.

## Contributing

Feel free to submit issues or pull requests if you have suggestions for improvements or find bugs.

