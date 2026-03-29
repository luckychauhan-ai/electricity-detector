import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import random

st.title("⚡ Electricity Bill Anomaly Detector")

COST_PER_UNIT = 8

# ------------------ VIRTUAL METER ------------------
st.subheader("⚡ Virtual Meter")

if "meter" not in st.session_state:
    st.session_state.meter = 0

if st.button("Simulate Usage"):
    usage = random.uniform(0.5, 3.0)
    st.session_state.meter += usage

st.write(f"Current Meter Reading: {round(st.session_state.meter, 2)} units")

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

# ------------------ DATAFRAME ------------------
df = pd.DataFrame(st.session_state.data, columns=["Units"])

if not df.empty:

    df["Day"] = range(1, len(df) + 1)

    st.subheader("📊 Usage Data")
    st.write(df)

    # ------------------ CALCULATIONS ------------------
    avg = df["Units"].mean()
    predicted_bill = avg * 30 * COST_PER_UNIT

    st.subheader("💰 Bill Prediction")
    st.write(f"Estimated Monthly Bill: ₹ {round(predicted_bill, 2)}")

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

    # ------------------ ALERT ------------------
    if units > avg * 1.5:
        st.error(
            f"⚠️ High usage detected! Today's usage ({units}) is higher than average ({round(avg, 2)})"
        )

else:
    st.write("Enter data to begin...")