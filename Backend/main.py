from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from jose import jwt
import bcrypt


from database import Base, get_db, engine

from models import (
    User,
    CandidateProfile,
    Internship,
    EligibilityRule,
    CandidatePreferences,
    SkillMCQ
)

from schemas import (
    RegisterRequest,
    LoginRequest,
    CandidateProfileRequest,
    InternshipRequest,
    EligibilityRuleRequest,
    CandidatePreferencesRequest,
    MCQResponse
)


# ==================================================
# APP
# ==================================================

app = FastAPI(
    title="Internship Recommendation Platform",
    description="Backend API for Internship Platform",
    version="1.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ==================================================
# DATABASE
# ==================================================

Base.metadata.create_all(bind=engine)


# ==================================================
# JWT SETTINGS
# ==================================================

SECRET_KEY = "internship-platform-secret-key"

ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/token"
)


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message": "Internship Platform API Running"
    }


# ==================================================
# US-01: CANDIDATE REGISTRATION
# ==================================================

@app.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    # Check duplicate email
    existing_email = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing_email:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    # Check duplicate mobile
    existing_mobile = db.query(User).filter(
        User.mobile == data.mobile
    ).first()

    if existing_mobile:

        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )


    # Hash password
    hashed_password = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


    # Create candidate user
    user = User(
        name=data.name,
        email=data.email,
        mobile=data.mobile,
        password=hashed_password,

        # IMPORTANT:
        # Normal registration is always candidate
        role="candidate",
        status="active"
    )


    db.add(user)

    db.commit()

    db.refresh(user)


    return {
        "message": "Registration successful",
        "user_id": user.id
    }


# ==================================================
# US-02: LOGIN
# ==================================================

@app.post("/login")
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):

    # Find user
    user = db.query(User).filter(
        User.email == data.email
    ).first()


    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    # Verify password
    password_match = bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password.encode("utf-8")
    )


    if not password_match:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    # Check account status
    if user.status != "active":

        raise HTTPException(
            status_code=403,
            detail=f"Account is {user.status}"
        )


    # JWT data
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }


    # Generate token
    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "name": user.name,
        "role": user.role
    }


# ==================================================
# OAUTH2 TOKEN ENDPOINT
# Used by Swagger Authorize button
# ==================================================

@app.post("/token")
def token(
    data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    # Swagger sends email as username
    user = db.query(User).filter(
        User.email == data.username
    ).first()


    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    # Verify password
    password_match = bcrypt.checkpw(
        data.password.encode("utf-8"),
        user.password.encode("utf-8")
    )


    if not password_match:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )


    # Check status
    if user.status != "active":

        raise HTTPException(
            status_code=403,
            detail=f"Account is {user.status}"
        )


    # JWT data
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    }


    # Generate token
    access_token = jwt.encode(
        token_data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ==================================================
# VERIFY JWT TOKEN
# ==================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )


        user_id = payload.get("user_id")


        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )


    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


    # Find user
    user = db.query(User).filter(
        User.id == user_id
    ).first()


    if user is None:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )


    # Check status
    if user.status != "active":

        raise HTTPException(
            status_code=403,
            detail=f"Account is {user.status}"
        )


    return user


# ==================================================
# ADMIN AUTHORIZATION
# ==================================================

def admin_required(
    current_user: User = Depends(get_current_user)
):

    # Check role
    if current_user.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )


    # Check status
    if current_user.status != "active":

        raise HTTPException(
            status_code=403,
            detail="Admin account is not active"
        )


    return current_user


# ==================================================
# US-03: CANDIDATE ACADEMIC PROFILE
# ==================================================

@app.post("/candidate-profile")
def create_candidate_profile(
    data: CandidateProfileRequest,
    db: Session = Depends(get_db)
):

    # Check candidate
    user = db.query(User).filter(
        User.id == data.user_id
    ).first()


    if not user:

        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )


    # Check duplicate profile
    existing = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == data.user_id
    ).first()


    if existing:

        raise HTTPException(
            status_code=400,
            detail="Candidate profile already exists"
        )


    # Create profile
    profile = CandidateProfile(
        user_id=data.user_id,
        degree=data.degree,
        branch=data.branch,
        cgpa=data.cgpa
    )


    db.add(profile)

    db.commit()

    db.refresh(profile)


    return {
        "message": "Candidate profile created",
        "profile_id": profile.id
    }


