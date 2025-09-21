# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import json
import PyPDF2
import re
from google import genai

# -----------------------------
# Initialization
# -----------------------------
app = FastAPI(title="AI Career Advisor")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["YOUR_FRONTEND_SERVER_URL"],  # frontend vite server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load careers data
with open("careers.json", "r") as f:
    careers_data = json.load(f)

# Load sentence-transformers model
model = SentenceTransformer('all-MiniLM-L6-v2')

# -----------------------------
# Google Gemini AI Setup
# -----------------------------
GOOGLE_API_KEY = "PUT_YOUR_API_KEY_HERE"  # 🔑 Replace this with your real key
client = genai.Client(api_key=GOOGLE_API_KEY)

# -----------------------------
# Models
# -----------------------------
class UserSkills(BaseModel):
    skills: str  # comma-separated skills input

# -----------------------------
# Helper Functions
# -----------------------------
def get_similarity(user_skills, role_skills):
    if not user_skills.strip() or not role_skills.strip():
        return 0.0
    user_embedding = model.encode(user_skills, convert_to_tensor=True)
    role_embedding = model.encode(role_skills, convert_to_tensor=True)
    return util.cos_sim(user_embedding, role_embedding).item()

def generate_ai_advice(role, missing_skills):
    if not missing_skills:
        missing_skills = ["No missing skills detected"]

    prompt = f"""
You are a career advisor. Suggest actionable steps for a student to become a {role}.
The student is missing the following skills: {', '.join(missing_skills)}.
Provide:
- Projects to try
- Resources or courses
- Certifications
Keep it concise and practical.
"""
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI advice not available: {str(e)}"

def extract_skills_from_text(text):
    predefined_skills = ["Python", "SQL", "Machine Learning", "Data Analysis", 
                         "Deep Learning", "NLP", "TensorFlow", "React", "HTML", "CSS", 
                         "JavaScript", "Docker", "Kubernetes", "Linux", "Agile"]
    found_skills = []
    for skill in predefined_skills:
        pattern = re.compile(r"\b" + re.escape(skill) + r"\b", re.IGNORECASE)
        if pattern.search(text):
            found_skills.append(skill)
    return found_skills

def recommend_career_logic(user_skills_str):
    user_skills_list = [s.strip() for s in user_skills_str.split(",")]
    results = []

    for career in careers_data:
        role = career["role"]
        role_skills_list = career["skills"]

        sim = get_similarity(user_skills_str, " ".join(role_skills_list))
        missing_skills = [s for s in role_skills_list if s not in user_skills_list]
        ai_advice = generate_ai_advice(role, missing_skills)

        results.append({
            "role": role,
            "similarity": round(sim, 3),
            "missing_skills": missing_skills,
            "ai_advice": ai_advice
        })

    results = sorted(results, key=lambda x: x["similarity"], reverse=True)[:5]
    return results

# -----------------------------
# Endpoints
# -----------------------------
@app.post("/recommend-career")
def recommend_career(user: UserSkills):
    return {"recommendations": recommend_career_logic(user.skills)}

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return {"error": "Only PDF files are supported for now."}

    # Extract text from PDF
    try:
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}"}

    # Extract skills
    user_skills_list = extract_skills_from_text(text)
    if not user_skills_list:
        return {"error": "No recognizable skills found in the resume."}

    user_skills_str = ", ".join(user_skills_list)
    recommendations = recommend_career_logic(user_skills_str)
    return {"recommendations": recommendations}
