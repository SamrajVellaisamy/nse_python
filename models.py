# from sqlalchemy import Column,ForeignKey,Integer,String,DateTime,Float
# from db import Base  
# from datetime import datetime   

# class Future(Base):
#     __tablename__ = 'future'
#     id = Column(Integer,primary_key=True,index=True)
#     name = Column(String)
#     changeOi = Column(Float)
#     priceChange = Column(Float)
#     expiryDate = Column(String)
#     created_at = Column(DateTime, default=datetime.utcnow)  # Set on insert
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
