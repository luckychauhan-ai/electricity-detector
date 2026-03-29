import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import random

# ---------------- PAGE ----------------
st.set_page_config(page_title="Electricity Dashboard", layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}
.stButton>button {
    width: 100%;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    left, right = st.columns([1.2, 1])

    with left:
        st.title("⚡ Electricity Detector")
        st.caption("Smart Energy Monitoring System")

        st.write("• Track daily usage")
        st.write("• Detect anomalies using AI")
        st.write("• Predict electricity bill")

        # CLEAN LOGO
        st.image("https://img.icons8.com/color/240/electricity.png", width=140)

    with right:
        st.markdown("### Login")

        name = st.text_input("Name")
        meter_id = st.text_input("Meter ID")

        if st.button("Login"):
            if name and meter_id:
                st.session_state.logged_in = True
                st.session_state.name = name
                st.session_state.meter_id = meter_id
                st.rerun()
            else:
                st.warning("Enter all details")

    st.stop()

# ---------------- DASHBOARD ----------------
name = st.session_state.name
meter_id = st.session_state.meter_id

# Logout
top1, top2 = st.columns([8,1])
with top2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.title("⚡ Electricity Dashboard")
st.caption(f"{name} • Meter ID: {meter_id}")

st.divider()

COST_PER_UNIT = 8

# ---------------- SESSION DATA ----------------
if "meter" not in st.session_state:
    st.session_state.meter = 0

if "data" not in st.session_state:
    st.session_state.data = []

# ---------------- INPUT ----------------
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Simulate Usage"):
        st.session_state.meter += random.uniform(0.5, 3.0)
    st.metric("Meter Reading", round(st.session_state.meter, 2))

with c2:
    use_meter = st.checkbox("Use Virtual Meter")

    units = st.session_state.meter if use_meter else st.number_input("Units", 0.0)

    if st.button("Add Data"):
        st.session_state.data.append(units)

with c3:
    if st.button("Reset"):
        st.session_state.data = []
        st.session_state.meter = 0

st.divider()

# ---------------- DATA ----------------
df = pd.DataFrame(st.session_state.data, columns=["Units"])

if not df.empty:

    df["Day"] = range(1, len(df)+1)

    avg = df["Units"].mean()
    predicted_bill = avg * 30 * COST_PER_UNIT

    # METRICS
    m1, m2, m3 = st.columns(3)
    m1.metric("Average Usage", round(avg, 2))
    m2.metric("Predicted Bill", f"₹ {round(predicted_bill, 2)}")
    m3.metric("Total Days", len(df))

    st.divider()

    # GRAPH
    fig, ax = plt.subplots()
    ax.plot(df["Day"], df["Units"], marker="o")

    if len(df) > 5:
        model = IsolationForest(contamination=0.2, random_state=42)
        df["anomaly"] = model.fit_predict(df[["Units"]])
        anomalies = df[df["anomaly"] == -1]
        ax.scatter(anomalies["Day"], anomalies["Units"])

    st.pyplot(fig)

    st.divider()

    # TABLE
    df["Cost"] = df["Units"] * COST_PER_UNIT
    st.dataframe(df)

    # PEAK
    max_day = df.loc[df["Units"].idxmax()]
    st.success(f"🔥 Highest Usage: Day {int(max_day['Day'])}")

    # RISKY
    risky = df[df["Units"] > avg * 1.5]
    if not risky.empty:
        st.warning("⚠️ High usage detected")

    # AI
    if len(df) > 5:
        if not anomalies.empty:
            st.error("Anomalies detected")
        else:
            st.success("Normal usage")

    # DOWNLOAD
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report", csv, "report.csv")

else:
    st.info("Add data to start 🚀")
