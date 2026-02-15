from fastapi import APIRouter,status,Query,HTTPException
import requests,json
from apscheduler.schedulers.background import BackgroundScheduler
from models import *
from sqlalchemy.orm import session
from fastapi.params import Depends
from db import *
from common import *
from nsepython import *  
from datetime import *
from zoneinfo import ZoneInfo
from schema import *

fnoList=[
  {
    "symbol": "HDFCBANK",
    "identifier": "BANKING_FINANCE"
  },
  # {
  #   "symbol": "ICICIBANK",
  #   "identifier": "BANKING_FINANCE"
  # },
  {
    "symbol": "TCS",
    "identifier": "IT"
  },
  {
    "symbol": "INFY",
    "identifier": "IT"
  },
  {
    "symbol": "RELIANCE",
    "identifier": "ENERGY"
  },
  # {
  #   "symbol": "ONGC",
  #   "identifier": "ENERGY"
  # },
  {
        "symbol": "EICHERMOT",
        "identifier": "EICHERMOTEQN"
    },

  # {
  #   "symbol": "LT",
  #   "identifier": "INFRA_CAPITAL_GOODS"
  # },
  # {
  #   "symbol": "BHEL",
  #   "identifier": "INFRA_CAPITAL_GOODS"
  # },
  # {
  #   "symbol": "HINDUNILVR",
  #   "identifier": "FMCG"
  # },
  {
    "symbol": "ITC",
    "identifier": "FMCG"
  },
  {
    "symbol": "SUNPHARMA",
    "identifier": "PHARMA"
  },
  {
    "symbol": "CIPLA",
    "identifier": "PHARMA"
  },
  {
    "symbol": "HINDALCO",
    "identifier": "METALS"
  },
  # {
  #   "symbol": "TATASTEEL",
  #   "identifier": "METALS"
  # },
  {
    "symbol": "POWERGRID",
    "identifier": "POWER_UTILITIES"
  },
  # {
  #   "symbol": "GODREJPROP",
  #   "identifier": "REALTY"
  # },
  # {
  #   "symbol": "BEL",
  #   "identifier": "DEFENCE_PSU"
  # },
  # {
  #   "symbol": "HAL",
  #   "identifier": "DEFENCE_PSU"
  # },
#   {
#     "symbol": "M&M",
#     "identifier": "AUTO"
#   }
]

routes = APIRouter()

@routes.post("/nse/addStock")
async def addStock(stocks:list[str]):
    setStock = set()  
    for stock in stocks:
        setStock.add(stock)
    collectData = []
    for symbol in setStock:
        collectData.append({"symbol": symbol,"identifier": symbol})
    try:
      stocklist = await db.stockList.insert_many(collectData)
      return {"status":status.HTTP_200_OK,"result":"Stocks added successfully"}
    except Exception as e:
        print("Error inserting stock data:", e)

@routes.get("/nse/getStock")
async def getStock():
    getdata = await db.stockList.find({},  {"_id":0}).to_list(length=100)
    if not getdata:
        raise HTTPException(status_code=404, detail="No stocks found")
    return {"status":status.HTTP_200_OK,"result":list(getdata)} 

@routes.post("/nse/deleteStock")
async def deleteStock(request:stockName):  
    try:
      db.stockList.delete_many({"symbol": request.symbol})
      return {"status":status.HTTP_200_OK,"result":"Stock deleted successfully"} 
    except Exception as e:
        raise HTTPException(status_code=404, detail="No stocks found") 

@routes.post("/nse/updateFNO")
async def call_api(): #db:session=Depends(get_db)  
    collectData=[]
    dt: str = Query(...) 
    try: 
        getStocks = await db.stockList.find({},  {"_id":0}).to_list(length=100)
        getStocks = [x['symbol'] for x in getStocks]
        if not getStocks:
            getStocks = ["HDFCBANK"]
        for symbol in getStocks:
            print('symbol',symbol)
            r = callApi("https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi?functionName=getSymbolDerivativesData&symbol="+symbol+"&instrumentType=FUT")   # Replace with your API   
            results = r['data']
            [changeOi,pchangeOi,priceChange,pchange,TradedVolume] = addValues(results) 
            collectData.append({"changeOi":changeOi,"priceChange":priceChange,"symbol":symbol,"pchangeOi":pchangeOi,"pchange":pchange,"createdAt":datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),"TradedVolume":TradedVolume}) 
        future = await db.futures.insert_many(collectData) 
        if not len(str(future)):
                print("not usse") 
        # getData = await db.futures.find({}).to_list(length=100) 
        return {"data":[ str(_id) for _id in future]}
    except Exception as e:
        print("Error:", e)

def addValues(arrays):  
    merged = {} 
    changeOi = 0
    priceChange = 0
    pchangeOi = 0
    pchange = 0
    TradedVolume = 0

    for arr in arrays: 
        changeOi  += arr["changeinOpenInterest"]
        pchangeOi += arr["pchangeinOpenInterest"]
        priceChange += arr["lastPrice"] - arr["openPrice"]
        pchange += arr["pchange"]
        TradedVolume += arr["totalTradedVolume"]
                
    return [changeOi,pchangeOi,priceChange,pchange,TradedVolume]

@routes.get("/nse/getFNO")
async def getOIData(): 
    getdata = await db.futures.find({},  {"_id":0}).to_list(length=100)
    if not getdata:
        pass
    return {"status":status.HTTP_200_OK,"result":list(getdata)}

def addArrow(params,data,i):
    if data[i][params] < data[i+1][params]:
      return '<mat-icon>arrow_upward</mat-icon>'
    elif data[i][params] > data[i+1][params]: 
        return '<mat-icon>arrow_downward</mat-icon>'
    else:
        return '-'
    
@routes.get("/nse/getFNO/{name}")
async def getOIData(name:str):
    getdata = await db.futures.find({"symbol":name},{"_id":0}).to_list(length=100)
    if not len(str(getdata)):
        pass 
    data = ((list(getdata))) 
    for i in range(len(data)-1): 
      data[i+1]['oiarrow'] = addArrow('changeOi',data,i)
      data[i+1]['pricearrow'] = addArrow('priceChange',data,i) 
    return {"status":status.HTTP_200_OK,"result":data[::-1]}




@routes.delete('/nse/fnoDelete')
async def deleteFno():
    try:
        delete = await db.futures.delete_many({})
        if not delete:
            pass 
        return {"status":status.HTTP_200_OK,"result":"successfully deleted !"} 
    except:
        pass

@routes.get("/nse/deleteQuery")
async def deleteQuery(date: str = Query(...)):
    print('data',date)
    try:
        delete = await db.futures.delete_many({"createdAt": {"$gt": datetime.fromisoformat(date)}})
        if not delete:
            pass 
        return {"status":status.HTTP_200_OK,"result":"successfully deleted !"} 
    except:
        pass
