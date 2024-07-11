from flask import Flask, request, jsonify, render_template
import os
import fitz  # PyMuPDF
import pandas as pd
import camelot
import spacy
from spacy.pipeline import EntityRuler
import re

app = Flask(__name__)

nlp = spacy.load("en_core_web_sm")


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
    return table.to_json(orient="split")


def clean_up_table(df):
    df = df.dropna(how="all").dropna(axis=1, how="all")
    df = df.apply(
        lambda x: x.str.strip() if x.dtype == "object" else x
    )  # Strip whitespace from strings
    df = df.replace("", pd.NA)  # Convert empty strings to NaNs
    df = df.dropna(how="all").dropna(
        axis=1, how="all"
    )  # Drop rows and columns with all NaNs
    return df


def extract_name(text):
    name_pattern = re.compile(r"\b([A-Z][a-z]* [A-Z][a-z]*)\b")
    names = name_pattern.findall(text)
    return names[0] if names else None


def extract_email(text):
    email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    emails = email_pattern.findall(text)
    return emails[0] if emails else None


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
    nlp.add_pipe(
        "entity_ruler", name="entity_ruler", last=True
    )  # Pass the string name 'entity_ruler'
    return nlp


def extract_info(text):
    nlp = create_nlp_pipeline()
    doc = nlp(text)

    info = {
        "name": "",
        "email": "",
        "education": [],
        "work_experience": [],
        "links": [],
        "skills": [],
    }

    # Extract name, email, and links separately
    info["name"] = extract_name(text)
    info["email"] = extract_email(text)
    info["links"] = extract_links(text)

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
        "education": r"EDUCATION\n(.*?)(?:\nSKILLS|\n$)",
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
    info["education"] = (
        sections["education"].split("\n") if sections["education"] else []
    )
    info["work_experience"] = (
        sections["work_experience"].split("\n") if sections["work_experience"] else []
    )
    info["skills"] = sections["skills"].split("\n") if sections["skills"] else []

    return info


if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    # Set the TESSDATA_PREFIX environment variable
    os.environ["TESSDATA_PREFIX"] = (
        "/usr/local/Cellar/tesseract/5.4.1/share/tessdata"  # Update this path as needed
    )
    app.run(debug=True)
