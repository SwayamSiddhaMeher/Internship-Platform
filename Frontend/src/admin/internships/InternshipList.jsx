import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

function InternshipList({
  onAdd,
  onEdit,
  onView,
  onBack
}) {
  const [internships, setInternships] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const token =
    localStorage.getItem("access_token");

  const loadInternships = async () => {
    try {
      setLoading(true);

      const response = await axios.get(
        `${API_URL}/admin/internships`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setInternships(response.data);

    } catch (error) {
      console.error(
        "ADMIN INTERNSHIP ERROR:",
        error
      );

      setMessage(
        error.response?.data?.detail ||
        "Unable to load internships"
      );

    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInternships();
  }, []);

  const deleteInternship = async (id) => {
    const confirmDelete =
      window.confirm(
        "Are you sure you want to delete this internship?"
      );

    if (!confirmDelete) {
      return;
    }

    try {
      await axios.delete(
        `${API_URL}/admin/internships/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setMessage(
        "Internship deleted successfully"
      );

      loadInternships();

    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
        "Unable to delete internship"
      );
    }
  };

  const changeStatus = async (
    id,
    status
  ) => {
    try {
      await axios.patch(
        `${API_URL}/admin/internships/${id}/status`,
        null,
        {
          params: {
            status: status
          },
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      setMessage(
        `Internship marked as ${status}`
      );

      loadInternships();

    } catch (error) {
      setMessage(
        error.response?.data?.detail ||
        "Unable to update status"
      );
    }
  };

  return (
    <div>

      <h2>Internship Management</h2>

      {message && (
        <div className="message">
          {message}
        </div>
      )}

      <button onClick={onAdd}>
        + Add Internship
      </button>

      <button
        className="secondary"
        onClick={onBack}
      >
        Back to Admin Dashboard
      </button>

      {loading ? (
        <p>Loading internships...</p>
      ) : internships.length === 0 ? (
        <div className="section">
          <p>
            No internships have been added yet.
          </p>

          <p>
            Click <strong>Add Internship</strong>{" "}
            to create the first internship.
          </p>
        </div>
      ) : (
        <div className="internship-list">

          {internships.map((internship) => (

            <div
              className="internship-card"
              key={internship.id}
            >

              <h3>
                {internship.title}
              </h3>

              <p>
                <strong>
                  Organization:
                </strong>{" "}
                {internship.organization}
              </p>

              <p>
                <strong>Domain:</strong>{" "}
                {internship.domain}
              </p>

              <p>
                <strong>Location:</strong>{" "}
                {internship.location || "N/A"}
              </p>

              <p>
                <strong>Work Mode:</strong>{" "}
                {internship.work_mode || "N/A"}
              </p>

              <p>
                <strong>Status:</strong>{" "}
                {internship.status}
              </p>

              <div>

                <button
                  onClick={() =>
                    onView(internship.id)
                  }
                >
                  View
                </button>

                <button
                  onClick={() =>
                    onEdit(internship.id)
                  }
                >
                  Edit
                </button>

                {internship.status ===
                  "Active" && (
                  <button
                    onClick={() =>
                      changeStatus(
                        internship.id,
                        "Closed"
                      )
                    }
                  >
                    Close
                  </button>
                )}

                {internship.status ===
                  "Closed" && (
                  <button
                    onClick={() =>
                      changeStatus(
                        internship.id,
                        "Active"
                      )
                    }
                  >
                    Reopen
                  </button>
                )}

                <button
                  className="secondary"
                  onClick={() =>
                    deleteInternship(
                      internship.id
                    )
                  }
                >
                  Delete
                </button>

              </div>

            </div>

          ))}

        </div>
      )}

    </div>
  );
}

export default InternshipList;