import { useState } from "react";
import axios from "axios";

import "./App.css";

import AdminDashboard from "./admin/AdminDashboard";
import CandidatePreferences from "./candidate/CandidatePreferences";

const API_URL = "http://127.0.0.1:8000";

function App() {

  const [page, setPage] = useState("login");

  // ==============================
  // LOGIN FORM
  // ==============================

  const [loginForm, setLoginForm] = useState({
    email: "",
    password: ""
  });

  // ==============================
  // REGISTER FORM
  // ==============================

  const [registerForm, setRegisterForm] = useState({
    name: "",
    email: "",
    mobile: "",
    password: ""
  });

  // ==============================
  // STATE
  // ==============================

  const [dashboard, setDashboard] = useState(null);

  const [internships, setInternships] = useState([]);

  const [eligibility, setEligibility] = useState({});

  const [message, setMessage] = useState("");

  const [loading, setLoading] = useState(false);

  // ==============================
  // LOGIN INPUT
  // ==============================

  const handleLoginChange = (e) => {
    setLoginForm({
      ...loginForm,
      [e.target.name]: e.target.value
    });
  };

  // ==============================
  // REGISTER INPUT
  // ==============================

  const handleRegisterChange = (e) => {
    setRegisterForm({
      ...registerForm,
      [e.target.name]: e.target.value
    });
  };

  // ==============================
  // REGISTER
  // ==============================

  const handleRegister = async (e) => {

    e.preventDefault();

    setLoading(true);
    setMessage("");

    try {

      const response = await axios.post(
        `${API_URL}/register`,
        registerForm
      );

      setMessage(response.data.message);

      setRegisterForm({
        name: "",
        email: "",
        mobile: "",
        password: ""
      });

      setPage("login");

    } catch (error) {

      console.error("REGISTER ERROR:", error);

      const detail = error.response?.data?.detail;

      if (Array.isArray(detail)) {

        setMessage(
          detail.map((item) => item.msg).join(", ")
        );

      } else {

        setMessage(
          detail ||
          error.message ||
          "Registration failed"
        );

      }

    } finally {

      setLoading(false);

    }
  };

  // ==============================
  // LOGIN
  // ==============================

  const handleLogin = async (e) => {

    e.preventDefault();

    setLoading(true);
    setMessage("");

    try {

      const response = await axios.post(
        `${API_URL}/login`,
        loginForm
      );

      console.log(
        "LOGIN RESPONSE:",
        response.data
      );

      // ==============================
      // STORE LOGIN DATA
      // ==============================

      localStorage.setItem(
        "access_token",
        response.data.access_token
      );

      localStorage.setItem(
        "user_id",
        response.data.user_id
      );

      localStorage.setItem(
        "name",
        response.data.name
      );

      localStorage.setItem(
        "role",
        response.data.role
      );

      // ==============================
      // ROLE BASED REDIRECT
      // ==============================

      if (response.data.role === "admin") {

        setPage("admin");

      } else {

        setPage("dashboard");

        await loadDashboard(
          response.data.access_token
        );

      }

    } catch (error) {

      console.error("LOGIN ERROR:", error);

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
          error.message ||
          "Login failed"
        );

      }

    } finally {

      setLoading(false);

    }
  };

  // ==============================
  // LOAD CANDIDATE DASHBOARD
  // ==============================

  const loadDashboard = async (token) => {

    try {

      const response = await axios.get(
        `${API_URL}/dashboard`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      console.log(
        "DASHBOARD RESPONSE:",
        response.data
      );

      setDashboard(response.data);

    } catch (error) {

      console.error(
        "DASHBOARD ERROR:",
        error
      );

      const detail =
        error.response?.data?.detail;

      setMessage(
        detail ||
        "Unable to load dashboard"
      );

    }
  };

  // ==============================
  // LOAD INTERNSHIPS
  // ==============================

  const loadInternships = async () => {

    setLoading(true);
    setMessage("");

    try {

      const response = await axios.get(
        `${API_URL}/internships`
      );

      console.log(
        "INTERNSHIPS:",
        response.data
      );

      setInternships(response.data);

      setPage("internships");

    } catch (error) {

      console.error(
        "INTERNSHIP ERROR:",
        error
      );

      const detail =
        error.response?.data?.detail;

      setMessage(
        detail ||
        "Unable to load internships"
      );

    } finally {

      setLoading(false);

    }
  };

  // ==============================
  // CHECK ELIGIBILITY
  // ==============================

  const checkEligibility = async (
    internshipId
  ) => {

    const userId =
      localStorage.getItem("user_id");

    if (!userId) {

      setMessage(
        "Please login again."
      );

      setPage("login");

      return;
    }

    try {

      setMessage(
        "Checking eligibility..."
      );

      const response = await axios.get(
        `${API_URL}/eligibility/${userId}/${internshipId}`
      );

      console.log(
        "ELIGIBILITY RESPONSE:",
        response.data
      );

      setEligibility((previous) => ({
        ...previous,
        [internshipId]: response.data
      }));

      setMessage("");

    } catch (error) {

      console.error(
        "ELIGIBILITY ERROR:",
        error
      );

      const detail =
        error.response?.data?.detail;

      setMessage(
        detail ||
        "Unable to check eligibility"
      );
    }
  };

  // ==============================
  // LOGOUT
  // ==============================

  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user_id"
    );

    localStorage.removeItem(
      "name"
    );

    localStorage.removeItem(
      "role"
    );

    setDashboard(null);

    setInternships([]);

    setEligibility({});

    setLoginForm({
      email: "",
      password: ""
    });

    setMessage("");

    setPage("login");
  };

  // ==============================
  // LOGIN PAGE
  // ==============================

  const loginPage = (
    <>
      <h2>Login</h2>

      <form onSubmit={handleLogin}>

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={loginForm.email}
          onChange={handleLoginChange}
          required
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={loginForm.password}
          onChange={handleLoginChange}
          required
        />

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Logging in..."
            : "Login"}
        </button>

      </form>

      <p className="switch-text">
        Don't have an account?
      </p>

      <button
        className="secondary"
        onClick={() => {
          setPage("register");
          setMessage("");
        }}
      >
        Create Account
      </button>
    </>
  );

  // ==============================
  // REGISTER PAGE
  // ==============================

  const registerPage = (
    <>
      <h2>Candidate Registration</h2>

      <form onSubmit={handleRegister}>

        <input
          type="text"
          name="name"
          placeholder="Full Name"
          value={registerForm.name}
          onChange={handleRegisterChange}
          required
        />

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={registerForm.email}
          onChange={handleRegisterChange}
          required
        />

        <input
          type="tel"
          name="mobile"
          placeholder="Mobile Number"
          value={registerForm.mobile}
          onChange={handleRegisterChange}
          required
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={registerForm.password}
          onChange={handleRegisterChange}
          required
        />

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Registering..."
            : "Register"}
        </button>

      </form>

      <p className="switch-text">
        Already have an account?
      </p>

      <button
        className="secondary"
        onClick={() => {
          setPage("login");
          setMessage("");
        }}
      >
        Back to Login
      </button>
    </>
  );

  // ==============================
  // CANDIDATE DASHBOARD
  // ==============================

  const dashboardPage = (
    <>
      <h2>Candidate Dashboard</h2>

      {dashboard ? (
        <>

          {/* Candidate Information */}

          <div className="section">

            <h3>Candidate Information</h3>

            <p>
              <strong>Name:</strong>{" "}
              {dashboard.user?.name}
            </p>

            <p>
              <strong>Email:</strong>{" "}
              {dashboard.user?.email}
            </p>

            <p>
              <strong>Mobile:</strong>{" "}
              {dashboard.user?.mobile}
            </p>

          </div>


          {/* Academic Profile */}

          <div className="section">

            <h3>Academic Profile</h3>

            {dashboard.profile ? (

              <>
                <p>
                  <strong>Degree:</strong>{" "}
                  {dashboard.profile.degree}
                </p>

                <p>
                  <strong>Branch:</strong>{" "}
                  {dashboard.profile.branch}
                </p>

                <p>
                  <strong>CGPA:</strong>{" "}
                  {dashboard.profile.cgpa}
                </p>
              </>

            ) : (

              <p>
                Academic profile not available.
              </p>

            )}

          </div>


          {/* View Internships */}

          <button
            onClick={loadInternships}
          >
            {loading
              ? "Loading..."
              : "View Available Internships"}
          </button>


          {/* US-17 */}

          <button
            onClick={() => {
              setMessage("");
              setPage("preferences");
            }}
          >
            Skills & Career Interests
          </button>


          {/* Logout */}

          <button
            className="secondary"
            onClick={logout}
          >
            Logout
          </button>

        </>

      ) : (

        <p className="loading">
          Loading dashboard...
        </p>

      )}

    </>
  );

  // ==============================
  // INTERNSHIPS PAGE
  // ==============================

  const internshipsPage = (
    <>
      <h2>Available Internships</h2>

      {internships.length === 0 ? (

        <p className="empty">
          No internships available.
        </p>

      ) : (

        <div className="internship-list">

          {internships.map((internship) => {

            const result =
              eligibility[internship.id];

            return (

              <div
                className="internship-card"
                key={internship.id}
              >

                <h3>
                  {internship.title}
                </h3>

                <p>
                  <strong>Degree:</strong>{" "}
                  {internship.required_degree}
                </p>

                <p>
                  <strong>Branch:</strong>{" "}
                  {internship.required_branch}
                </p>

                <p>
                  <strong>
                    Minimum CGPA:
                  </strong>{" "}
                  {internship.minimum_cgpa}
                </p>

                <button
                  onClick={() =>
                    checkEligibility(
                      internship.id
                    )
                  }
                >
                  Check Eligibility
                </button>


                {result && (

                  <div
                    className={
                      result.eligibility_status ===
                      "Eligible"
                        ? "eligibility-result eligible"
                        : "eligibility-result not-eligible"
                    }
                  >

                    <h4>
                      Eligibility Result
                    </h4>

                    <p>
                      <strong>Status:</strong>{" "}
                      {result.eligibility_status}
                    </p>

                    {result.reasons &&
                      result.reasons.length > 0 && (

                        <div>

                          <strong>
                            Reasons:
                          </strong>

                          <ul>

                            {result.reasons.map(
                              (reason, index) => (

                                <li key={index}>
                                  {reason}
                                </li>

                              )
                            )}

                          </ul>

                        </div>

                      )}

                  </div>

                )}

              </div>

            );
          })}

        </div>

      )}


      <button
        className="secondary"
        onClick={() => {
          setPage("dashboard");
          setMessage("");
        }}
      >
        Back to Dashboard
      </button>


      <button
        className="secondary"
        onClick={logout}
      >
        Logout
      </button>

    </>
  );

  // ==============================
  // MAIN UI
  // ==============================

  return (

    <div className="container">

      <div className="card">

        <h1>
          Internship Platform
        </h1>


        {page === "login" &&
          loginPage}


        {page === "register" &&
          registerPage}


        {page === "dashboard" &&
          dashboardPage}


        {page === "internships" &&
          internshipsPage}


        {/* ==============================
            US-17: CANDIDATE PREFERENCES
        ============================== */}

        {page === "preferences" && (

          <CandidatePreferences
            onBack={() => {
              setMessage("");
              setPage("dashboard");
            }}
          />

        )}


        {/* ==============================
            ADMIN
        ============================== */}

        {page === "admin" && (

          <AdminDashboard
            logout={logout}
          />

        )}


        {/* ==============================
            GLOBAL MESSAGE
        ============================== */}

        {message && (

          <div className="message">
            {message}
          </div>

        )}

      </div>

    </div>

  );
}

export default App;