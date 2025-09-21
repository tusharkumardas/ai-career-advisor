ROLE_DOCS = {
    "data_scientist": {
        "title": "Data Scientist",
        "desc": "Requires python, pandas, statistics, machine learning",
        "skills": ["python", "pandas", "statistics", "machine learning"],
        "source": "seed-corpus"
    },
    "product_manager": {
        "title": "Product Manager",
        "desc": "Requires product thinking, roadmap, stakeholder management, analytics",
        "skills": ["product management", "roadmap", "analytics"],
        "source": "seed-corpus"
    }
}

def knn_roles(extracted_profile, topk=3):
    user_skills = {s['name'] for s in extracted_profile.get('skills', [])}
    scores = []
    for role_id, doc in ROLE_DOCS.items():
        overlap = len(user_skills.intersection(set(doc['skills'])))
        scores.append((role_id, overlap))
    scores.sort(key=lambda x: -x[1])
    out = []
    for role_id, score in scores[:topk]:
        doc = ROLE_DOCS[role_id]
        missing = [s for s in doc['skills'] if s not in user_skills]
        out.append({
            "id": role_id,
            "title": doc["title"],
            "score": score,
            "missing_skills": missing,
            "source": doc["source"]
        })
    return out
