import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import random

# ---------------- PAGE ----------------
st.set_page_config(page_title="Electricity Dashboard", layout="wide")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:

    left, right = st.columns([1.2, 1])

    with left:
        st.title("⚡ Electricity Detector")
        st.markdown("### Smart Energy Monitoring")

        st.write("• Track daily electricity usage")
        st.write("• Detect abnormal spikes")
        st.write("• Predict monthly bill")

        # CLEAN LOGO (simple SVG style)
        st.image("https://img.icons8.com/fluency/240/lightning-bolt.png", width=120)

    with right:
        st.markdown("### Login")

        name = st.text_input("Name")
        meter = st.text_input("Meter ID")

        if st.button("Login"):
            if name and meter:
                st.session_state.logged_in = True
                st.session_state.name = name
                st.session_state.meter = meter
                st.rerun()
            else:
                st.warning("Enter all details")

    st.stop()

# ---------------- DASHBOARD ----------------
name = st.session_state.name
meter = st.session_state.meter

# Logout
top1, top2 = st.columns([8,1])
with top2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.title("⚡ Electricity Dashboard")
st.caption(f"{name} • Meter: {meter}")

st.divider()

COST = 8

# ---------------- SESSION DATA ----------------
if "units" not in st.session_state:
    st.session_state.units = []

if "meter_val" not in st.session_state:
    st.session_state.meter_val = 0

# ---------------- INPUT ----------------
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Simulate"):
        st.session_state.meter_val += random.uniform(0.5, 3.0)
    st.metric("Meter", round(st.session_state.meter_val, 2))

with c2:
    use_meter = st.checkbox("Use meter")

    if use_meter:
        val = st.session_state.meter_val
    else:
        val = st.number_input("Units", 0.0)

    if st.button("Add"):
        st.session_state.units.append(val)

with c3:
    if st.button("Reset"):
        st.session_state.units = []
        st.session_state.meter_val = 0

st.divider()

# ---------------- DATA ----------------
df = pd.DataFrame(st.session_state.units, columns=["Units"])

if not df.empty:

    df["Day"] = range(1, len(df)+1)

    avg = df["Units"].mean()
    bill = avg * 30 * COST

    m1, m2, m3 = st.columns(3)
    m1.metric("Average", round(avg,2))
    m2.metric("Bill", f"₹ {round(bill,2)}")
    m3.metric("Days", len(df))

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
    df["Cost"] = df["Units"] * COST
    st.dataframe(df)

    # SIMPLE ALERT
    if avg > 10:
        st.warning("⚠️ High average usage")

    # AI RESULT
    if len(df) > 5:
        if not anomalies.empty:
            st.error("Anomalies detected")
        else:
            st.success("Normal usage")

    # DOWNLOAD
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report", csv, "report.csv")

else:
    st.info("Add data to begin")
