
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import random

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Electricity Dashboard", layout="wide")

# ------------------ LOGIN ------------------
st.sidebar.title("👤 User Info")

name = st.sidebar.text_input("Enter Name")
meter_id = st.sidebar.text_input("Meter ID")

start = st.sidebar.button("Start Monitoring")

if not start:
    st.warning("Please enter details and click Start Monitoring")
    st.stop()

# ------------------ HEADER ------------------
st.title("⚡ Electricity Bill Anomaly Detector")

st.success(f"Welcome {name} 👋")
st.info(f"Meter ID: {meter_id}")

COST_PER_UNIT = 8

# ------------------ SESSION ------------------
if "meter" not in st.session_state:
    st.session_state.meter = 0

if "data" not in st.session_state:
    st.session_state.data = []

# ------------------ VIRTUAL METER ------------------
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⚡ Simulate Usage"):
        st.session_state.meter += random.uniform(0.5, 3.0)
    st.metric("Meter Reading", round(st.session_state.meter, 2))

with col2:
    use_meter = st.checkbox("Use Virtual Meter")

    if use_meter:
        units = st.session_state.meter
    else:
        units = st.number_input("Enter units", min_value=0.0)

    if st.button("➕ Add Data"):
        st.session_state.data.append(units)

with col3:
    if st.button("🔄 Reset"):
        st.session_state.data = []
        st.session_state.meter = 0

# ------------------ DATA ------------------
df = pd.DataFrame(st.session_state.data, columns=["Units"])

if not df.empty:

    df["Day"] = range(1, len(df)+1)

    avg = df["Units"].mean()
    predicted_bill = avg * 30 * COST_PER_UNIT

    # ------------------ METRICS ------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Average Usage", round(avg, 2))
    c2.metric("Predicted Bill", f"₹ {round(predicted_bill, 2)}")
    c3.metric("Total Days", len(df))

    # ------------------ GRAPH ------------------
    st.subheader("📈 Usage Trend")

    fig, ax = plt.subplots()
    ax.plot(df["Day"], df["Units"], marker="o")

    # Highlight anomalies (after AI)
    if len(df) > 5:
        model = IsolationForest(contamination=0.2, random_state=42)
        df["anomaly"] = model.fit_predict(df[["Units"]])

        anomalies = df[df["anomaly"] == -1]

        ax.scatter(anomalies["Day"], anomalies["Units"])  # red dots default

    ax.set_xlabel("Day")
    ax.set_ylabel("Units")
    st.pyplot(fig)

    # ------------------ COST ------------------
    df["Cost"] = df["Units"] * COST_PER_UNIT
    st.subheader("💸 Cost Table")
    st.dataframe(df)

    # ------------------ PEAK ------------------
    max_day = df.loc[df["Units"].idxmax()]
    st.success(f"🔥 Highest Usage: Day {int(max_day['Day'])} ({round(max_day['Units'],2)} units)")

    # ------------------ DAILY CHANGE ------------------
    if len(df) > 1:
        change = ((df["Units"].iloc[-1] - df["Units"].iloc[-2]) / df["Units"].iloc[-2]) * 100
        st.write(f"📊 Change from yesterday: {round(change,2)}%")

    # ------------------ RISKY ------------------
    st.subheader("⚠️ Risky Days")
    risky = df[df["Units"] > avg * 1.5]

    if not risky.empty:
        st.warning(risky)
    else:
        st.info("No risky days")

    # ------------------ AI SECTION ------------------
    st.subheader("🧠 AI Anomaly Detection")

    if len(df) > 5:
        if not anomalies.empty:
            st.error("⚠️ Anomalies Detected")
            st.dataframe(anomalies)
        else:
            st.success("✅ No anomalies detected")

        st.info("Isolation Forest algorithm is used for anomaly detection")
    else:
        st.warning("Add at least 6 days of data")

    # ------------------ DOWNLOAD ------------------
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Report", csv, "report.csv")

    # ------------------ ALERT ------------------
    if units > avg * 1.5:
        st.error(f"⚠️ High usage today ({units}) compared to avg ({round(avg,2)})")

else:
    st.info("Add data to start 🚀")
