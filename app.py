import re
import fitz  # PyMuPDF
import pandas as pd
from flask import Flask, request, jsonify, render_template
import os

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

            if filename.lower().endswith('pdf'):
                extracted_info = extract_info_from_pdf(file_path)
            else:
                return jsonify({'error': 'Unsupported file type'}), 400

            os.remove(file_path)
            return jsonify({'extracted_info': extracted_info}), 200

    except Exception as e:
        app.logger.error(f"Error processing file: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

def extract_info_from_pdf(file_path):
    try:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text("text")

        # Extract information using regex
        extracted_info = {
            'name': extract_name(text),
            'email': extract_email(text),
            'links': extract_links(text),
            'experience': extract_experience(text),
            'education': extract_education(text),
            'skills': extract_skills(text)
        }

        return extracted_info

    except Exception as e:
        app.logger.error(f"Error extracting info from PDF: {e}")
        raise

def extract_name(text):
    # Implement a regex to find the name (this is a simplified example)
    name_pattern = re.compile(r'\b([A-Z][a-z]* [A-Z][a-z]*)\b')
    names = name_pattern.findall(text)
    return names[0] if names else None

def extract_email(text):
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    emails = email_pattern.findall(text)
    return emails[0] if emails else None

def extract_links(text):
    link_pattern = re.compile(r'\bhttps?://\S+\b')
    links = link_pattern.findall(text)
    return links

def extract_experience(text):
    # Extract experience details (this is a simplified example)
    experience_pattern = re.compile(r'(Experience|Work History)(.*?)(Education|Skills)', re.DOTALL)
    experience = experience_pattern.findall(text)
    return experience[0][1].strip() if experience else None

def extract_education(text):
    # Extract education details (this is a simplified example)
    education_pattern = re.compile(r'(Education)(.*?)(Experience|Skills)', re.DOTALL)
    education = education_pattern.findall(text)
    return education[0][1].strip() if education else None

def extract_skills(text):
    # Extract skills details (this is a simplified example)
    skills_pattern = re.compile(r'(Skills)(.*)', re.DOTALL)
    skills = skills_pattern.findall(text)
    return skills[0][1].strip() if skills else None

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
