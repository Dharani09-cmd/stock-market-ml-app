import streamlit as st
import matplotlib.pyplot as plt
from stock_prediction import predict_price
from auth import create_user_table, signup, login

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Stock Market Predictor", layout="wide")

# ----------------- INIT DB -----------------
create_user_table()

# ----------------- SESSION STATE -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =================================================
# 🔐 LOGIN / SIGNUP PAGE
# =================================================
if not st.session_state.logged_in:
    st.title("🔐 Stock Market Predictor")

    choice = st.radio("Select Option", ["Login", "Signup"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Signup":
        if st.button("Create Account"):
            if signup(username, password):
                st.success("✅ Account created successfully! Please login.")
            else:
                st.error("❌ Username already exists.")

    if choice == "Login":
        if st.button("Login"):
            if login(username, password):
                st.session_state.logged_in = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

# =================================================
# 📊 DASHBOARD
# =================================================
else:
    st.title("📈 Real-Time Stock Market Data Analysis & Prediction")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.write("Enter **multiple stock symbols** separated by commas.")

    tickers = st.text_input(
        "Stock Symbols (Example: AAPL, TSLA, MSFT)",
        "AAPL, TSLA"
    )

    ticker_list = [t.strip().upper() for t in tickers.split(",")]

    if st.button("Analyze Stocks"):
        plt.figure(figsize=(10, 5))

        for ticker in ticker_list:
            try:
                price, data = predict_price(ticker)

                st.success(f"✅ {ticker} → Predicted Price After 30 Days: ${price}")

                plt.plot(data['Close'], label=ticker)

            except:
                st.error(f"❌ Error fetching data for {ticker}")

        plt.xlabel("Date")
        plt.ylabel("Stock Price")
        plt.legend()
        st.pyplot(plt)
