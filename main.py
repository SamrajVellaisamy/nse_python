from fastapi import FastAPI,Request,status 
from fastapi.middleware.cors import CORSMiddleware
import requests
import datetime as dt
from datetime import date,timedelta  
import asyncio
from schema import Stock,OptionHistory,FutureRequest
from common import *
from tokenGen import fetch_nse_cookies 
from collections import defaultdict
from trade import *
from routers import product,futures,users,login,cashMarketValue,market_snapshot,market_score
from models import *  
from nsepython import *  
from apscheduler.schedulers.background import BackgroundScheduler 
from zoneinfo import ZoneInfo
from contextlib import asynccontextmanager
from filter import performers
from db import Database

scheduler = BackgroundScheduler()
con_db = Database()
    
app = FastAPI(title="NSE APP DATA", description="We can collect NSE data here as much as we want",tags=["Live"]) 

# Base.metadata.create_all(engine) 

# app.include_router(login.route,tags=["Login"])
# app.include_router(users.route,tags=["User"])
# app.include_router(product.route,tags=["Pivot"])
app.include_router(futures.routes,tags=["Futures"])
app.include_router(cashMarketValue.routers,tags=["Cash Market Value"])
app.include_router(market_snapshot.routes,tags=["Market Snapshot"])
app.include_router(market_score.router,tags=["Market score"])
# fnoList = fnolist()
historyResults = []
today = date.today()
prevDate = today-timedelta(days=31)
prevDate = prevDate.strftime("%d-%m-%Y") 
todayIs = today.strftime("%d-%m-%Y")  
formatOne = "%Y-%m-%d"
formatTwo = "%d-%m-%Y"  
indices=[]
checkSymbol=''
stockList=[]
stockHistories=[]
percentage = 0

origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://localhost:8080",
    "http://127.0.0.1:8000/docs",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials='true',
    allow_methods=["*"],
    allow_headers=["*"],
)

BaseUrl="http://127.0.0.1:8000/nse/"

BASE_ENV = os.getenv("ENV_URL","https://www.nseindia.com/api/") 
 
@app.get('/nse/nselist')
def lists(request:Request):
    BaseUrl = str(request.base_url)
    niftyList = ["NIFTY 50",
    "NIFTY NEXT 50",
    "NIFTY BANK",
    "NIFTY IT",
    "NIFTY MEDIA",
    "NIFTY METAL",
    "NIFTY PHARMA",
    "NIFTY AUTO",
    "NIFTY ENERGY",
    "NIFTY MIDCAP 50",
    "NIFTY MIDCAP 100",
    "NIFTY MIDCAP 150",
    "NIFTY SMALLCAP 50",
    "NIFTY SMALLCAP 100",
    "NIFTY SMALLCAP 250",
    "NIFTY FINANCIAL SERVICES",       
    "NIFTY MIDSMALLCAP 400",
    "NIFTY 100",
    "NIFTY 200"]
    try:
        # for i in nse_index()['indexName']:
        #     if 'INDIA VIX' not in i and len(i) < 15:
        #         indices.append(i)
        return {'status': 200,'list':niftyList}
    except:
        return {'status': 400,'msg':"Error in list"}

@app.get('/nse/futureindices')
async def getIndices(request:Request):
    BaseUrl = str(request.base_url) 
    try:           
        result = await con_db.get_ims_stock_list(); #callApi(BASE_ENV+"underlying-information")
        # return {'status':200,'result':result["data"]["UnderlyingList"]+result["data"]["IndexList"]}
        return {"status":status.HTTP_200_OK,"result":list(result)} 
    except Exception as e:
        return {'status':400,'error':e}

@app.get("/nse/futureContracts/{symbol}")
def futureContracts(symbol:str):
    header = callApi("https://www.nseindia.com/json/quotes/derivative-all-contracts.json")['columns']
    indimate = []
    try:  
        output = callApi('https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi?functionName=getSymbolDerivativesData&symbol='+symbol+'&instrumentType=FUT')
        for con in output['data']:  
            indimate.append(get_futures_data(con))
            
        return {'status':200,'header':header,'result':output['data'],'status':indimate} 
    except:
        return {'status':404,'header':[],'result':[]} 
    
@app.get('/nse/option/{symbol}')
def expiryList(symbol:str):   
    expiry = callApi('https://www.nseindia.com/api/NextApi/apiClient/GetQuoteApi?functionName=getOptionChainDropdown&symbol='+symbol)
    try:           
        result0 = callApi(BASE_ENV+"NextApi/apiClient/GetQuoteApi?functionName=getOptionChainData&symbol="+symbol+"&params=expiryDate="+expiry['expiryDates'][0])

        result1 = callApi(BASE_ENV+"NextApi/apiClient/GetQuoteApi?functionName=getOptionChainData&symbol="+symbol+"&params=expiryDate="+expiry['expiryDates'][1])

        result2 = callApi(BASE_ENV+"NextApi/apiClient/GetQuoteApi?functionName=getOptionChainData&symbol="+symbol+"&params=expiryDate="+expiry['expiryDates'][2])
      
        return {'status':200,'result':option([result0['data'],result1['data'],result2['data']])}
    except Exception as e:
        return {'status':400,'error':e}

