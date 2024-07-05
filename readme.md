
# OCR and PDF Table Extraction Web App

This is a simple web application built with Flask that allows users to upload images or PDF files and extract text and tables from them. The application leverages PaddleOCR for image text extraction and Camelot for PDF table extraction.

## Table of Contents

- [About the App](#about-the-app)
- [Requirements](#requirements)
- [Setting Up the Environment](#setting-up-the-environment)
- [Running the App](#running-the-app)
- [Libraries Used](#libraries-used)

## About the App

This web application allows users to upload image files (PNG, JPG, JPEG) or PDF documents. The app extracts text from the uploaded files and, in the case of PDFs, also extracts tables. The extracted text and tables are then displayed on the web interface.

## Requirements

- Python 3.7+
- pip (Python package installer)

## Setting Up the Environment

1. **Clone the repository**:
   ```
   git clone git@github.com:taofiqsulayman/text-reader.git
   cd text-reader
   ```

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
   ```
   pip install flask paddlepaddle paddleocr pdfplumber pandas camelot-py[cv]
   ```

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

- **Flask**: A micro web framework written in Python.
- **PaddleOCR**: An OCR tool developed by PaddlePaddle, which provides text detection and recognition capabilities.
- **pdfplumber**: A library for extracting text, tables, and metadata from PDFs.
- **Camelot**: A Python library to extract tabular data from PDFs.
- **Pandas**: A data manipulation and analysis library, used for cleaning and formatting extracted tables.

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

1. **Upload an Image**: Upload a PNG, JPG, or JPEG file to extract text from the image using PaddleOCR.
2. **Upload a PDF**: Upload a PDF file to extract text and tables using pdfplumber and Camelot.

## Troubleshooting

- **PaddleOCR Installation Issues**: If you encounter issues installing PaddleOCR, ensure you have the correct version of PaddlePaddle installed. Refer to the [PaddlePaddle installation guide](https://www.paddlepaddle.org.cn/install/quick) for more details.
- **Camelot Dependencies**: Camelot requires additional dependencies like `ghostscript` and `opencv-python`. Ensure these are installed correctly. For macOS, you might need to install `ghostscript` using Homebrew:
  ```bash
  brew install ghostscript
  ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue if you encounter any bugs or have feature requests.