# ==================================================
# OLD INTERNSHIP API
# ==================================================
# Kept for compatibility with your existing project.
# New internship data should be added through
# /admin/internships
# ==================================================

@app.post("/internships")
def create_internship(
    data: InternshipRequest,
    db: Session = Depends(get_db)
):

    if data.minimum_cgpa < 0 or data.minimum_cgpa > 10:

        raise HTTPException(
            status_code=400,
            detail="Invalid CGPA requirement"
        )


    internship = Internship(

        title=data.title,

        organization=data.organization,

        description=data.description,

        domain=data.domain,

        location=data.location,

        work_mode=data.work_mode,

        duration=data.duration,

        stipend=data.stipend,

        vacancies=data.vacancies,

        required_degree=data.required_degree,

        required_branch=data.required_branch,

        minimum_cgpa=data.minimum_cgpa,

        maximum_backlogs=data.maximum_backlogs,

        graduation_year=data.graduation_year,

        application_start_date=data.application_start_date,

        application_deadline=data.application_deadline,

        application_url=data.application_url,

        source_type=data.source_type,

        source_name=data.source_name,

        source_url=data.source_url,

        status=data.status
    )


    db.add(internship)

    db.commit()

    db.refresh(internship)


    return {
        "message": "Internship created",
        "internship_id": internship.id
    }


# ==================================================
# ADMIN: CREATE INTERNSHIP
# ==================================================

@app.post("/admin/internships")
def admin_create_internship(

    data: InternshipRequest,

    db: Session = Depends(get_db),

    admin: User = Depends(admin_required)

):

    # Validate CGPA
    if data.minimum_cgpa < 0 or data.minimum_cgpa > 10:

        raise HTTPException(
            status_code=400,
            detail="Invalid CGPA requirement"
        )


    # Validate status
    allowed_status = [
        "Active",
        "Closed",
        "Archived",
        "Draft"
    ]

    if data.status not in allowed_status:

        raise HTTPException(
            status_code=400,
            detail="Invalid internship status"
        )


    # Create internship
    internship = Internship(

        title=data.title,

        organization=data.organization,

        description=data.description,

        domain=data.domain,

        location=data.location,

        work_mode=data.work_mode,

        duration=data.duration,

        stipend=data.stipend,

        vacancies=data.vacancies,

        required_degree=data.required_degree,

        required_branch=data.required_branch,

        minimum_cgpa=data.minimum_cgpa,

        maximum_backlogs=data.maximum_backlogs,

        graduation_year=data.graduation_year,

        application_start_date=data.application_start_date,

        application_deadline=data.application_deadline,

        application_url=data.application_url,

        source_type=data.source_type,

        source_name=data.source_name,

        source_url=data.source_url,

        status=data.status
    )


    db.add(internship)

    db.commit()

    db.refresh(internship)


    return {
        "message": "Internship added successfully",
        "internship_id": internship.id
    }


# ==================================================
# ADMIN: GET ALL INTERNSHIPS
# ==================================================

@app.get("/admin/internships")
def admin_get_internships(

    db: Session = Depends(get_db),

    admin: User = Depends(admin_required)

):

    internships = db.query(Internship).all()


    return internships


# ==================================================
# ADMIN: GET SINGLE INTERNSHIP
# ==================================================

@app.get("/admin/internships/{internship_id}")
def admin_get_internship(

    internship_id: int,

    db: Session = Depends(get_db),

    admin: User = Depends(admin_required)

):

    internship = db.query(Internship).filter(
        Internship.id == internship_id
    ).first()


    if not internship:

        raise HTTPException(
            status_code=404,
            detail="Internship not found"
        )


    return internship


# ==================================================
# ADMIN: UPDATE INTERNSHIP
# ==================================================

