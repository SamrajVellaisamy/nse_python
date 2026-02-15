from pydantic import BaseModel, Field
from datetime import date 
from typing import Optional
from utils import PyObjectId

class Pivot(BaseModel):
    high: float | int=0
    low: float | int=0
    close: float | int=0
    open: float | int=0
    days: float | int=0
    vixValue: float | int=0
    market: float | int=0

class Stock(BaseModel):
    symbol:str
    fromdate:str
    todate:str
    limit:int
    page:int
    percentage:int

class BriefHistory(BaseModel):
    symbol:str
    fromdate:str
    todate:str

class OptionHistory(BaseModel):
    fromdate:str
    todate:str
    optionType:str
    strike:str
    symbol:str
    expirydate:str

class FutureRequest(BaseModel):
    symbol:str
    expirydate:str
    previousDate:str
    toDate:str

class tokenRequest(BaseModel):
    nsit:str
    nseappid:str

class FuturesData:
    changeOI:int
    price:int

class stockName(BaseModel):
    symbol:str

class FutureDataOut(FuturesData):
    id: PyObjectId = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {PyObjectId: str}
 