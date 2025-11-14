"""
Shared utility functions
"""
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from passlib.context import CryptContext
from jose import JWTError, jwt

from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())


def generate_history_id(test_name: str, parameters: Optional[Dict] = None) -> str:
    """
    Generate a consistent history ID for a test case
    This allows tracking the same test across different runs
    """
    base = test_name
    if parameters:
        # Sort parameters to ensure consistent hash
        param_str = "_".join(f"{k}:{v}" for k, v in sorted(parameters.items()))
        base = f"{test_name}_{param_str}"
    
    return hashlib.sha256(base.encode()).hexdigest()[:16]


def calculate_pass_rate(passed: int, total: int) -> float:
    """Calculate pass rate percentage"""
    if total == 0:
        return 0.0
    return round((passed / total) * 100, 2)


def format_duration(duration_ms: int) -> str:
    """Format duration in milliseconds to human-readable string"""
    if duration_ms < 1000:
        return f"{duration_ms}ms"
    elif duration_ms < 60000:
        seconds = duration_ms / 1000
        return f"{seconds:.1f}s"
    else:
        minutes = duration_ms / 60000
        return f"{minutes:.1f}m"


def calculate_flakiness_score(total_runs: int, passed_runs: int, failed_runs: int) -> float:
    """
    Calculate flakiness score for a test
    Score ranges from 0 (stable) to 1 (very flaky)
    """
    if total_runs < 2:
        return 0.0
    
    # Calculate the ratio of the minority status
    minority = min(passed_runs, failed_runs)
    flakiness = minority / total_runs
    
    # Weight by total runs (more runs = more confidence)
    confidence_factor = min(total_runs / 10, 1.0)
    
    return round(flakiness * confidence_factor, 3)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for storage"""
    import re
    # Remove or replace invalid characters
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = f"{name[:250]}.{ext}" if ext else name[:255]
    return filename


class Logger:
    """Simple logger wrapper"""
    
    @staticmethod
    def info(message: str, **kwargs):
        print(f"[INFO] {message}", kwargs)
    
    @staticmethod
    def error(message: str, **kwargs):
        print(f"[ERROR] {message}", kwargs)
    
    @staticmethod
    def warning(message: str, **kwargs):
        print(f"[WARNING] {message}", kwargs)
    
    @staticmethod
    def debug(message: str, **kwargs):
        if settings.DEBUG:
            print(f"[DEBUG] {message}", kwargs)


logger = Logger()