@app.put("/admin/internships/{internship_id}")
def admin_update_internship(

    internship_id: int,

    data: InternshipRequest,

    db: Session = Depends(get_db),

    admin: User = Depends(admin_required)

):

    internship = db.query(Internship).filter(
        Internship.id == internship_id
    ).first()


    if not internship:

        raise HTTPException(
            status_code=404,
            detail="Internship not found"
        )


    # Validate status
    allowed_status = [
        "Active",
        "Closed",
        "Archived",
        "Draft"
    ]

    if data.status not in allowed_status:

        raise HTTPException(
            status_code=400,
            detail="Invalid internship status"
        )


    # Update fields
    internship.title = data.title

    internship.organization = data.organization

    internship.description = data.description

    internship.domain = data.domain

    internship.location = data.location

    internship.work_mode = data.work_mode

    internship.duration = data.duration

    internship.stipend = data.stipend

    internship.vacancies = data.vacancies

    internship.required_degree = data.required_degree

    internship.required_branch = data.required_branch

    internship.minimum_cgpa = data.minimum_cgpa

    internship.maximum_backlogs = data.maximum_backlogs

    internship.graduation_year = data.graduation_year

    internship.application_start_date = data.application_start_date

    internship.application_deadline = data.application_deadline

    internship.application_url = data.application_url

    internship.source_type = data.source_type

    internship.source_name = data.source_name

    internship.source_url = data.source_url

    internship.status = data.status


    db.commit()

    db.refresh(internship)


    return {
        "message": "Internship updated successfully",
        "internship_id": internship.id
    }


# ==================================================
# ADMIN: DELETE INTERNSHIP
# ==================================================

@app.delete("/admin/internships/{internship_id}")
def admin_delete_internship(

    internship_id: int,

    db: Session = Depends(get_db),

    admin: User = Depends(admin_required)

):

    internship = db.query(Internship).filter(
        Internship.id == internship_id
    ).first()


    if not internship:

        raise HTTPException(
            status_code=404,
            detail="Internship not found"
        )


    db.delete(internship)

    db.commit()


    return {
        "message": "Internship deleted successfully"
    }


# ==================================================
# ADMIN: CHANGE INTERNSHIP STATUS
# ==================================================

@app.patch("/admin/internships/{internship_id}/status")
def admin_update_internship_status(

    internship_id: int,

    status: str,

    db: Session = Depends(get_db),

    admin: User = Depends(admin_required)

):

    allowed_status = [
        "Active",
        "Closed",
        "Archived",
        "Draft"
    ]


    if status not in allowed_status:

        raise HTTPException(
            status_code=400,
            detail="Invalid internship status"
        )


    internship = db.query(Internship).filter(
        Internship.id == internship_id
    ).first()


    if not internship:

        raise HTTPException(
            status_code=404,
            detail="Internship not found"
        )


    internship.status = status

    db.commit()

    db.refresh(internship)


    return {
        "message": "Internship status updated",
        "status": internship.status
    }


# ==================================================
# US-08: ELIGIBILITY RULES
# ==================================================

@app.post("/eligibility-rules")
def create_eligibility_rule(

    data: EligibilityRuleRequest,

    db: Session = Depends(get_db)

):

    # Check internship
    internship = db.query(Internship).filter(
        Internship.id == data.internship_id
    ).first()


    if not internship:

        raise HTTPException(
            status_code=404,
            detail="Internship not found"
        )


    # Allowed rule types
    allowed_rules = [
        "degree",
        "branch",
        "minimum_cgpa"
    ]


    if data.rule_name not in allowed_rules:

        raise HTTPException(
            status_code=400,
            detail="Invalid eligibility rule"
        )


    # Validate CGPA rule
    if data.rule_name == "minimum_cgpa":

        try:

            value = float(data.rule_value)

            if value < 0 or value > 10:

                raise ValueError

        except ValueError:

            raise HTTPException(
                status_code=400,
                detail="Invalid CGPA rule value"
            )


    # Create rule
    rule = EligibilityRule(

        internship_id=data.internship_id,

        rule_name=data.rule_name,

        rule_value=data.rule_value
    )


    db.add(rule)

    db.commit()

    db.refresh(rule)


    return {
        "message": "Eligibility rule created",
        "rule_id": rule.id
    }


