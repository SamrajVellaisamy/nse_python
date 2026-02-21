# from bson import ObjectId

# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return ObjectId(v)

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status,Depends

pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')
Oauth_Scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


SECRET_KEY ="JKFGUEHGJKEKJGHIUFNGKJDFNKUGHFSGNLKJSFIU"
SET_MINUTES = 30
ALGORITHM = "HS256"

def hash_password(password): 
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data:dict,expires_delta: timedelta | None = None):
    update_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=SET_MINUTES)
    update_encode.update({"exp": expire})
    token = jwt.encode(update_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token:str=Depends(Oauth_Scheme)): 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token!")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token!")