from fastapi import APIRouter
from common import *
import requests
import pandas as pd
from db import *

routers = APIRouter()
BASE_ENV = os.getenv("ENV_URL","https://www.nseindia.com/api/") 
@routers.post("/nse/cashMarketValue")
# async def cash_market_value():
#     stockList =  await db.stockList.find({},  {"_id":0}).to_list(length=100) 
#     try:
#         for stock in stockList: 
#             storeData = {}
#             response = callApi(BASE_ENV + "NextApi/apiClient/GetQuoteApi?functionName=getSymbolData&marketType=N&series=EQ&symbol="+stock['symbol'])  
#             equity_response = response['equityResponse'][0]   
#             last_document = await db.ims_cash_market.find_one({"symbol":stock['symbol']},sort=[("_id",-1)])  
            
#             if last_document and "totalTradedVolume" in last_document:
#                 Traded_Old_Volume_value = last_document["totalTradedVolume"]
#             else:
#                 Traded_Old_Volume_value = 0

#             storeData.update({"changeVolume": equity_response['tradeInfo']['totalTradedVolume'] - Traded_Old_Volume_value,"totalTradedVolume": equity_response['tradeInfo']['totalTradedVolume'],"totalTradedValue": equity_response['tradeInfo']['totalTradedValue'],"lastPrice": equity_response['tradeInfo']['lastPrice'],"lastUpdateTime": equity_response['lastUpdateTime'],"symbol": equity_response['metaData']['symbol'],"open": equity_response['metaData']['open'],"dayHigh": equity_response['metaData']['dayHigh'],"dayLow": equity_response['metaData']['dayLow'],"previousClose": equity_response['metaData']['previousClose'],"change": equity_response['metaData']['change'],"pChange": equity_response['metaData']['pChange']}) 
#             insert_result = await db.ims_cash_market.insert_one(storeData) 
#     except Exception as e:
#         return {"status": 500,"error": str(e)} 

@routers.get("/nse/getCashMarketValue")
async def get_cash_market_value(symbol: str): 
    try:
        getdata = await db.ims_cash_market.find({"symbol": symbol},  {"_id":0}).to_list(length=100) 
        if not getdata:
            raise HTTPException(status_code=404, detail="No market data found")
        return {"status":200,"result":list(getdata)} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve market data! Error: {e}")

@routers.delete("/nse/deleteCashMarketValue")
async def delete_cash_market_value(symbol: str): 
    try:
        getdata = await db.ims_cash_market.delete_one({"symbol": symbol})
        if not getdata:
            raise HTTPException(status_code=404, detail="No market data found")
        return {"status":200,"result":list(getdata)} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve market data! Error: {e}")

@routers.delete("/nse/deleteManyCashMarketValue")
async def deleteManyCashMarketValue(): 
    try:
        getdata = await db.ims_cash_market.delete_many({})
        if not getdata:
            raise HTTPException(status_code=404, detail="No market data found")
        return {"status":200,"result":list(getdata)} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve market data! Error: {e}")



#averagePrice - vwap
#tradedVolume - totalTradedVolume
 