# ==================================================
# US-09: CANDIDATE ELIGIBILITY CHECK
# ==================================================

@app.get("/eligibility/{user_id}/{internship_id}")
def check_eligibility(

    user_id: int,

    internship_id: int,

    db: Session = Depends(get_db)

):

    # Get candidate profile
    candidate = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == user_id
    ).first()


    if not candidate:

        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )


    # Get internship
    internship = db.query(Internship).filter(
        Internship.id == internship_id
    ).first()


    if not internship:

        raise HTTPException(
            status_code=404,
            detail="Internship not found"
        )


    # Get rules
    rules = db.query(EligibilityRule).filter(
        EligibilityRule.internship_id == internship_id
    ).all()


    if not rules:

        raise HTTPException(
            status_code=404,
            detail="No eligibility rules found for this internship"
        )


    reasons = []

    eligible = True


    # Check rules
    for rule in rules:

        # Degree
        if rule.rule_name == "degree":

            if candidate.degree.lower() != rule.rule_value.lower():

                eligible = False

                reasons.append(
                    "Degree requirement not satisfied"
                )


        # Branch
        elif rule.rule_name == "branch":

            if candidate.branch.lower() != rule.rule_value.lower():

                eligible = False

                reasons.append(
                    "Branch requirement not satisfied"
                )


        # Minimum CGPA
        elif rule.rule_name == "minimum_cgpa":

            try:

                required_cgpa = float(
                    rule.rule_value
                )


                if candidate.cgpa < required_cgpa:

                    eligible = False

                    reasons.append(
                        "Minimum CGPA requirement not satisfied"
                    )


            except ValueError:

                eligible = False

                reasons.append(
                    "Invalid CGPA eligibility rule"
                )


    # Status
    if eligible:

        status = "Eligible"

    else:

        status = "Not Eligible"


    return {

        "user_id": user_id,

        "internship_id": internship_id,

        "eligibility_status": status,

        "reasons": reasons
    }


# ==================================================
# US-15: CANDIDATE DASHBOARD
# ==================================================

@app.get("/dashboard")
def dashboard(

    user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    # Get candidate profile
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == user.id
    ).first()


    # Get internships
    internships = db.query(Internship).all()


    # Profile data
    profile_data = None


    if profile:

        profile_data = {

            "degree": profile.degree,

            "branch": profile.branch,

            "cgpa": profile.cgpa
        }


    # Internship data
    internship_data = [

        {

            "id": internship.id,

            "title": internship.title,

            "organization": internship.organization,

            "domain": internship.domain,

            "location": internship.location,

            "work_mode": internship.work_mode,

            "duration": internship.duration,

            "stipend": internship.stipend,

            "required_degree": internship.required_degree,

            "required_branch": internship.required_branch,

            "minimum_cgpa": internship.minimum_cgpa,

            "application_deadline": internship.application_deadline,

            "application_url": internship.application_url,

            "status": internship.status

        }

        for internship in internships

    ]


    return {

        "user": {

            "id": user.id,

            "name": user.name,

            "email": user.email,

            "mobile": user.mobile

        },

        "profile": profile_data,

        "internships": internship_data
    }


# ==================================================
# US-16: VIEW AVAILABLE INTERNSHIPS
# ==================================================

@app.get("/internships")
def get_internships(

    db: Session = Depends(get_db)

):

    internships = db.query(Internship).filter(
        Internship.status == "Active"
    ).all()


    return [

        {

            "id": internship.id,

            "title": internship.title,

            "organization": internship.organization,

            "description": internship.description,

            "domain": internship.domain,

            "location": internship.location,

            "work_mode": internship.work_mode,

            "duration": internship.duration,

            "stipend": internship.stipend,

            "vacancies": internship.vacancies,

            "required_degree": internship.required_degree,

            "required_branch": internship.required_branch,

            "minimum_cgpa": internship.minimum_cgpa,

            "maximum_backlogs": internship.maximum_backlogs,

            "graduation_year": internship.graduation_year,

            "application_start_date": internship.application_start_date,

            "application_deadline": internship.application_deadline,

            "application_url": internship.application_url,

            "source_type": internship.source_type,

            "source_name": internship.source_name,

            "source_url": internship.source_url,

            "status": internship.status

        }

        for internship in internships

    ]

