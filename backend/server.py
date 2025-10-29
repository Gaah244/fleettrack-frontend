from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import bcrypt
import jwt
from passlib.context import CryptContext

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
ALGORITHM = "HS256"

# Commission rates per truck type
COMMISSION_RATES = {
    "BKO": 3.50,
    "PYW": 3.50,
    "NYC": 3.50,
    "GKY": 7.50,
    "GSD": 7.50,
    "AUA": 10.00
}

TRUCK_TYPES = ["BKO", "PYW", "NYC", "GKY", "GSD", "AUA"]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============= MODELS =============

class UserRegister(BaseModel):
    username: str
    password: str
    role: str = "driver"  # driver, helper, or admin

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    username: str
    role: str
    createdAt: str

class DeliveryUpdate(BaseModel):
    userId: str
    truck_type: str
    count: int

class UserStats(BaseModel):
    id: str
    username: str
    role: str
    total_deliveries: int
    total_commission: float
    deliveries_by_truck: dict

# ============= HELPER FUNCTIONS =============

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    """Verify that the current user is an admin"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def calculate_user_stats(user_id: str) -> dict:
    """Calculate total deliveries and commission for a user"""
    deliveries = await db.deliveries.find({"userId": user_id}, {"_id": 0}).to_list(1000)
    
    total_deliveries = 0
    total_commission = 0.0
    deliveries_by_truck = {truck: 0 for truck in TRUCK_TYPES}
    
    for delivery in deliveries:
        truck_type = delivery.get("truck_type")
        count = delivery.get("count", 0)
        
        if truck_type in COMMISSION_RATES:
            total_deliveries += count
            deliveries_by_truck[truck_type] = count
            total_commission += count * COMMISSION_RATES[truck_type]
    
    return {
        "total_deliveries": total_deliveries,
        "total_commission": round(total_commission, 2),
        "deliveries_by_truck": deliveries_by_truck
    }

# ============= AUTH ROUTES =============

@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    """Register a new user"""
    # Check if username already exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Validate role
    if user_data.role not in ["driver", "helper", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'driver', 'helper', or 'admin'")
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(user_data.password)
    
    new_user = {
        "id": user_id,
        "username": user_data.username,
        "password": hashed_pwd,
        "role": user_data.role,
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(new_user)
    
    # Initialize deliveries for all truck types
    for truck in TRUCK_TYPES:
        await db.deliveries.insert_one({
            "id": str(uuid.uuid4()),
            "userId": user_id,
            "truck_type": truck,
            "count": 0,
            "updatedAt": datetime.now(timezone.utc).isoformat()
        })
    
    # Create token
    token = create_access_token({"sub": user_id})
    
    return {
        "message": "User registered successfully",
        "token": token,
        "user": {
            "id": user_id,
            "username": user_data.username,
            "role": user_data.role
        }
    }

@api_router.post("/auth/login")
async def login(credentials: UserLogin):
    """Login a user and return JWT token"""
    # Find user by username
    user = await db.users.find_one({"username": credentials.username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Verify password
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create token
    token = create_access_token({"sub": user["id"]})
    
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "role": current_user["role"]
    }

# ============= DELIVERY ROUTES =============

@api_router.get("/deliveries/my")
async def get_my_deliveries(current_user: dict = Depends(get_current_user)):
    """Get current user's deliveries and commission"""
    stats = await calculate_user_stats(current_user["id"])
    
    return {
        "user": {
            "id": current_user["id"],
            "username": current_user["username"],
            "role": current_user["role"]
        },
        "stats": stats,
        "commission_rates": COMMISSION_RATES
    }

@api_router.post("/deliveries/update")
async def update_deliveries(update: DeliveryUpdate, admin: dict = Depends(get_admin_user)):
    """Admin only: Update delivery count for a user and truck type"""
    # Validate truck type
    if update.truck_type not in TRUCK_TYPES:
        raise HTTPException(status_code=400, detail="Invalid truck type")
    
    # Check if user exists
    user = await db.users.find_one({"id": update.userId})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update or create delivery record
    result = await db.deliveries.update_one(
        {"userId": update.userId, "truck_type": update.truck_type},
        {
            "$set": {
                "count": update.count,
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    # Calculate updated stats
    stats = await calculate_user_stats(update.userId)
    
    return {
        "message": "Delivery updated successfully",
        "stats": stats
    }

@api_router.get("/deliveries/all-users")
async def get_all_users_stats(admin: dict = Depends(get_admin_user)):
    """Admin only: Get all users with their stats"""
    users = await db.users.find({"role": {"$in": ["driver", "helper"]}}, {"_id": 0, "password": 0}).to_list(1000)
    
    users_with_stats = []
    for user in users:
        stats = await calculate_user_stats(user["id"])
        users_with_stats.append({
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "total_deliveries": stats["total_deliveries"],
            "total_commission": stats["total_commission"],
            "deliveries_by_truck": stats["deliveries_by_truck"]
        })
    
    return {"users": users_with_stats}

@api_router.post("/deliveries/reset-month")
async def reset_month(admin: dict = Depends(get_admin_user)):
    """Admin only: Reset all deliveries for the new month"""
    # Reset all delivery counts to 0
    result = await db.deliveries.update_many(
        {},
        {
            "$set": {
                "count": 0,
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return {
        "message": "All deliveries reset successfully for the new month",
        "updated_count": result.modified_count
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()