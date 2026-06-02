from fastapi import FastAPI,Request
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
from routers import product,futures,users,login
from models import *  
from nsepython import *   

@app.get('/nse/futureindices')
def getIndices(request:Request):
    BaseUrl = str(request.base_url) 
    try:           
        result = callApi(BASE_ENV+"underlying-information")
        return {'status':200,'result':result["data"]["UnderlyingList"]+result["data"]["IndexList"]}
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