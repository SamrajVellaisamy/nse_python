from fastapi import APIRouter,HTTPException,status
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from schema import *
from db import *
from routers.utils import *


route = APIRouter(prefix="/auth")
@route.post("/login", response_model=TokenData)
async def login(req:OAuth2PasswordRequestForm = Depends()):
    try: 
        user = await db.users.find_one({"username":req.username})
        if user and verify_password(req.password, user["password"]):
            return  {"access_token":create_token({"sub": user["username"]}),"token_type":"Bearer"}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid username or password!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Unable to login! Error: {e}")