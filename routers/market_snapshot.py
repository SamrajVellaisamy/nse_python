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


routes = APIRouter()
con_db = Database()

@routes.get("/nse/getSnapshot")
async def getSnapshot(symbol: str, date: str = Query(...)):
    try:
        getdata = await con_db.market_snapshot_find(symbol,date)
        if not getdata:
            raise HTTPException(status_code=404, detail="No snapshot data found")
        return {"status": status.HTTP_200_OK, "result": list(getdata)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to retrieve snapshot data! Error: {e}")