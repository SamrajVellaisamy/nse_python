import json
import requests
import pandas as pd
import random
import time

# ----------------------------------------------
def get_futures_data(data):  
    """
    Reliable NSE Futures data fetcher.
    Works for both index and stock futures.
    """  
    fut_chain = data
    if not fut_chain:
        return {}
    # The first contract is usually the near-month
    first = fut_chain    
    oi = first.get("changeinOpenInterest", 0)
    prev_oi = first.get("openInterest", 0)
    last_price = first.get("lastPrice",0)
    prev_close = first.get("prevClose",0)
    expiry = first.get("expiryDate",0)     
    return get_signal(last_price - prev_close,oi,expiry)
# ----------------------------------------------
def get_signal(price_change, oi_change,expiry):
    if price_change > 0 and oi_change > 0:
        return f"{expiry}🟢 Long Buildup → BUY CALL"
    elif price_change > 0 and oi_change < 0:
        return f"{expiry}🟡 Short Covering → Mild Bullish"
    elif price_change < 0 and oi_change > 0:
        return f"{expiry}🔴 Short Buildup → SELL CALL"
    elif price_change < 0 and oi_change < 0:
        return f"{expiry}🟠 Long Unwinding → Weakness"
    else:
        return "⚪ Neutral"

# ----------------------------------------------
def optionOIanalyze(data, percent_range=5, top_n=3):     
    # OPTION CHAIN
    opt_data = data
    rec = opt_data["records"]
    spot = rec["underlyingValue"]
    expiry = rec["expiryDates"][0]
    ce_rows, pe_rows = [], []
    for item in rec["data"]:
        strike = item.get("strikePrice")
        if "CE" in item:
            ce = item["CE"]
            ce_rows.append({
                "strike": strike,
                "OI": ce["openInterest"],
                "COI": ce["changeinOpenInterest"],
                "LTP": ce["lastPrice"]
            })
        if "PE" in item:
            pe = item["PE"]
            pe_rows.append({
                "strike": strike,
                "OI": pe["openInterest"],
                "COI": pe["changeinOpenInterest"],
                "LTP": pe["lastPrice"]
            })

    ce_df = pd.DataFrame(ce_rows)
    pe_df = pd.DataFrame(pe_rows)
    low, high = spot * (1 - percent_range / 100), spot * (1 + percent_range / 100)
    ce_df = ce_df[(ce_df.strike >= low) & (ce_df.strike <= high)]
    pe_df = pe_df[(pe_df.strike >= low) & (pe_df.strike <= high)]
    ce_top = ce_df.sort_values(["OI", "COI"], ascending=False).head(top_n)
    pe_top = pe_df.sort_values(["OI", "COI"], ascending=False).head(top_n)
    return {"putOi":json.loads(pe_top.to_json(orient='records', indent=2)),"callOi":json.loads(ce_top.to_json(orient='records', indent=2))}