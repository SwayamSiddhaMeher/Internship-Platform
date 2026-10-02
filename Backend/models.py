from sqlalchemy import Column, Integer, String, Float
from database import Base


# ==========================================
# USER
# ==========================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    mobile = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        default="candidate",
        nullable=False
    )

    status = Column(
        String,
        default="active",
        nullable=False
    )


# ==========================================
# US-03: CANDIDATE PROFILE
# ==========================================

class CandidateProfile(Base):

    __tablename__ = "candidate_profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        unique=True,
        nullable=False
    )

    degree = Column(
        String,
        nullable=False
    )

    branch = Column(
        String,
        nullable=False
    )

    cgpa = Column(
        Float,
        nullable=False
    )


# ==========================================
# US-06: INTERNSHIP
# ==========================================

class Internship(Base):

    __tablename__ = "internships"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Basic Information
    title = Column(
        String,
        nullable=False
    )

    organization = Column(
        String,
        nullable=False
    )

    description = Column(
        String,
        nullable=True
    )

    domain = Column(
        String,
        nullable=False
    )

    # Internship Details
    location = Column(
        String,
        nullable=True
    )

    work_mode = Column(
        String,
        nullable=True
    )

    duration = Column(
        String,
        nullable=True
    )

    stipend = Column(
        String,
        nullable=True
    )

    vacancies = Column(
        Integer,
        nullable=True
    )

    # Eligibility
    required_degree = Column(
        String,
        nullable=False
    )

    required_branch = Column(
        String,
        nullable=False
    )

    minimum_cgpa = Column(
        Float,
        nullable=False
    )

    maximum_backlogs = Column(
        Integer,
        nullable=True
    )

    graduation_year = Column(
        Integer,
        nullable=True
    )

    # Application
    application_start_date = Column(
        String,
        nullable=True
    )

    application_deadline = Column(
        String,
        nullable=True
    )

    application_url = Column(
        String,
        nullable=True
    )

    # Source
    source_type = Column(
        String,
        nullable=True
    )

    source_name = Column(
        String,
        nullable=True
    )

    source_url = Column(
        String,
        nullable=True
    )

    # Status
    status = Column(
        String,
        default="Active"
    )


# ==========================================
# US-08: ELIGIBILITY RULES
# ==========================================

class EligibilityRule(Base):

    __tablename__ = "eligibility_rules"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    internship_id = Column(
        Integer,
        nullable=False
    )

    rule_name = Column(
        String,
        nullable=False
    )

    rule_value = Column(
        String,
        nullable=False
    )

class CandidatePreferences(Base):
    __tablename__ = "candidate_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)

    skills = Column(String, nullable=True)
    career_interests = Column(String, nullable=True)

    preferred_domain = Column(String, nullable=True)
    preferred_location = Column(String, nullable=True)
    preferred_work_mode = Column(String, nullable=True)

# ==========================================
# US-18: AI GENERATED MCQ
# ==========================================

class SkillMCQ(Base):

    __tablename__ = "skill_mcqs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    skill = Column(
        String,
        nullable=False
    )

    question = Column(
        String,
        nullable=False
    )

    option_a = Column(
        String,
        nullable=False
    )

    option_b = Column(
        String,
        nullable=False
    )

    option_c = Column(
        String,
        nullable=False
    )

    option_d = Column(
        String,
        nullable=False
    )

    correct_answer = Column(
        String,
        nullable=False
    )

    difficulty = Column(
        String,
        nullable=False
    )

    