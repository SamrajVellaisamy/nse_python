from fastapi import APIRouter,HTTPException,status
from fastapi.params import Depends
from schema import *
from db import *
from routers.utils import *

route = APIRouter(prefix="/nse")

@route.post("/users")
async def createUser(req:user): 
    try: 
        item = {"username":req.username,"password":hash_password(req.password)}
        users = await db.users.insert_one(item)
        return {"status":200,"message":"User created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Unable to create! Error: {e}")

@route.get("/users",response_model=list[DisplayUser])    
async def getUser(current_user:user=Depends(verify_token)):
    try: 
        users = await db.users.find({},{"password":0}).to_list(length=None)
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Unable to retrieve users! Error: {e}")
    
@route.get("/users/{username}",response_model=DisplayUser)
async def getUserByUsername(username:str):
    try: 
        user = await db.users.find_one({"username":username},{"password":0})
        if user:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Unable to retrieve user! Error: {e}")
    
@route.put("/users/{username}")
async def updateUser(username:str,req:user):
    try: 
        update_data = {"$set": {"password": hash_password(req.password)}}
        result = await db.users.update_one({"username": username}, update_data)
        if result.modified_count == 1:
            return {"status":200,"message":"User updated successfully!"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found!")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Unable to update user! Error: {e}")
    
@route.delete("/users/{username}")
async def deleteUser(username:str):
    try: 
        result = await db.users.delete_one({"username": username})
        if result.deleted_count == 1:
            return {"status":200,"message":"User deleted successfully!"}  
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Unable to delete user! Error: {e}")