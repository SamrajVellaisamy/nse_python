from fastapi import APIRouter,status,Query
import requests,json
from apscheduler.schedulers.background import BackgroundScheduler
from models import *
from sqlalchemy.orm import session
from fastapi.params import Depends
from db import *
from common import *
from nsepython import *  
from datetime import *
import pytz

fnoList=[
  {
    "symbol": "HDFCBANK",
    "identifier": "BANKING_FINANCE"
  },
  {
    "symbol": "ICICIBANK",
    "identifier": "BANKING_FINANCE"
  },
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
  {
    "symbol": "ONGC",
    "identifier": "ENERGY"
  },
  {
    "symbol": "TMCV",
    "identifier": "AUTO"
  },
  {
        "symbol": "EICHERMOT",
        "identifier": "EICHERMOTEQN"
    },

  {
    "symbol": "LT",
    "identifier": "INFRA_CAPITAL_GOODS"
  },
  {
    "symbol": "BHEL",
    "identifier": "INFRA_CAPITAL_GOODS"
  },
  {
    "symbol": "HINDUNILVR",
    "identifier": "FMCG"
  },
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
  {
    "symbol": "TATASTEEL",
    "identifier": "METALS"
  },
  {
    "symbol": "NTPC",
    "identifier": "POWER_UTILITIES"
  },
  {
    "symbol": "POWERGRID",
    "identifier": "POWER_UTILITIES"
  },
  {
    "symbol": "DLF",
    "identifier": "REALTY"
  },
  {
    "symbol": "GODREJPROP",
    "identifier": "REALTY"
  },
  {
    "symbol": "BEL",
    "identifier": "DEFENCE_PSU"
  },
  {
    "symbol": "HAL",
    "identifier": "DEFENCE_PSU"
  },
  {
    "symbol": "M&M",
    "identifier": "AUTO"
  }
]

routes = APIRouter()

@routes.post("/nse/updateFNO")
async def call_api(): #db:session=Depends(get_db)  
    collectData=[]
    dt: str = Query(...)
    try: 
        for i in range(len(fnoList)):
            r = nsefetch("https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi?functionName=getSymbolDerivativesData&symbol="+fnoList[i]['symbol']+"&instrumentType=FUT")   # Replace with your API   
            results = r['data']
            [changeOi,priceChange,pchangeOi,pchange] = addValues(results)
            collectData.append({"changeOi":changeOi,"priceChange":priceChange,"symbol":fnoList[i]['symbol'],"pchangeOi":pchangeOi,"pchange":pchange,"createdAt":datetime.now(pytz.timezone("Asia/Kolkata"))}) 
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

    for arr in arrays:
        changeOi  += arr["changeinOpenInterest"]
        pchangeOi += arr["pchangeinOpenInterest"]
        priceChange += arr["change"]
        pchange += arr["pchange"]
                
    return [changeOi,pchangeOi,priceChange,pchange]

@routes.get("/nse/getFNO")
async def getOIData(): 
    getdata = await db.futures.find({},  {"_id":0}).to_list(length=100)
    if not getdata:
        pass
    return {"status":status.HTTP_200_OK,"result":list(getdata)}

@routes.get("/nse/getFNO/{name}")
async def getOIData(name:str):
    getdata = await db.futures.find({"symbol":name},{"_id":0}).to_list(length=100)
    if not len(str(getdata)):
        pass 
    data = ((list(getdata))) 
    for i in range(len(data)-1): 
      data[i+1]['oiarrow'] = '<mat-icon>arrow_upward</mat-icon>' if data[i]['changeOi'] < data[i+1]['changeOi'] else '<mat-icon>arrow_downward</mat-icon>'
      data[i+1]['pricearrow'] = '<mat-icon>arrow_upward</mat-icon>' if data[i]['pchangeOi'] < data[i+1]['pchangeOi'] else '<mat-icon>arrow_downward</mat-icon>'
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
