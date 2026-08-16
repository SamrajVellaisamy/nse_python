from fastapi import APIRouter,status,Query,HTTPException
from db import Database

routes = APIRouter()
con_db = Database()

@routes.get("/nse/getHighOI")
async def getHighOI():
    result=[]
    getdata = await con_db.get_high_oi()
    if not getdata:
        raise HTTPException(status_code=404, detail="No stocks found")
    for data in getdata:
        if len(data["nearby_levels"]) > 0:
            result.append(data)
            
    return {"status":status.HTTP_200_OK,"result":list(result)} 