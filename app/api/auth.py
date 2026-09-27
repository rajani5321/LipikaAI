import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import UserLogin, UserRegister, UserResponse
from app.db.client import db_manager

router = APIRouter(prefix="/auth", tags=["Authentication & Admin Users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister):
    clean_username = user_in.username.strip().lower()
    if not clean_username:
        raise HTTPException(status_code=400, detail="Username cannot be empty")
        
    # Check if username or email already exists
    existing = db_manager.users.find_one({"username": clean_username})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{clean_username}' is already registered."
        )

    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "username": clean_username,
        "password": user_in.password,
        "name": user_in.name.strip(),
        "role": user_in.role.strip() or "Technical Recruiter",
        "department": user_in.department.strip() or "Human Resources",
        "email": user_in.email.strip().lower(),
        "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    }

    db_manager.users.insert_one(user_doc)
    db_manager.log_activity("User Registration", f"New HR Admin '{user_doc['name']}' registered.", "auth")

    return UserResponse(
        id=user_id,
        username=user_doc["username"],
        name=user_doc["name"],
        role=user_doc["role"],
        department=user_doc["department"],
        email=user_doc["email"]
    )

@router.post("/login", response_model=UserResponse)
def login(credentials: UserLogin):
    login_id = credentials.username.strip().lower()
    
    # Allow login by username OR email
    user = db_manager.users.find_one({"username": login_id})
    if not user and "@" in login_id:
        user = db_manager.users.find_one({"email": login_id})
        
    if not user or user.get("password") != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    db_manager.log_activity("User Login", f"HR Admin '{user.get('name')}' logged in.", "auth")

    return UserResponse(
        id=str(user.get("id") or user.get("_id")),
        username=user.get("username"),
        name=user.get("name", "HR Manager"),
        role=user.get("role", "Lead Recruiter"),
        department=user.get("department", "Human Resources"),
        email=user.get("email", "")
    )

@router.get("/me", response_model=UserResponse)
def get_current_user(username: Optional[str] = None):
    # If specific username requested
    if username:
        user = db_manager.users.find_one({"username": username.strip().lower()})
        if user:
            return UserResponse(
                id=str(user.get("id") or user.get("_id")),
                username=user.get("username"),
                name=user.get("name"),
                role=user.get("role"),
                department=user.get("department"),
                email=user.get("email", "")
            )

    # Default to Lipika Murmu or first registered user
    user = db_manager.users.find_one({"username": "lipika"})
    if not user:
        user = db_manager.users.find_one({"username": "admin"})
    if not user:
        user = db_manager.users.find_one({})

    if user:
        return UserResponse(
            id=str(user.get("id") or user.get("_id")),
            username=user.get("username"),
            name=user.get("name", "Lipika Murmu"),
            role=user.get("role", "Lead Technical Recruiter"),
            department=user.get("department", "Human Resources"),
            email=user.get("email", "lipika.murmu@lipikaai.com")
        )

    return UserResponse(
        id="demo-hr-01",
        username="lipika",
        name="Lipika Murmu",
        role="Lead Technical Recruiter",
        department="Human Resources",
        email="lipika.murmu@lipikaai.com"
    )

@router.get("/users", response_model=List[UserResponse])
def list_users():
    users = db_manager.users.find({})
    return [
        UserResponse(
            id=str(u.get("id") or u.get("_id")),
            username=u.get("username"),
            name=u.get("name", "Admin"),
            role=u.get("role", "Recruiter"),
            department=u.get("department", "HR"),
            email=u.get("email", "")
        )
        for u in users
    ]
