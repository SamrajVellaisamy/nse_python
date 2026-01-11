import pandas as pd
import pandas_ta as ta
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# --- Stock symbols ---
symbols = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "LT.NS", "SBIN.NS", "HINDUNILVR.NS", "AXISBANK.NS", "ITC.NS"
]

start_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
qualified = []

# --- Custom Supertrend function (robust) ---
def supertrend(df, period=7, multiplier=3):
    # Calculate ATR safely
    atr = ta.atr(df["High"], df["Low"], df["Close"], length=period)
    if atr is None or atr.isna().all():
        raise ValueError("ATR calculation failed (all NaN)")

    atr = atr.fillna(method="bfill").fillna(method="ffill")

    hl2 = (df["High"] + df["Low"]) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)

    final_upperband = upperband.copy()
    final_lowerband = lowerband.copy()
    supertrend = pd.Series(index=df.index)
    direction = pd.Series(index=df.index)

    for i in range(1, len(df)):
        curr, prev = i, i - 1
        # Carry forward bands
        if df["Close"].iloc[curr] > final_upperband.iloc[prev]:
            direction.iloc[curr] = 1
        elif df["Close"].iloc[curr] < final_lowerband.iloc[prev]:
            direction.iloc[curr] = -1
        else:
            direction.iloc[curr] = direction.iloc[prev]
            if direction.iloc[curr] == 1 and final_lowerband.iloc[curr] < final_lowerband.iloc[prev]:
                final_lowerband.iloc[curr] = final_lowerband.iloc[prev]
            if direction.iloc[curr] == -1 and final_upperband.iloc[curr] > final_upperband.iloc[prev]:
                final_upperband.iloc[curr] = final_upperband.iloc[prev]
        supertrend.iloc[curr] = (
            final_lowerband.iloc[curr] if direction.iloc[curr] == 1 else final_upperband.iloc[curr]
        )

    df["Supertrend"] = supertrend.fillna(method="bfill").fillna(method="ffill")
    return df

# --- Main Scanner ---
for sym in symbols:
    try:
        df = yf.download(sym, start=start_date, interval="1d", progress=False, auto_adjust=False)
        
        if df.empty or len(df) < 200:
            print(f"⚠️ Skipping {sym}: insufficient data")
            continue
        df.dropna(subset=["High", "Low", "Close"], inplace=True)
        # --- Indicators ---
        df["SMA20"] = ta.sma(df["Close"], length=20)
        df["SMA200"] = ta.sma(df["Close"], length=200)
        df = supertrend(df, period=7, multiplier=3)
        df["RSI14"] = ta.rsi(df["Close"], length=14)
        df["Prev_High"] = df["High"].shift(1)

        latest = df.iloc[-1] 

        # --- Skip incomplete data ---
        if df[["SMA20", "SMA200", "Supertrend", "RSI14", "Prev_High"]].iloc[-1].isna().any():
            print(f"⚠️ Skipping {sym}: indicators not ready")
            continue

        # --- Condition ---
        if (
            latest["SMA20"] > latest["SMA200"]
            and latest["Close"] > latest["SMA20"]
            and latest["Close"] > latest["Supertrend"]
            and latest["RSI14"] > 40
            and latest["Close"] > latest["Prev_High"]
        ):
            qualified.append(sym)
            print(f"✅ {sym} meets condition on {latest.name.date()}")
        else:
            print(f"❌ {sym} does not meet condition")

    except Exception as e:
        print(f"⚠️ Error processing {sym}: {e}")

# --- Final Output ---
print("\n📊 Stocks meeting all conditions:\n")
if qualified:
    print(qualified)
else:
    print("None found.")
