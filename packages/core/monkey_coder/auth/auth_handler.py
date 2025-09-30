# auth_module.py

from fastapi import FastAPI, Depends, HTTPException, status, Security, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import timedelta
import secrets
import uuid

# --- CONFIGURATION ---

SECRET_KEY = "YOUR_SUPER_SECRET_KEY_CHANGE_ME"  # Use env var in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
API_KEY_HEADER_NAME = "X-API-Key"

# --- PASSWORD HASHING ---

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# --- MODELS ---

class User(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True

class UserInDB(User):
    api_key: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    api_key: str
    user: Dict[str, Any]

class TokenData(BaseModel):
    user_id: Optional[str] = None

# --- IN-MEMORY STORES (Replace with DB in production) ---

fake_users_db: Dict[str, UserInDB] = {}
active_sessions: Dict[str, Dict[str, Any]] = {}  # session_id: {user_id, expires, refresh_token}

# --- JWT UTILS ---

from ..utils.time import utc_now

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = utc_now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str):
    expire = utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"user_id": user_id, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# --- API KEY UTILS ---

def generate_api_key() -> str:
    return secrets.token_urlsafe(32)

def get_user_by_api_key(api_key: str) -> Optional[UserInDB]:
    for user in fake_users_db.values():
        if user.api_key == api_key:
            return user
    return None

# --- AUTHENTICATION DEPENDENCIES ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)

def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    user = next((u for u in fake_users_db.values() if u.email == email), None)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(
    token: str = Security(oauth2_scheme),
    api_key: Optional[str] = Security(api_key_header)
) -> UserInDB:
    # Try JWT first
    if token:
        try:
            payload = decode_token(token)
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            user_id: str = payload.get("user_id")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            # Session check
            session = active_sessions.get(payload.get("session_id"))
            if not session or session["user_id"] != user_id:
                raise HTTPException(status_code=401, detail="Session expired or invalid")
            user = fake_users_db.get(user_id)
            if user is None or not user.is_active:
                raise HTTPException(status_code=401, detail="Inactive user")
            return user
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid JWT token")
    # Try API Key
    if api_key:
        user = get_user_by_api_key(api_key)
        if user and user.is_active:
            return user
        raise HTTPException(status_code=403, detail="Invalid API key")
    raise HTTPException(status_code=401, detail="Not authenticated")

# --- FASTAPI APP & ROUTES ---

app = FastAPI(title="Auth Module Example")

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    # Session management
    session_id = str(uuid.uuid4())
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email, "session_id": session_id}
    )
    refresh_token = create_refresh_token(user.id)
    active_sessions[session_id] = {
        "user_id": user.id,
        "expires": utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "refresh_token": refresh_token
    }
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        api_key=user.api_key,
        user={"id": user.id, "email": user.email}
    )

@app.post("/auth/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        user_id = payload.get("user_id")
        user = fake_users_db.get(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Inactive user")
        # Find session by refresh token
        session_id = next((sid for sid, s in active_sessions.items() if s["refresh_token"] == refresh_token), None)
        if not session_id:
            raise HTTPException(status_code=401, detail="Session not found")
        # Issue new access token
        new_access_token = create_access_token(
            data={"user_id": user.id, "email": user.email, "session_id": session_id}
        )
        return Token(
            access_token=new_access_token,
            refresh_token=refresh_token,
            api_key=user.api_key,
            user={"id": user.id, "email": user.email}
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@app.post("/auth/logout")
async def logout(request: Request, token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
        session_id = payload.get("session_id")
        if session_id and session_id in active_sessions:
            del active_sessions[session_id]
        return {"msg": "Logged out"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/protected")
async def protected_route(current_user: UserInDB = Depends(get_current_user)):
    return {"msg": f"Hello, {current_user.email}!"}

# --- USER REGISTRATION (for testing/demo) ---

@app.post("/auth/register")
async def register(email: EmailStr, password: str):
    if any(u.email == email for u in fake_users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    api_key = generate_api_key()
    user = UserInDB(
        id=user_id,
        email=email,
        hashed_password=hash_password(password),
        api_key=api_key
    )
    fake_users_db[user_id] = user
    return {"msg": "User registered", "api_key": api_key}

# --- ERROR HANDLING ---

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    return await fastapi.responses.JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# --- SECURITY NOTES ---
# - Use HTTPS in production.
# - Store SECRET_KEY and sensitive config in environment variables.
# - Replace in-memory stores with a persistent database.
# - Rotate API keys and JWT secrets regularly.
# - Implement rate limiting and monitoring for brute-force protection.