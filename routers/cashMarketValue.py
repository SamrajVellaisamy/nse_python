from fastapi import APIRouter, HTTPException
from common import *
import requests
import pandas as pd
import os 
from db import Database

routers = APIRouter()
con_db = Database()

BASE_ENV = os.getenv("ENV_URL","https://www.nseindia.com/api/") 
@routers.get("/nse/getCashMarketValue")
async def get_cash_market_value(symbol: str): 
    try:
        getdata = await con_db.ims_cash_market(symbol=symbol) 
        if not getdata:
            raise HTTPException(status_code=404, detail="No market data found")
        return {"status":200,"result":list(getdata)} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve market data! Error: {e}")

@routers.delete("/nse/deleteCashMarketValue")
async def delete_cash_market_value(symbol: str): 
    try:
        getdata = await con_db.ims_cash_market_delete({"symbol": symbol})
        if not getdata:
            raise HTTPException(status_code=404, detail="No market data found")
        return {"status":200,"result":list(getdata)} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve market data! Error: {e}")

@routers.delete("/nse/deleteManyCashMarketValue")
async def deleteManyCashMarketValue(): 
    try:
        getdata = await con_db.ims_cash_market_deletemany()
        if not getdata:
            raise HTTPException(status_code=404, detail="No market data found")
        return {"status":200,"result":list(getdata)} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve market data! Error: {e}")



#averagePrice - vwap
#tradedVolume - totalTradedVolume
 