import streamlit as st
import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import ssl
import warnings

ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")

st.set_page_config(page_title="AI Stock Analyzer", layout="wide")

st.title("🤖 AI Multi-Stock Market Analysis & Prediction Dashboard")
st.write("Supports NSE (.NS) & US Stocks — Example: TCS, ITC, SBIN, AAPL")


def format_symbol(symbol):
    symbol = symbol.strip().upper()
    if "." not in symbol:
        return symbol + ".NS"
    return symbol


def market_mood(df):
    if df is None or df.empty or len(df) < 21:
        return "⚪ Not Enough Data"
    last = float(df["Close"].iloc[-1])
    prev = float(df["Close"].iloc[-21])
    change = ((last - prev) / prev) * 100
    if change > 5:
        return "🟢 Bullish"
    elif change < -5:
        return "🔴 Bearish"
    return "⚪ Neutral"


def risk_score(df):
    if df is None or df.empty:
        return "⚪ Unknown"
    returns = df["Close"].pct_change().dropna()
    if returns.empty:
        return "⚪ Unknown"
    vol = float(returns.std() * 100)
    if vol < 1.2:
        return "🟢 Low Risk"
    elif vol < 2.5:
        return "🟡 Medium Risk"
    return "🔴 High Risk"


def crash_warning(df):
    if df is None or df.empty or len(df) < 8:
        return "⚪ Not Enough Data"
    last = float(df["Close"].iloc[-1])
    week = float(df["Close"].iloc[-8])
    drop = ((week - last) / week) * 100
    return "⚠ Possible Downtrend" if drop > 6 else "✔ Stable"


def predict_price(df):
    df = df.reset_index(drop=True)
    df["Days"] = np.arange(len(df))
    X = df[["Days"]]
    y = df["Close"]
    model = LinearRegression()
    model.fit(X, y)
    future = np.array([[len(df) + 30]])
    return float(model.predict(future)[0])


def performance_score(df):
    if df is None or df.empty:
        return 0
    start = float(df["Close"].iloc[0])
    end = float(df["Close"].iloc[-1])
    return ((end - start) / start) * 100


def portfolio_recommendation(results):
    sorted_stocks = sorted(results, key=lambda x: x["growth"], reverse=True)
    return {
        "Low Risk": sorted_stocks[-1]["symbol"],
        "Balanced": sorted_stocks[len(sorted_stocks) // 2]["symbol"],
        "High Return": sorted_stocks[0]["symbol"],
    }


symbols = st.text_input(
    "Enter Stock Symbols (comma separated):",
    "TCS, ITC, SBIN, WIPRO",
)

if st.button("Analyze"):

    stocks = [format_symbol(s) for s in symbols.split(",")]
    results = []

    for stock in stocks:
        st.subheader(stock)

        try:
            df = yf.download(stock, period="1y", progress=False)

            if df is None or df.empty:
                st.error(f"❌ No data found for {stock}")
                continue

            df = df.dropna()

            if df.empty:
                st.error(f"❌ No usable data for {stock}")
                continue

            st.line_chart(df["Close"])

            pred = predict_price(df)
            mood = market_mood(df)
            risk = risk_score(df)
            warn = crash_warning(df)
            growth = performance_score(df)

            st.write(f"**Predicted Price (30 days): ₹{pred:.2f}**")
            st.write(f"Market Mood: {mood}")
            st.write(f"Risk Level: {risk}")
            st.write(f"Crash Signal: {warn}")
            st.write(f"Performance Growth: {growth:.2f}%")

            results.append(
                {
                    "symbol": stock,
                    "pred": pred,
                    "mood": mood,
                    "risk": risk,
                    "warn": warn,
                    "growth": growth,
                }
            )

        except Exception as e:
            st.error(f"{stock} failed — {str(e)}")

    if results:

        st.subheader("🏆 Performance Ranking")

        ranked = sorted(results, key=lambda x: x["growth"], reverse=True)

        for i, r in enumerate(ranked, 1):
            st.write(f"{i}. **{r['symbol']}** — {r['growth']:.2f}% growth")

        st.subheader("💼 Suggested Portfolio")

        p = portfolio_recommendation(results)

        st.success(f"✔ Safe Investor → {p['Low Risk']}")
        st.success(f"✔ Balanced Investor → {p['Balanced']}")
        st.success(f"✔ High Return Investor → {p['High Return']}")

        st.subheader("🤖 AI Insights")

        for r in results:
            st.info(f"{r['symbol']} → {r['mood']} | {r['risk']} | {r['warn']}")
