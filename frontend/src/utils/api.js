const API_BASE = "http://127.0.0.1:8080";

export async function analyzeProfile(profile) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
  return res.json();
}

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/upload_resume`, {
    method: "POST",
    body: formData,
  });

  return res.json();
}
