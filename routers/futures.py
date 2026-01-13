from fastapi import APIRouter,status
import requests,json
from apscheduler.schedulers.background import BackgroundScheduler
from models import *
from sqlalchemy.orm import session
from fastapi.params import Depends
from db import *
from common import *
from nsepython import *  

fnoList = [{"symbol":"ONGC"},{"symbol":"EICHERMOT"},{"symbol":"LT"},{"symbol":"BHEL"},{"symbol":"HINDUNILVR"},{"symbol":"ITC"},{"symbol":"SUNPHARMA"},{"symbol":"CIPLA"},{"symbol":"HINDALCO"},{"symbol":"TATASTEEL"},{"symbol":"NTPC"},{"symbol":"POWERGRID"},{"symbol":"DLF"},{"symbol":"GODREJPROP"},{"symbol":"BEL"},{"symbol":"HAL"},{"symbol":"NATIONALUM"}]

routes = APIRouter()

@routes.post("/updateFNO")
async def call_api(): #db:session=Depends(get_db)  
    collectData=[]
    try: 
        for i in range(len(fnoList)):
            r = nsefetch("https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi?functionName=getSymbolDerivativesData&symbol="+fnoList[i]['symbol']+"&instrumentType=FUT")   # Replace with your API   
            results = r['data'] 
            [changeOi,priceChange,expiryDate] = addValues(results) 
            collectData.append({"changeOi":changeOi,"price":priceChange,"symbol":fnoList[i]['symbol'],"expiryDate":expiryDate}) 
        future = await db.futures.insert_many(collectData) 
        if not len(str(future)):
                print("not usse")
        return {"data":[ str(_id) for _id in future]}
    except Exception as e:
        print("Error:", e)

def addValues(arrays):  
    merged = {} 
    changeOi = 0
    priceChange = 0 
    for arr in arrays:
        changeOi  += arr["changeinOpenInterest"]
        priceChange += arr["pchange"]
        expiryDate = arr["expiryDate"]
                
    return [changeOi,priceChange,expiryDate]

@routes.get("/getFNO")
async def getOIData(): 
    getdata = await db.futures.find({}).to_list(length=100)
    if not getdata:
        pass
    return {"status":status.HTTP_200_OK,"result":{"data":[ str(_id) for _id in getdata]}}

@routes.get("/getFNO/{name}")
async def getOIData(name:str):
    getdata = await db.futures.find({"symbol":name},{"_id":0}).to_list(length=100)
    if not len(str(getdata)):
        pass
    return {"status":status.HTTP_200_OK,"result":{"data":[str(_id) for _id in getdata]}}

@routes.delete('/fnoDelete')
async def deleteFno():
    try:
        delete = await db.futures.delete_many({})
        if not delete:
            pass 
        return {"status":status.HTTP_200_OK,"result":"successfully deleted !"} 
    except:
        pass