# ==================================================
# US-17: CANDIDATE SKILLS & CAREER INTERESTS
# ==================================================

@app.post("/candidate-preferences")
def create_candidate_preferences(
    data: CandidatePreferencesRequest,
    db: Session = Depends(get_db)
):

    # Check user
    user = db.query(User).filter(
        User.id == data.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    # Check if preferences already exist
    existing = db.query(CandidatePreferences).filter(
        CandidatePreferences.user_id == data.user_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Candidate preferences already exist"
        )

    preferences = CandidatePreferences(
        user_id=data.user_id,
        skills=data.skills,
        career_interests=data.career_interests,
        preferred_domain=data.preferred_domain,
        preferred_location=data.preferred_location,
        preferred_work_mode=data.preferred_work_mode
    )

    db.add(preferences)
    db.commit()
    db.refresh(preferences)

    return {
        "message": "Candidate preferences saved successfully",
        "preference_id": preferences.id
    }

@app.get("/candidate-preferences/{user_id}")
def get_candidate_preferences(
    user_id: int,
    db: Session = Depends(get_db)
):

    preferences = db.query(
        CandidatePreferences
    ).filter(
        CandidatePreferences.user_id == user_id
    ).first()

    if not preferences:
        raise HTTPException(
            status_code=404,
            detail="Candidate preferences not found"
        )

    return {
        "id": preferences.id,
        "user_id": preferences.user_id,
        "skills": preferences.skills,
        "career_interests": preferences.career_interests,
        "preferred_domain": preferences.preferred_domain,
        "preferred_location": preferences.preferred_location,
        "preferred_work_mode": preferences.preferred_work_mode
    }

@app.put("/candidate-preferences/{user_id}")
def update_candidate_preferences(
    user_id: int,
    data: CandidatePreferencesRequest,
    db: Session = Depends(get_db)
):

    preferences = db.query(
        CandidatePreferences
    ).filter(
        CandidatePreferences.user_id == user_id
    ).first()

    if not preferences:
        raise HTTPException(
            status_code=404,
            detail="Candidate preferences not found"
        )

    preferences.skills = data.skills
    preferences.career_interests = data.career_interests
    preferences.preferred_domain = data.preferred_domain
    preferences.preferred_location = data.preferred_location
    preferences.preferred_work_mode = data.preferred_work_mode

    db.commit()
    db.refresh(preferences)

    return {
        "message": "Candidate preferences updated successfully"
    }

@app.post("/generate-mcqs")
def generate_mcqs(
    data: GenerateMCQRequest,
    db: Session = Depends(get_db)
):
    # AI generation will happen here

    return {
        "message": "MCQs generated successfully"
    }

@app.post("/generate-mcqs")
def generate_mcqs(
    data: GenerateMCQRequest,
    db: Session = Depends(get_db)
):

    generated_questions = generate_mcqs(
        data.skill,
        data.number_of_questions,
        data.difficulty
    )

    saved_questions = []

    for item in generated_questions:

        mcq = SkillMCQ(
            skill=data.skill,
            question=item["question"],
            option_a=item["option_a"],
            option_b=item["option_b"],
            option_c=item["option_c"],
            option_d=item["option_d"],
            correct_answer=item["correct_answer"],
            difficulty=item["difficulty"]
        )

        db.add(mcq)
        saved_questions.append(mcq)

    db.commit()

    return {
        "message": "MCQs generated successfully",
        "skill": data.skill,
        "questions": [
            {
                "id": q.id,
                "skill": q.skill,
                "question": q.question,
                "option_a": q.option_a,
                "option_b": q.option_b,
                "option_c": q.option_c,
                "option_d": q.option_d,
                "difficulty": q.difficulty
            }
            for q in saved_questions
        ]
    }