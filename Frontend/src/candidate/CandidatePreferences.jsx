import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

function CandidatePreferences({ onBack }) {
  const userId = localStorage.getItem("user_id");
  const token = localStorage.getItem("access_token");

  const [formData, setFormData] = useState({
    skills: "",
    career_interests: "",
    preferred_domain: "",
    preferred_location: "",
    preferred_work_mode: ""
  });

  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [existingPreferences, setExistingPreferences] = useState(false);

  // Load existing preferences
  useEffect(() => {
    const loadPreferences = async () => {
      try {
        const response = await axios.get(
          `${API_URL}/candidate-preferences/${userId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        setFormData({
          skills: response.data.skills || "",
          career_interests: response.data.career_interests || "",
          preferred_domain: response.data.preferred_domain || "",
          preferred_location: response.data.preferred_location || "",
          preferred_work_mode: response.data.preferred_work_mode || ""
        });

        setExistingPreferences(true);

      } catch (error) {
        // 404 means preferences have not been created yet
        if (error.response?.status !== 404) {
          console.error("Error loading preferences:", error);
        }
      }
    };

    if (userId && token) {
      loadPreferences();
    }
  }, [userId, token]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setMessage("");

    try {
      const data = {
        user_id: Number(userId),
        ...formData
      };

      let response;

      if (existingPreferences) {
        // Update existing preferences
        response = await axios.put(
          `${API_URL}/candidate-preferences/${userId}`,
          data,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );
      } else {
        // Create new preferences
        response = await axios.post(
          `${API_URL}/candidate-preferences`,
          data,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        setExistingPreferences(true);
      }

      setMessage(
        response.data.message ||
        "Preferences saved successfully!"
      );

    } catch (error) {
      console.error("Preferences error:", error);

      const detail = error.response?.data?.detail;

      setMessage(
        detail || "Unable to save preferences."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div>

      <h2>Skills & Career Interests</h2>

      {message && (
        <div className="message">
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit}>

        {/* Skills */}
        <div className="section">

          <h3>Your Skills</h3>

          <input
            type="text"
            name="skills"
            placeholder="Example: Python, SQL, React, Java"
            value={formData.skills}
            onChange={handleChange}
            required
          />

          <p>
            Enter your skills separated by commas.
          </p>

        </div>


        {/* Career Interests */}
        <div className="section">

          <h3>Career Interests</h3>

          <input
            type="text"
            name="career_interests"
            placeholder="Example: Software Development, AI/ML"
            value={formData.career_interests}
            onChange={handleChange}
            required
          />

        </div>


        {/* Preferred Domain */}
        <div className="section">

          <h3>Preferred Domain</h3>

          <select
            name="preferred_domain"
            value={formData.preferred_domain}
            onChange={handleChange}
          >

            <option value="">
              Select Domain
            </option>

            <option value="Software Development">
              Software Development
            </option>

            <option value="AI/ML">
              AI / ML
            </option>

            <option value="Data Science">
              Data Science
            </option>

            <option value="Web Development">
              Web Development
            </option>

            <option value="Cyber Security">
              Cyber Security
            </option>

            <option value="Cloud Computing">
              Cloud Computing
            </option>

            <option value="Other">
              Other
            </option>

          </select>

        </div>


        {/* Preferred Location */}
        <div className="section">

          <h3>Preferred Location</h3>

          <input
            type="text"
            name="preferred_location"
            placeholder="Example: Bhubaneswar"
            value={formData.preferred_location}
            onChange={handleChange}
          />

        </div>


        {/* Preferred Work Mode */}
        <div className="section">

          <h3>Preferred Work Mode</h3>

          <select
            name="preferred_work_mode"
            value={formData.preferred_work_mode}
            onChange={handleChange}
          >

            <option value="">
              Select Work Mode
            </option>

            <option value="Remote">
              Remote
            </option>

            <option value="On-site">
              On-site
            </option>

            <option value="Hybrid">
              Hybrid
            </option>

          </select>

        </div>


        {/* Buttons */}
        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Saving..."
            : existingPreferences
              ? "Update Preferences"
              : "Save Preferences"
          }
        </button>

        <button
          type="button"
          className="secondary"
          onClick={onBack}
        >
          Back to Dashboard
        </button>

      </form>

    </div>
  );
}

export default CandidatePreferences;