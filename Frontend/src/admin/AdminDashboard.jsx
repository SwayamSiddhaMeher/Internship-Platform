import { useState } from "react";
import InternshipList from "./internships/InternshipList";
import AddInternship from "./internships/AddInternship";

function AdminDashboard({ logout }) {

  const [page, setPage] =
    useState("dashboard");

  // ==============================
  // INTERNSHIP LIST
  // ==============================

  if (page === "internships") {
    return (
      <InternshipList
        onAdd={() =>
          setPage("add-internship")
        }

        onEdit={(id) => {
          console.log(
            "Edit internship:",
            id
          );
        }}

        onView={(id) => {
          console.log(
            "View internship:",
            id
          );
        }}

        onBack={() =>
          setPage("dashboard")
        }
      />
    );
  }

  // ==============================
  // ADD INTERNSHIP
  // ==============================

  if (page === "add-internship") {
    return (
      <AddInternship
        onBack={() =>
          setPage("internships")
        }

        onSuccess={() =>
          setPage("internships")
        }
      />
    );
  }

  // ==============================
  // ADMIN DASHBOARD
  // ==============================

  return (
    <div>

      <h2>Admin Dashboard</h2>

      <div className="section">

        <h3>
          Welcome, Admin
        </h3>

        <p>
          You are logged in as an
          administrator.
        </p>

      </div>

      <div className="section">

        <h3>
          Internship Management
        </h3>

        <button
          onClick={() =>
            setPage("add-internship")
          }
        >
          Add Internship
        </button>

        <button
          onClick={() =>
            setPage("internships")
          }
        >
          View Internships
        </button>

      </div>

      <button
        className="secondary"
        onClick={logout}
      >
        Logout
      </button>

    </div>
  );
}

export default AdminDashboard;