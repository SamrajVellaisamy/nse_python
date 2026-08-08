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

import datetime
import os 
from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    
    def __init__(self):  
        # MONGO_URI = os.getenv("MONGO_URI","mongodb+srv://admin:admin@cluster0.87wdxlx.mongodb.net/?appName=Cluster0")
        MONGO_URI =  os.getenv("MONGO_URI","mongodb://127.0.0.1:27017/?tls=false&ssl=false&tlsAllowInvalidCertificates=true")

        client = AsyncIOMotorClient(
            MONGO_URI,
            tls=False,
            ssl=False,
            tlsAllowInvalidCertificates=True,   # Railway fix
            serverSelectionTimeoutMS=30000
        )

        client.admin.command('ping')

        self.db = client["IMS"]


    def get_ims_stock_list(self):
        return self.db.ims_stock_list.find({},  {"_id":0}).to_list(length=100)

    def ims_cash_market(self,symbol):
        return self.db.ims_cash_market.find({"symbol": symbol},  {"_id":0}).sort([("_id", -1)]).to_list(length=60)

    def ims_cash_market_delete(self,symbol):
        self.db.ims_cash_market.delete_one({"symbol": symbol})
        
    def ims_cash_market_deletemany(self):
        return self.db.ims_cash_market.delete_many({})

    def ims_stock_list(self):
        return self.db.ims_stock_list.find({},  {"_id":0}).to_list(length=100)
        
    def ims_stock_list_delete_many(self,symbol):
        return self.db.ims_stock_list.delete_many({"symbol": symbol})

    def ims_future(self):
        return self.db.ims_future.find({},  {"_id":0}).sort[{"createdAt": -1}].to_list(length=100)

    def ims_future(self,name,date):
        return self.db.ims_future.find({"symbol":name,"createdAt": {"$gte": date}},{"_id":0}).to_list(length=100) 

    def ims_future_delete_many(self):
        return self.db.ims_future.delete_many({})

    def ims_future_delete_many(self,date):
        return self.db.ims_future.delete_many({"createdAt": {"$gt": datetime.fromisoformat(date)}})

    def market_snapshot_find(self,symbol,date):
        return self.db.market_snapshot.find({"symbol": symbol, "timestamp": {"$gte": date}}, {"_id": 0}).sort([("timestamp", -1)]).to_list(length=100)
    
    def get_score_market(self,symbol,date):
        return self.db.ims_stock_score.find({"symbol":symbol,"created_at":{"$gte":date}},{"_id":0}).sort([("created_at", -1)]).to_list(length=100)
        
    print("Successfully connected to the local MongoDB server!")
    