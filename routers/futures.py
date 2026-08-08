from fastapi import APIRouter,status,Query,HTTPException
import requests,json
from apscheduler.schedulers.background import BackgroundScheduler
from models import *
from sqlalchemy.orm import session
from fastapi.params import Depends
from db import Database
from common import *
from nsepython import *  
from datetime import *
from zoneinfo import ZoneInfo
from schema import *

BASE_ENV = os.getenv("ENV_URL","https://www.nseindia.com/api/") 

routes = APIRouter()
con_db = Database()

@routes.get("/nse/getStock")
async def getStock():
    getdata = await con_db.ims_stock_list()
    if not getdata:
        raise HTTPException(status_code=404, detail="No stocks found")
    return {"status":status.HTTP_200_OK,"result":list(getdata)} 

@routes.post("/nse/deleteStock")
async def deleteStock(request:stockName):  
    try:
      con_db.ims_stock_list_delete_many(request.symbol)
      return {"status":status.HTTP_200_OK,"result":"Stock deleted successfully"} 
    except Exception as e:
        raise HTTPException(status_code=404, detail="No stocks found") 

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
        priceChange += arr["underlyingValue"]
        pchange += arr["pchange"]
        TradedVolume += arr["totalTradedVolume"]
                
    return [changeOi,pchangeOi,priceChange,pchange,TradedVolume]

@routes.get("/nse/getFNO")
async def getOIData(): 
    getdata = await con_db.ims_future()
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
async def getOIData(name:str,date: str = Query(...)): 
    try: 
        getdata = await con_db.ims_future(name,date)
        if not len(str(getdata)):
            pass 
        data = list(getdata) 
        for i in range(len(data)-1): 
            data[i+1]['oiarrow'] = addArrow('changeOi',data,i)
            data[i+1]['pricearrow'] = addArrow('priceChange',data,i) 
        return {"status":status.HTTP_200_OK,"result":data[::-1]}
    except Exception:
        return {"status":status.HTTP_200_OK,"result":"Empty"} 




@routes.delete('/nse/fnoDelete')
async def deleteFno():
    try:
        delete = await con_db.ims_future_delete_many()
        if not delete:
            pass 
        return {"status":status.HTTP_200_OK,"result":"successfully deleted !"} 
    except:
        pass

@routes.get("/nse/deleteQuery")
async def deleteQuery(date: str = Query(...)): 
    try:
        delete = await con_db.ims_future_delete_many(date)
        if not delete:
            pass 
        return {"status":status.HTTP_200_OK,"result":"successfully deleted !"} 
    except:
        pass
