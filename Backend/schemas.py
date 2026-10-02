from pydantic import BaseModel, EmailStr, Field


# ==========================================
# US-01: CANDIDATE REGISTRATION
# ==========================================

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    password: str


# ==========================================
# US-02: CANDIDATE LOGIN
# ==========================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==========================================
# US-03: CANDIDATE PROFILE
# ==========================================

class CandidateProfileRequest(BaseModel):
    user_id: int
    degree: str
    branch: str
    cgpa: float = Field(ge=0, le=10)


# ==========================================
# US-06: INTERNSHIP
# ==========================================

class InternshipRequest(BaseModel):
    title: str
    organization: str
    description: str | None = None

    domain: str
    location: str | None = None
    work_mode: str | None = None
    duration: str | None = None
    stipend: str | None = None
    vacancies: int | None = None

    required_degree: str
    required_branch: str
    minimum_cgpa: float = Field(ge=0, le=10)
    maximum_backlogs: int | None = None
    graduation_year: int | None = None

    application_start_date: str | None = None
    application_deadline: str | None = None
    application_url: str | None = None

    source_type: str | None = None
    source_name: str | None = None
    source_url: str | None = None

    status: str = "Active"


# ==========================================
# US-08: ELIGIBILITY RULES
# ==========================================

class EligibilityRuleRequest(BaseModel):
    internship_id: int
    rule_name: str
    rule_value: str


# ==========================================
# US-17: CANDIDATE PREFERENCES
# ==========================================

class CandidatePreferencesRequest(BaseModel):
    user_id: int

    skills: str | None = None
    career_interests: str | None = None

    preferred_domain: str | None = None
    preferred_location: str | None = None
    preferred_work_mode: str | None = None

# ==========================================
# US-18: AI GENERATED MCQ
# ==========================================

class GenerateMCQRequest(BaseModel):

    skill: str
    number_of_questions: int = Field(
        default=5,
        ge=1,
        le=20
    )

    difficulty: str = "Mixed"

class MCQResponse(BaseModel):

    id: int
    skill: str
    question: str

    option_a: str
    option_b: str
    option_c: str
    option_d: str

    difficulty: str