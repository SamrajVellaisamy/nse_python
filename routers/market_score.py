from fastapi import APIRouter,Query
from db import Database

router = APIRouter()
con_db = Database()

@router.get("/nse/marketscore/")
async def getScoreMarket(symbol:str,date:str = Query(...)): 
    try:
        getScore = await con_db.get_score_market(symbol,date)
        if not getScore:
            pass
        return {"status":200,"result":list(getScore)}
    except Exception:
        return {"status":400,"Message":"Failed to get market score!"}