def option(arrays):   
    merged = {} 
    for arr in arrays:
        for item in arr:
            strike = item["strikePrice"]

            # First time → insert entire object
            if strike not in merged:
                merged[strike] = item.copy()
                continue

            # Merge CE section safely
            if "CE" in item and "CE" in merged[strike]:
                for k, v in item["CE"].items():
                    if v is None:
                        continue  # ignore null
                    if isinstance(v, (int, float)):
                        # add numbers
                        old = merged[strike]["CE"].get(k)
                        if isinstance(old, (int, float)):
                            merged[strike]["CE"][k] = old + v
                    else:
                        # overwrite only non-null strings
                        merged[strike]["CE"][k] = v

            # Merge PE section safely
            if "PE" in item and "PE" in merged[strike]:
                for k, v in item["PE"].items():
                    if v is None:
                        continue  # ignore null
                    if isinstance(v, (int, float)):
                        old = merged[strike]["PE"].get(k)
                        if isinstance(old, (int, float)):
                            merged[strike]["PE"][k] = old + v
                    else:
                        merged[strike]["PE"][k] = v

    return list(merged.values())
    
@app.post('/nse/optionHistory')
def optionHistory(request:OptionHistory):  
    fromDate = (dt.datetime.strptime(request.fromdate,formatOne)).strftime(formatTwo)
    toDate = (dt.datetime.strptime(request.todate,formatOne)).strftime(formatTwo) 
    optiontype = request.optionType
    strike = request.strike
    symbol = request.symbol
    expirydate = request.expirydate
    try:
        optionResult = callApi(BASE_ENV+"NextApi/apiClient/GetQuoteApi?functionName=getDerivativesHistoricalData&symbol="+symbol+"&instrumentType=OPTSTK&year=&expiryDate="+expirydate+"&strikePrice="+strike+"&optionType=&fromDate="+fromDate+"&toDate="+toDate) 
        chain = []
        result = []
        combined = defaultdict(lambda: {
            "CE_FH_OPEN_INT": 0,
            "CE_FH_CHANGE_IN_OI": 0,
            "PE_FH_OPEN_INT": 0,
            "PE_FH_CHANGE_IN_OI": 0,
        }) 
        for entry in optionResult:  
            chain.append({
                "strike": entry["FH_STRIKE_PRICE"],
                "CE_FH_OPEN_INT": entry["FH_OPEN_INT"] if entry["FH_OPTION_TYPE"] == "CE" else "0" ,
                "CE_FH_CHANGE_IN_OI":entry["FH_CHANGE_IN_OI"] if entry["FH_OPTION_TYPE"] == "CE" else "0",
                "PE_FH_OPEN_INT": entry["FH_OPEN_INT"] if entry["FH_OPTION_TYPE"] == "PE" else "0",
                "PE_FH_CHANGE_IN_OI":entry["FH_CHANGE_IN_OI"] if entry["FH_OPTION_TYPE"] == "PE" else "0",
                "FH_MARKET_LOT":entry["FH_MARKET_LOT"]
            })
        
        for entry in chain:
            strike = entry["strike"]
            combined[strike]["CE_FH_OPEN_INT"] += int(entry["CE_FH_OPEN_INT"])
            combined[strike]["CE_FH_CHANGE_IN_OI"] += float(entry["CE_FH_CHANGE_IN_OI"])
            combined[strike]["PE_FH_OPEN_INT"] += int(entry["PE_FH_OPEN_INT"])
            combined[strike]["PE_FH_CHANGE_IN_OI"] += float(entry["PE_FH_CHANGE_IN_OI"])

        
        for strike, values in combined.items():
            result.append({
                "strike": strike,
                "CE_FH_OPEN_INT": values["CE_FH_OPEN_INT"],
                "CE_FH_CHANGE_IN_OI": values["CE_FH_CHANGE_IN_OI"],
                "PE_FH_OPEN_INT": values["PE_FH_OPEN_INT"],
                "PE_FH_CHANGE_IN_OI": values["PE_FH_CHANGE_IN_OI"]
            })
  
        return {'status':200,"realdata":optionResult,'result':sorted(result, key=lambda x: x["strike"])}
        # return {'status':200,'result':result}
    except: 
        return {'status':400,'currenPrice':'-','optionList':'output'}

