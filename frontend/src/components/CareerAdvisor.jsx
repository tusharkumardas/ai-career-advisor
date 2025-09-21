// frontend/src/components/CareerAdvisor.jsx
import React, { useState } from "react";

const backendURL = "http://127.0.0.1:8000";

export default function CareerAdvisor() {
  const [skills, setSkills] = useState("");
  const [resume, setResume] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setResume(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setRecommendations([]);

    try {
      let response;
      if (resume) {
        const formData = new FormData();
        formData.append("file", resume);

        response = await fetch(`${backendURL}/upload-resume`, {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch(`${backendURL}/recommend-career`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ skills }),
        });
      }

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.error || "Failed to get recommendations");
      }

      const data = await response.json();
      setRecommendations(data.recommendations);
    } catch (err) {
      setError(err.message);
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-blue-50 p-6 rounded-2xl shadow-lg">
        <h1 className="text-3xl font-bold text-blue-900 mb-6 text-center">
          AI Career Advisor
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-blue-900 font-semibold mb-1">
              Enter your skills (comma-separated):
            </label>
            <input
              type="text"
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
              placeholder="Python, SQL, React..."
              className="w-full px-4 py-2 rounded-lg border border-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-blue-900 font-semibold mb-1">
              Or upload your resume (PDF):
            </label>
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              className="w-full text-blue-900"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200 font-semibold"
          >
            {loading ? "Analyzing..." : "Get Recommendations"}
          </button>
        </form>

        {error && (
          <p className="mt-4 text-red-600 font-semibold text-center">{error}</p>
        )}

        {recommendations.length > 0 && (
          <div className="mt-6 space-y-4">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="p-4 bg-white rounded-xl shadow border border-blue-200"
              >
                <h2 className="text-xl font-bold text-blue-800">{rec.role}</h2>
                <p>
                  <span className="font-semibold">Similarity:</span>{" "}
                  {rec.similarity}
                </p>
                <p>
                  <span className="font-semibold">Missing Skills:</span>{" "}
                  {rec.missing_skills.length > 0
                    ? rec.missing_skills.join(", ")
                    : "None"}
                </p>
                <p className="mt-2 text-gray-700 whitespace-pre-line">
                  <span className="font-semibold">AI Advice:</span>{" "}
                  {rec.ai_advice}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
