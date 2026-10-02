import { useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

function AddInternship({ onBack, onSuccess }) {

  const [formData, setFormData] = useState({
    title: "",
    organization: "",
    description: "",
    domain: "",
    location: "",
    work_mode: "",
    duration: "",
    stipend: "",
    vacancies: "",
    required_degree: "",
    required_branch: "",
    minimum_cgpa: "",
    maximum_backlogs: "",
    graduation_year: "",
    application_start_date: "",
    application_deadline: "",
    application_url: "",
    source_type: "",
    source_name: "",
    source_url: "",
    status: "Draft"
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

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

      const token =
        localStorage.getItem("access_token");

      const data = {
        ...formData,

        vacancies:
          formData.vacancies
            ? Number(formData.vacancies)
            : null,

        minimum_cgpa:
          Number(formData.minimum_cgpa),

        maximum_backlogs:
          formData.maximum_backlogs
            ? Number(formData.maximum_backlogs)
            : null,

        graduation_year:
          formData.graduation_year
            ? Number(formData.graduation_year)
            : null
      };

      const response = await axios.post(
        `${API_URL}/admin/internships`,
        data,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log(
        "INTERNSHIP CREATED:",
        response.data
      );

      setMessage(
        "Internship added successfully!"
      );

      if (onSuccess) {
        setTimeout(() => {
          onSuccess();
        }, 1000);
      }

    } catch (error) {

      console.error(
        "ADD INTERNSHIP ERROR:",
        error
      );

      const detail =
        error.response?.data?.detail;

      if (Array.isArray(detail)) {

        setMessage(
          detail
            .map((item) => item.msg)
            .join(", ")
        );

      } else {

        setMessage(
          detail ||
          "Unable to add internship"
        );
      }

    } finally {
      setLoading(false);
    }
  };

  return (
    <div>

      <h2>Add Internship</h2>

      {message && (
        <div className="message">
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit}>

        {/* =========================
            BASIC INFORMATION
        ========================== */}

        <div className="section">

          <h3>Basic Information</h3>

          <input
            type="text"
            name="title"
            placeholder="Internship Title"
            value={formData.title}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="organization"
            placeholder="Organization"
            value={formData.organization}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="domain"
            placeholder="Domain (e.g. Software Development)"
            value={formData.domain}
            onChange={handleChange}
            required
          />

          <textarea
            name="description"
            placeholder="Internship Description"
            value={formData.description}
            onChange={handleChange}
            rows="5"
          />

        </div>

        {/* =========================
            LOCATION
        ========================== */}

        <div className="section">

          <h3>Location</h3>

          <input
            type="text"
            name="location"
            placeholder="Location"
            value={formData.location}
            onChange={handleChange}
          />

          <select
            name="work_mode"
            value={formData.work_mode}
            onChange={handleChange}
          >
            <option value="">
              Select Work Mode
            </option>

            <option value="On-site">
              On-site
            </option>

            <option value="Remote">
              Remote
            </option>

            <option value="Hybrid">
              Hybrid
            </option>
          </select>

        </div>

        {/* =========================
            INTERNSHIP DETAILS
        ========================== */}

        <div className="section">

          <h3>Internship Details</h3>

          <input
            type="text"
            name="duration"
            placeholder="Duration (e.g. 6 Months)"
            value={formData.duration}
            onChange={handleChange}
          />

          <input
            type="text"
            name="stipend"
            placeholder="Stipend (e.g. ₹10,000/month)"
            value={formData.stipend}
            onChange={handleChange}
          />

          <input
            type="number"
            name="vacancies"
            placeholder="Number of Vacancies"
            value={formData.vacancies}
            onChange={handleChange}
            min="1"
          />

        </div>

        {/* =========================
            ELIGIBILITY
        ========================== */}

        <div className="section">

          <h3>Eligibility</h3>

          <input
            type="text"
            name="required_degree"
            placeholder="Required Degree (e.g. B.Tech)"
            value={formData.required_degree}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="required_branch"
            placeholder="Required Branch (e.g. CSE)"
            value={formData.required_branch}
            onChange={handleChange}
            required
          />

          <input
            type="number"
            name="minimum_cgpa"
            placeholder="Minimum CGPA"
            value={formData.minimum_cgpa}
            onChange={handleChange}
            min="0"
            max="10"
            step="0.01"
            required
          />

          <input
            type="number"
            name="maximum_backlogs"
            placeholder="Maximum Backlogs"
            value={formData.maximum_backlogs}
            onChange={handleChange}
            min="0"
          />

          <input
            type="number"
            name="graduation_year"
            placeholder="Graduation Year"
            value={formData.graduation_year}
            onChange={handleChange}
          />

        </div>

        {/* =========================
            APPLICATION
        ========================== */}

        <div className="section">

          <h3>Application Information</h3>

          <label>
            Application Start Date
          </label>

          <input
            type="date"
            name="application_start_date"
            value={formData.application_start_date}
            onChange={handleChange}
          />

          <label>
            Application Deadline
          </label>

          <input
            type="date"
            name="application_deadline"
            value={formData.application_deadline}
            onChange={handleChange}
          />

          <input
            type="url"
            name="application_url"
            placeholder="Application URL"
            value={formData.application_url}
            onChange={handleChange}
          />

        </div>

        {/* =========================
            SOURCE
        ========================== */}

        <div className="section">

          <h3>Source Information</h3>

          <select
            name="source_type"
            value={formData.source_type}
            onChange={handleChange}
          >
            <option value="">
              Select Source Type
            </option>

            <option value="PM_INTERNSHIP">
              PM Internship Scheme
            </option>

            <option value="COMPANY">
              Company
            </option>

            <option value="OTHER_VERIFIED">
              Other Verified Source
            </option>
          </select>

          <input
            type="text"
            name="source_name"
            placeholder="Source Name"
            value={formData.source_name}
            onChange={handleChange}
          />

          <input
            type="url"
            name="source_url"
            placeholder="Source URL"
            value={formData.source_url}
            onChange={handleChange}
          />

        </div>

        {/* =========================
            STATUS
        ========================== */}

        <div className="section">

          <h3>Status</h3>

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option value="Draft">
              Draft
            </option>

            <option value="Active">
              Active
            </option>

            <option value="Closed">
              Closed
            </option>

            <option value="Archived">
              Archived
            </option>
          </select>

        </div>

        {/* =========================
            BUTTONS
        ========================== */}

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Saving..."
            : "Save Internship"}
        </button>

        <button
          type="button"
          className="secondary"
          onClick={onBack}
        >
          Back
        </button>

      </form>

    </div>
  );
}

export default AddInternship;