from flask import Flask, render_template, request
import pdfplumber
from groq import Groq
import json
import re
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def analyze_with_ai(resume_text, job_description, candidate_info):
    prompt = f"""
You are an expert ATS (Applicant Tracking System) and senior recruiter.
Analyze the following resume against the job description provided.

=== CANDIDATE'S EXTRA INFO ===
{candidate_info if candidate_info else "Not provided"}

=== JOB DESCRIPTION ===
{job_description if job_description else "No specific job description provided. Do a general ATS analysis."}

=== RESUME TEXT ===
{resume_text}

Return ONLY valid JSON (no markdown, no code fences) in this exact structure:
{{
  "ats_score": <integer 0-100>,
  "match_score": <integer 0-100>,
  "skills_found": <integer count>,
  "experience_years": <integer or 0>,
  "missing_keywords_count": <integer>,
  "candidate_name": "<full name from resume>",
  "candidate_summary": "<2-3 sentence professional summary>",
  "strengths": ["strength1", "strength2", "strength3", "strength4"],
  "weaknesses": ["weakness1", "weakness2", "weakness3"],
  "missing_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "skills_matched": ["skill1", "skill2", "skill3", "skill4", "skill5"],
  "improvements": [
    "Specific actionable improvement 1",
    "Specific actionable improvement 2",
    "Specific actionable improvement 3",
    "Specific actionable improvement 4",
    "Specific actionable improvement 5"
  ],
  "verdict": "<one-line hiring verdict>"
}}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except Exception:
        return {
            "ats_score": 50,
            "match_score": 50,
            "skills_found": 0,
            "experience_years": 0,
            "missing_keywords_count": 0,
            "candidate_name": "Unknown",
            "candidate_summary": "AI parsing failed. Raw: " + raw[:200],
            "strengths": ["N/A"],
            "weaknesses": ["N/A"],
            "missing_keywords": [],
            "skills_matched": [],
            "improvements": ["Try again with a clearer PDF."],
            "verdict": "Could not analyze properly."
        }

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return render_template("index.html", error="Please upload a resume.")
    file = request.files["resume"]
    if file.filename == "":
        return render_template("index.html", error="No file selected.")
    job_description = request.form.get("job_description", "").strip()
    candidate_info = request.form.get("candidate_info", "").strip()
    try:
        resume_text = extract_text_from_pdf(file)
        if not resume_text.strip():
            return render_template("index.html", error="Could not read PDF. Try another file.")
        result = analyze_with_ai(resume_text, job_description, candidate_info)
        return render_template("result.html", result=result)
    except Exception as e:
        return render_template("index.html", error=f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)