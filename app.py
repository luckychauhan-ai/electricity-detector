import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import random

# ------------------ PAGE ------------------
st.set_page_config(page_title="Electricity Dashboard", layout="wide")

# ------------------ SESSION ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------ LOGIN SCREEN ------------------
if not st.session_state.logged_in:

    col1, col2 = st.columns(2)

    # LEFT SIDE
    with col1:
        st.title("⚡ Electricity Detector")
        st.subheader("Smart Energy Monitoring System")

        st.write("📊 Track daily usage")
        st.write("🧠 Detect anomalies using AI")
        st.write("💰 Predict electricity bill")
        st.write("💡 Save energy efficiently")

        # Better logo 
st.markdown("""
<h1 style="text-align:center; color:#00bcd4;">
⚡ Electricity Detector
</h1>
""", unsafe_allow_html=True)    
    
      # RIGHT SIDE
    with col2:
        st.subheader("🔐 Login")

        name = st.text_input("Enter Name")
        meter_id = st.text_input("Meter ID")

        if st.button("Login"):
            if name and meter_id:
                st.session_state.logged_in = True
                st.session_state.name = name
                st.session_state.meter_id = meter_id
                st.rerun()
            else:
                st.warning("Please fill all details")

    st.stop()

# ------------------ DASHBOARD ------------------
name = st.session_state.name
meter_id = st.session_state.meter_id

# Logout button
colA, colB = st.columns([6,1])
with colB:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Header
st.title("⚡ Electricity Bill Anomaly Detector")
st.success(f"Welcome {name} 👋")
st.info(f"Meter ID: {meter_id}")

st.markdown("---")

COST_PER_UNIT = 8

# ------------------ SESSION ------------------
if "meter" not in st.session_state:
    st.session_state.meter = 0

if "data" not in st.session_state:
    st.session_state.data = []

# ------------------ INPUT ------------------
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

st.markdown("---")

# ------------------ DATA ------------------
df = pd.DataFrame(st.session_state.data, columns=["Units"])

if not df.empty:

    df["Day"] = range(1, len(df)+1)

    avg = df["Units"].mean()
    predicted_bill = avg * 30 * COST_PER_UNIT

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Average Usage", round(avg, 2))
    c2.metric("Predicted Bill", f"₹ {round(predicted_bill, 2)}")
    c3.metric("Total Days", len(df))

    st.markdown("---")

    # Graph
    st.subheader("📈 Usage Trend")

    fig, ax = plt.subplots()
    ax.plot(df["Day"], df["Units"], marker="o")

    if len(df) > 5:
        model = IsolationForest(contamination=0.2, random_state=42)
        df["anomaly"] = model.fit_predict(df[["Units"]])
        anomalies = df[df["anomaly"] == -1]
        ax.scatter(anomalies["Day"], anomalies["Units"])

    st.pyplot(fig)

    st.markdown("---")

    # Cost
    df["Cost"] = df["Units"] * COST_PER_UNIT
    st.subheader("💸 Cost Table")
    st.dataframe(df)

    # Peak
    max_day = df.loc[df["Units"].idxmax()]
    st.success(f"🔥 Highest Usage: Day {int(max_day['Day'])}")

    # Risky
    st.subheader("⚠️ Risky Days")
    risky = df[df["Units"] > avg * 1.5]

    if not risky.empty:
        st.warning(risky)
    else:
        st.info("No risky days")

    # AI
    st.subheader("🧠 AI Detection")

    if len(df) > 5:
        if not anomalies.empty:
            st.error("Anomalies Detected")
            st.dataframe(anomalies)
        else:
            st.success("No anomalies")
    else:
        st.warning("Add at least 6 days")

    st.markdown("---")

    # Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Report", csv, "report.csv")

else:
    st.info("Add data to start 🚀")
