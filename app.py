import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import random

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Electricity Detector", layout="wide")

st.title("⚡ Electricity Bill Anomaly Detector")

COST_PER_UNIT = 8

# ------------------ VIRTUAL METER ------------------
st.subheader("⚡ Virtual Meter")

if "meter" not in st.session_state:
    st.session_state.meter = 0

if st.button("Simulate Usage"):
    st.session_state.meter += random.uniform(0.5, 3.0)

st.write(f"Current Meter Reading: {round(st.session_state.meter,2)} units")

# ------------------ DATA STORAGE ------------------
if "data" not in st.session_state:
    st.session_state.data = []

# ------------------ INPUT ------------------
st.subheader("Add Data")

use_meter = st.checkbox("Use Virtual Meter Reading")

if use_meter:
    units = st.session_state.meter
else:
    units = st.number_input("Enter today's units", min_value=0.0)

if st.button("Add Data"):
    st.session_state.data.append(units)

# Reset button
if st.button("Reset Data"):
    st.session_state.data = []
    st.session_state.meter = 0

# ------------------ DATAFRAME ------------------
df = pd.DataFrame(st.session_state.data, columns=["Units"])

if not df.empty:

    df["Day"] = range(1, len(df) + 1)

    st.subheader("📊 Usage Data")
    st.dataframe(df)

    # ------------------ CALCULATIONS ------------------
    avg = df["Units"].mean()
    predicted_bill = avg * 30 * COST_PER_UNIT

    # Metrics UI
    col1, col2 = st.columns(2)
    col1.metric("Average Usage", round(avg, 2))
    col2.metric("Predicted Bill", f"₹ {round(predicted_bill, 2)}")

    # ------------------ COST ANALYSIS ------------------
    st.subheader("💸 Cost Analysis")
    df["Cost"] = df["Units"] * COST_PER_UNIT
    st.dataframe(df)

    # ------------------ PEAK USAGE ------------------
    max_day = df.loc[df["Units"].idxmax()]
    st.write(f"🔥 Highest usage on Day {int(max_day['Day'])}: {round(max_day['Units'],2)} units")

    # ------------------ DAILY CHANGE ------------------
    if len(df) > 1:
        change = ((df["Units"].iloc[-1] - df["Units"].iloc[-2]) / df["Units"].iloc[-2]) * 100
        st.write(f"📊 Change from yesterday: {round(change,2)}%")

    # ------------------ RISKY DAYS ------------------
    st.subheader("⚠️ Risky Days")
    risky_days = df[df["Units"] > avg * 1.5]

    if not risky_days.empty:
        st.write(risky_days)
    else:
        st.write("No risky days detected")

    # ------------------ AI ANOMALY ------------------
    st.subheader("🧠 AI-Based Anomaly Detection")

    if len(df) > 5:
        model = IsolationForest(contamination=0.2)
        df["anomaly"] = model.fit_predict(df[["Units"]])

        anomalies = df[df["anomaly"] == -1]

        if not anomalies.empty:
            st.write(anomalies)
        else:
            st.write("No anomalies detected")

        st.write("Anomalies are detected using Isolation Forest ML model")
    else:
        st.write("Add more data for AI detection")

    # ------------------ GRAPH ------------------
    st.subheader("📈 Usage Graph")

    fig, ax = plt.subplots()
    ax.plot(df["Day"], df["Units"])
    ax.set_xlabel("Day")
    ax.set_ylabel("Units")
    ax.set_title("Daily Electricity Usage")

    st.pyplot(fig)

    # ------------------ DOWNLOAD ------------------
    st.subheader("📥 Download Report")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", csv, "electricity_report.csv", "text/csv")

    # ------------------ ALERT ------------------
    if units > avg * 1.5:
        st.error(f"⚠️ High usage detected! Today's usage ({units}) is higher than average ({round(avg, 2)})")

else:
    st.write("Enter data to begin...")
