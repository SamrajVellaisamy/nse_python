# from sqlalchemy import engine,create_engine 
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# sqlite_file_name = "./future.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

# connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, connect_args=connect_args)

# SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)
# Base = declarative_base()

# def get_db():
#     db=SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://admin:admin@cluster0.87wdxlx.mongodb.net/?appName=Cluster0")

client = AsyncIOMotorClient(MONGO_URL)
db = client["fast_api"]   # database name