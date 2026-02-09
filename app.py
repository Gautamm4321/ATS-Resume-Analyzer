from flask import Flask, render_template, request
import pdfplumber

app = Flask(__name__)

def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print("PDF Error:", e)
    return text.lower()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    resume_text = ""

    if 'resume' not in request.files:
        return "No file uploaded", 400

    file = request.files['resume']

    if file.filename == "":
        return "No file selected", 400

    if not file.filename.lower().endswith('.pdf'):
        return "Only PDF files allowed", 400

    resume_text = extract_text_from_pdf(file)

    score = 0
    feedback = []

    education = ["education", "qualification", "academic"]
    experience = ["experience", "work experience", "employment"]
    skills = ["skills", "technical skills"]
    projects = ["projects", "project"]

    if any(word in resume_text for word in education):
        score += 20
    else:
        feedback.append("Add a clear Education section with degree details.")

    if any(word in resume_text for word in experience):
        score += 30
    else:
        feedback.append("Experience section is missing or lacks detail.")

    if any(word in resume_text for word in skills):
        score += 30
    else:
        feedback.append("Mention technical and soft skills clearly.")

    if any(word in resume_text for word in projects):
        score += 20
    else:
        feedback.append("Projects section not found. Add academic or personal projects.")

    if score >= 80:
        verdict = "Excellent ATS-friendly resume"
    elif score >= 60:
        verdict = "Good resume, minor improvements needed"
    else:
        verdict = "Resume needs significant improvement"

    return render_template(
        "result.html",
        score=score,
        feedback=feedback,
        verdict=verdict
    )

if __name__ == "__main__":
    app.run()
