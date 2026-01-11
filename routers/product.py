from fastapi import APIRouter
from schema import Pivot

route = APIRouter(prefix="/pivot")

# @route.get('/')
# def product():
#     return "hello sam"


@route.post('/')
def pivotCalculation(pivot:Pivot): 
    High = pivot.high
    Low = pivot.low
    Close = pivot.close
    Open = pivot.open 
    Days = pivot.days
    vixValue = pivot.vixValue
    Market = pivot.market
    if Open:
        return tradeDay(High,Low,Close,Open)           
    elif Days:
        return vixCal(Days,vixValue,Market)            
    elif (not(Open) and not(Days)):
        return morethanDay(High,Low,Close)
    else:
        return {'status':400,'result':[]}
    
def morethanDay(High,Low,Close): 
    P = (High + Low + Close) / 3 
    R1 = (P * 2) - Low 
    R2 = P + (High - Low) 
    S1 = (P * 2) - High
    S2 = P - (High - Low) 
    R3 = High + 2*(P-Low) 
    S3 = Low - 2*(High-P) 
    return {'status':200,"Pivot":P ,"S1" :S1,"R1" :R1,"S2" :S2,"R2" :R2,"S3" : S3, "R3" :R3}
        
def tradeDay(High,Low,Close,Open):        
    P = (High + Close + Low + Open) / 4  
    S1 = 2 * P - High
    R1 = 2 * P - Low         
    S2 = P - (R1 - S1)
    R2 = P + (R1 - S1)
    S3 = Low - 2 * (High - P)
    R3 = High + 2 * (P - Low) 
    return {"Pivot":P ,"S1" :S1,"R1" :R1,"S2" :S2,"R2" :R2,"S3" : S3, "R3" :R3}

        
def vixCal(Days,vixValue,Market):  
    vValue = vixValue / math.sqrt(365 / Days) 
    v_high = Market + (Market*vValue / 100)
    v_low = Market - (Market*vValue / 100) 
    return {'status':202,"Vix high": v_high,"Vix Low":v_low}