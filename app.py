import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import random

# ------------------ PAGE ------------------
st.set_page_config(page_title="Electricity Dashboard", layout="wide")

# ------------------ INSTAGRAM STYLE UI ------------------
st.markdown("""
<style>
body {
    background-color: #fafafa;
}
.block-container {
    padding-top: 2rem;
}
.main-title {
    font-size: 32px;
    font-weight: 600;
}
.subtle {
    color: #8e8e8e;
}
.card {
    padding: 20px;
    border-radius: 10px;
    background-color: white;
    border: 1px solid #dbdbdb;
}
</style>
""", unsafe_allow_html=True)

# ------------------ SESSION ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ------------------ LOGIN ------------------
if not st.session_state.logged_in:

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="main-title">⚡ Electricity Detector</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtle">Smart Energy Monitoring System</p>', unsafe_allow_html=True)

        st.write("Track usage 📊")
        st.write("Detect anomalies 🧠")
        st.write("Predict bills 💰")

        # REALISTIC LOGO (clean style)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Lightning_icon.svg/512px-Lightning_icon.svg.png", width=120)

    with col2:
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

# ------------------ DASHBOARD ------------------
name = st.session_state.name
meter_id = st.session_state.meter_id

# Logout
colA, colB = st.columns([8,1])
with colB:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Header
st.markdown('<p class="main-title">⚡ Electricity Dashboard</p>', unsafe_allow_html=True)
st.markdown(f'<p class="subtle">User: {name} | Meter: {meter_id}</p>', unsafe_allow_html=True)

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
    if st.button("Simulate"):
        st.session_state.meter += random.uniform(0.5, 3.0)
    st.metric("Meter", round(st.session_state.meter, 2))

with col2:
    use_meter = st.checkbox("Use Meter")

    if use_meter:
        units = st.session_state.meter
    else:
        units = st.number_input("Units", min_value=0.0)

    if st.button("Add"):
        st.session_state.data.append(units)

with col3:
    if st.button("Reset"):
        st.session_state.data = []
        st.session_state.meter = 0

# ------------------ DATA ------------------
df = pd.DataFrame(st.session_state.data, columns=["Units"])

if not df.empty:

    df["Day"] = range(1, len(df)+1)

    avg = df["Units"].mean()
    bill = avg * 30 * COST_PER_UNIT

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Avg", round(avg, 2))
    c2.metric("Bill", f"₹ {round(bill, 2)}")
    c3.metric("Days", len(df))

    st.markdown("---")

    # Graph
    fig, ax = plt.subplots()
    ax.plot(df["Day"], df["Units"], marker="o")

    if len(df) > 5:
        model = IsolationForest(contamination=0.2, random_state=42)
        df["anomaly"] = model.fit_predict(df[["Units"]])
        anomalies = df[df["anomaly"] == -1]
        ax.scatter(anomalies["Day"], anomalies["Units"])

    st.pyplot(fig)

    st.markdown("---")

    # Table
    df["Cost"] = df["Units"] * COST_PER_UNIT
    st.dataframe(df)

    # Risky
    risky = df[df["Units"] > avg * 1.5]
    if not risky.empty:
        st.warning("⚠️ High usage detected")

    # AI
    if len(df) > 5:
        if not anomalies.empty:
            st.error("Anomalies found")
        else:
            st.success("Normal usage")

    # Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download", csv, "report.csv")

else:
    st.info("Start adding data 🚀")