@app.post('/nse/fnoview/')
def NseViewFNO(request:FutureRequest):    
    symbol = request.symbol
    expirydate = request.expirydate
    previousDate = request.previousDate if request.previousDate  else prevDate
    toDate = request.toDate if request.toDate  else todayIs
    
    try:  
        fnoResult = callApi(BASE_ENV+"NextApi/apiClient/GetQuoteApi?functionName=getDerivativesHistoricalData&symbol="+symbol+"&instrumentType=FUTSTK&year=&expiryDate=&strikePrice=&optionType=&fromDate="+previousDate+"&toDate="+toDate)

        header = callApi('https://www.nseindia.com/json/quotes/derivatives-historical.json')['columns']

        return {'status':200,'header':header,'result':fnoResult} 
    except: 
        return {'status':400,header:[],'result':[]}

@app.post('/nse/prev_history')
def prev_history(request:Stock): 
    fromDate = (dt.datetime.strptime(request.fromdate,formatOne)).strftime(formatTwo)
    toDate = (dt.datetime.strptime(request.todate,formatOne)).strftime(formatTwo) 
    limit = request.limit
    header = callApi('https://www.nseindia.com/json/quotes/equity-historical.json')
    stockList = callApi('https://www.nseindia.com/api/equity-stockIndices?index='+request.symbol)['data'] 
    historyResults = []
    try:
        for i in range(0,len(stockList)):
            if('NIFTY' not in stockList[i]['symbol']):
                payload = callApi(
                BASE_ENV+"NextApi/apiClient/GetQuoteApi?functionName=getHistoricalTradeData&symbol=" + re.sub("&", "%26",stockList[i]['symbol']) + "&series=EQ&fromDate=" + fromDate + "&toDate=" + toDate)
                if len(payload) > 0:
                    historyResults.append(payload) 
        return {'status': 200,'result':historyResults,'header':header['columns'],'total':len(stockList)}
    except Exception as e:
        return {'status': 200,'result':historyResults,'header':header['columns'],'total':len(stockList)}

    
def changePercentage(a,b):
    p = (((a/b)-1)*100)
    return round(p) 

@app.post('/nse/tokens')
def createToken():
    return {'status':200,'result':asyncio.run(fetch_nse_cookies())}

def alignDateTime():
    [date,time,day] = dt.datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S %w").split(" ") 
    return {"Date":date,"Time":time > "09:15:00" and time < "15:30:00","Day":day != "6" and day != "0"}

def call_api(): 
    if alignDateTime()['Time'] and alignDateTime()['Day']:
        requests.post(BaseUrl+"updateFNO")
        requests.post(BaseUrl+"cashMarketValue")  
    else:
        print("Market is closed. Scheduler will run when market opens.")
     
def call_delete_api():
    requests.get(BaseUrl+"fnoDelete")

def create_scheduler():
    # print('create call api')
    scheduler = BackgroundScheduler()
    scheduler.add_job(call_api, "interval", minutes=5)
    scheduler.start()
    return scheduler

def token_create_scheduler(): 
    scheduler = BackgroundScheduler()
    scheduler.add_job(createToken, "interval", minutes=20)
    scheduler.start()
    return scheduler

token_scheduler = token_create_scheduler()

# scheduler = create_scheduler() 

@app.get("/nse/shutdown")
def shutdown_event():
    scheduler.pause()
    token_scheduler.pause()
    return {"message": "Scheduler shut down successfully."}

@app.get("/nse/startup")
def startup():
    call_api()
    scheduler.resume()
    token_scheduler.resume()
    return {"message": "Scheduler started successfully."}
 
@app.get("/nse/currentOI")
def currentOi(fno:str):
    collectData=[] 
    r = callApi(BASE_ENV+"NextApi/apiClient/GetQuoteApi?functionName=getSymbolDerivativesData&symbol="+fno+"&instrumentType=FUT")   # Replace with your API   
    results = r['data'] 
    [changeOi,pchangeOi,priceChange,pchange,TradedVolume] = futures.addValues(results)
    collectData.append({"changeOi":changeOi,"priceChange":priceChange/3,"symbol":fno,"pchangeOi":pchangeOi,"pchange":pchange,"TradedVolume":TradedVolume,"oiarrow":"","pricearrow":""})
    return {'status':200,'result':collectData} 
 
# from multiprocessing import Process, Value
# @app.get("/nse/topperformers")
# def topperformers():
#     try:
#         top_performers = Process(target = performers)  # Set a timeout of 60 seconds
#         top_performers.start()
#         top_performers.join()  # Wait for the process to finish or
#         return {'status':200,'result':top_performers}
#     except Exception as e:
#         return {'status':400,'error':str(e)}