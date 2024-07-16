from flask import Flask, request, jsonify, render_template
import os
import fitz  # PyMuPDF
import pandas as pd
import camelot
import spacy
from spacy.pipeline import EntityRuler
from spacy.matcher import Matcher
import re

import nltk

nltk.download("stopwords")
from nltk.corpus import stopwords

app = Flask(__name__)

nlp = spacy.load("en_core_web_sm")
stop_words = set(stopwords.words("english"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file:
            filename = file.filename
            file_path = os.path.join("uploads", filename)
            file.save(file_path)

            if filename.lower().endswith(("png", "jpg", "jpeg")):
                text = extract_text_from_image(file_path)
                tables = []  # No tables to extract from images
            elif filename.lower().endswith("pdf"):
                text, tables = extract_text_and_tables_from_pdf(file_path)
            else:
                return jsonify({"error": "Unsupported file type"}), 400

            os.remove(file_path)

            extracted_info = process_extracted_text(text)

            return (
                jsonify(
                    {
                        "extracted_text": text,
                        "extracted_tables": tables,
                        "extracted_info": extracted_info,
                    }
                ),
                200,
            )

    except Exception as e:
        app.logger.error(f"Error processing file: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route("/analyze", methods=["POST"])
def analyze_cv():
    try:
        if "file" not in request.files or "job_description" not in request.form:
            return jsonify({"error": "Missing required parameters"}), 400

        file = request.files["file"]
        job_description = request.form["job_description"]

        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400

        if file:
            filename = file.filename
            file_path = os.path.join("uploads", filename)
            file.save(file_path)

            with fitz.open(file_path) as doc:
                resume_text = ""
                for page in doc:
                    resume_text += page.get_text("text")

            os.remove(file_path)
            extracted_info = process_extracted_text(resume_text)

            match_percentage, matching_skills = analyze_job_description(
                job_description, clean_text(resume_text)
            )

            cleaned = clean_text(resume_text)

            return (
                jsonify(
                    {
                        "job_description": job_description,
                        "extracted_info": extracted_info,
                        "match_percentage": match_percentage,
                        "matching_skills": matching_skills,
                        "cleaned_text": cleaned,
                    }
                ),
                200,
            )

    except Exception as e:
        app.logger.error(f"Error analyzing CV: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


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
    return table.to_json(orient="split")


def clean_text(text):
    # Remove hyperlinks
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)

    # Remove special characters and punctuations
    text = re.sub(r"[^A-Za-z0-9\s]", "", text)

    text = text.lower()

    text_tokens = text.split()
    filtered_text = [word for word in text_tokens if word not in stop_words]

    return " ".join(filtered_text)


def clean_up_table(df):
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    df = df.replace("", pd.NA)
    df = df.dropna(how="all").dropna(axis=1, how="all")
    return df


# def extract_name(text):
#     name_pattern = re.compile(r"\b([A-Z][a-z]* [A-Z][a-z]*)\b")
#     names = name_pattern.findall(text)
#     return names[0] if names else None


def extract_name(resume_text):
    nlp = spacy.load("en_core_web_md")
    matcher = Matcher(nlp.vocab)

    # Define name patterns
    patterns = [
        [{"POS": "PROPN"}, {"POS": "PROPN"}],  # First name and Last name
        [
            {"POS": "PROPN"},
            {"POS": "PROPN"},
            {"POS": "PROPN"},
        ],  # First name, Middle name, and Last name
        [
            {"POS": "PROPN"},
            {"POS": "PROPN"},
            {"POS": "PROPN"},
            {"POS": "PROPN"},
        ],  # First name, Middle name, Middle name, and Last name
        # Add more patterns as needed
    ]

    for pattern in patterns:
        matcher.add("NAME", patterns=[pattern])

    doc = nlp(resume_text)
    matches = matcher(doc)

    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text

    return None


def extract_education(text):
    # Remove new lines from the text
    text = text.replace("\n", " ")

    education = []

    # Expanded regex pattern to find education information
    pattern = r"(?i)(?:Bsc|B\.A|B\.S|B\.Eng|B\.Tech|B\.Ed|B\.Com|B\.Pharm|B\.Nurs|B\.Arch|B\.Bus|B\.Admin|B\.Fin|Msc|M\.A|M\.S|M\.Eng|M\.Tech|M\.Ed|M\.Com|M\.Pharm|M\.Nurs|M\.Arch|M\.Bus|M\.Admin|M\.Fin|Ph\.D|Doctorate|Associate|Diploma|Certificate|Bachelor(?:'s)?|Master(?:'s)?|Doctorate(?:'s)?|Ph\.D)\s(?:\w+\s)*\w+"

    matches = re.findall(pattern, text)
    for match in matches:
        education.append(match.strip())

    return education


# def extract_email(text):
#     email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
#     emails = email_pattern.findall(text)
#     return emails[0] if emails else None


def extract_email(text):
    email = None

    # Use regex pattern to find a potential email address
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    if match:
        email = match.group()

    return email


def extract_contact_number(text):
    contact_number = None

    # Use regex pattern to find a potential contact number
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    if match:
        contact_number = match.group()

    return contact_number


def extract_links(text):
    link_pattern = re.compile(r"\bhttps?://\S+\b")
    links = link_pattern.findall(text)
    return links


def create_nlp_pipeline():
    nlp = spacy.blank("en")
    ruler = EntityRuler(nlp, overwrite_ents=True)

    patterns = [
        {
            "label": "EDUCATION",
            "pattern": [{"LOWER": "b.a."}, {"LOWER": "m.a."}, {"LOWER": "phd"}],
        },
        {"label": "SKILLS", "pattern": [{"LOWER": "skills"}]},
        {
            "label": "WORK_EXPERIENCE",
            "pattern": [
                {"LOWER": {"IN": ["work", "experience", "history"]}},
                {"LOWER": {"IN": ["work", "experience", "history"]}, "OP": "?"},
            ],
        },
    ]

    ruler.add_patterns(patterns)
    nlp.add_pipe("entity_ruler", name="entity_ruler", last=True)
    return nlp


def extract_info(text):
    nlp = create_nlp_pipeline()
    doc = nlp(text)

    info = {
        "name": "",
        "email": "",
        "contact_number": "",
        "education": [],
        "work_experience": [],
        "links": [],
        "skills": [],
    }

    # Extract name, email, and links separately
    info["name"] = extract_name(text)
    info["email"] = extract_email(text)
    info["links"] = extract_links(text)
    info["education"] = extract_education(text)
    info["contact_number"] = extract_contact_number(text)

    for ent in doc.ents:
        if ent.label_ == "EDUCATION":
            info["education"].append(ent.text)
        elif ent.label_ == "WORK_EXPERIENCE":
            info["work_experience"].append(ent.text)
        elif ent.label_ == "SKILLS":
            info["skills"].append(ent.text)

    return info


def process_extracted_text(extracted_text):
    sections = {
        "name": "",
        "email": "",
        "education": "",
        "work_experience": "",
        "skills": "",
    }

    sections_pattern = {
        "work_experience": r"(?i)(WORK|EXPERIENCE|HISTORY)\n(.*?)(?:\nEDUCATION|\n$)",
        "skills": r"SKILLS\n(.*)",
    }

    for section, pattern in sections_pattern.items():
        match = re.search(pattern, extracted_text, re.DOTALL)
        if match:
            sections[section] = (
                match.group(2).strip() if match.groups() else match.group(0).strip()
            )

    # Process name and email separately
    info = extract_info(extracted_text)
    info["work_experience"] = (
        sections["work_experience"].split("\n") if sections["work_experience"] else []
    )
    info["skills"] = sections["skills"].split("\n") if sections["skills"] else []

    return info


def find_skills_in_cv(job_description, cv_text):
    # Normalize job description by replacing newlines with commas if any
    job_description = job_description.replace("\n", ",")

    # Convert job description to an array of skills
    required_skills = [
        skill.strip().lower() for skill in job_description.split(",") if skill.strip()
    ]

    # Prepare the CV text for searching
    cv_text_lower = cv_text.lower()

    # Dictionary to store whether each skill is found in the CV
    skills_found = {}

    # Search for each skill in the CV text
    for skill in required_skills:
        skills_found[skill] = skill in cv_text_lower

    return skills_found


def analyze_job_description(job_description, resume_text):
    skills_found = find_skills_in_cv(job_description, resume_text)
    total_skills = len(skills_found)
    matched_skills = sum(found for found in skills_found.values())
    match_percentage = (
        round((matched_skills / total_skills) * 100, 1) if total_skills > 0 else 0
    )
    matching_skills = [skill for skill, found in skills_found.items() if found]
    return match_percentage, matching_skills


if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    # Set the TESSDATA_PREFIX environment variable
    os.environ["TESSDATA_PREFIX"] = "/usr/share/tesseract-ocr/4.00/tessdata/"
    app.run(debug=True)
