import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from streamlit_autorefresh import st_autorefresh
import psutil

# -----------------------------------
# PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="MedIntelOps Dashboard",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<div style='text-align:center; padding:20px;'>

<h1 style='color:white;'>
🏥 MedIntelOps Command Center
</h1>

<h4 style='color:#94A3B8;'>
Intelligent Medical AI Monitoring & Incident Intelligence Platform
</h4>

</div>
""", unsafe_allow_html=True)
# -----------------------------------
# AUTO REFRESH
# -----------------------------------

st_autorefresh(
    interval=5000,
    key="dashboard_refresh"
)

# -----------------------------------
# DATABASE LOADER
# -----------------------------------

def load_data():

    conn = sqlite3.connect(
        "database/logs.db"
    )

    df = pd.read_sql_query(
        "SELECT * FROM telemetry",
        conn
    )

    conn.close()

    return df

# -----------------------------------
# LOAD DATA
# -----------------------------------

data = load_data()

# -----------------------------------
# TITLE
# -----------------------------------

# -----------------------------------
# KPI CARDS
# -----------------------------------

total_requests = len(data)

anomalies = len(
    data[data["anomaly"] == "Anomaly"]
)

critical_incidents = len(
    data[data["severity"] == "Critical"]
)

health_score = round(
    data["reliability_score"].mean(),
    2
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Requests",
        total_requests
    )

with col2:
    st.metric(
        "Anomalies",
        anomalies
    )

with col3:
    st.metric(
        "Critical Incidents",
        critical_incidents
    )

with col4:
    st.metric(
        "System Health",
        f"{health_score}%"
    )

# -----------------------------------
# LIVE ALERTS
# -----------------------------------

st.subheader("🚨 Live Alerts")

critical_data = data[
    data["severity"] == "Critical"
]

if len(critical_data) > 0:

    for _, row in critical_data.iterrows():

        st.error(
            f"""
Critical Incident Detected

Request ID: {row['request_id']}

Reliability Score: {row['reliability_score']}%
"""
        )
else:

    st.success(
        "No critical incidents detected."
    )

# -----------------------------------
# ANOMALY GRAPH
# -----------------------------------

st.subheader("📊 Anomaly Detection Analysis")

fig1 = px.scatter(
    data,
    x="latency",
    y="tokens_used",
    color="anomaly",
    size="confidence",
    hover_data=["request_id"],
    title="Latency vs Token Usage"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

# -----------------------------------
# RELIABILITY TREND
# -----------------------------------

st.subheader("📈 Reliability Trend")

fig2 = px.line(
    data,
    x="request_id",
    y="reliability_score",
    markers=True,
    title="Reliability Score Trend"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# -----------------------------------
# SEVERITY DISTRIBUTION
# -----------------------------------

st.subheader("🚨 Severity Distribution")

severity_counts = (
    data["severity"]
    .value_counts()
    .reset_index()
)

severity_counts.columns = [
    "Severity",
    "Count"
]

fig3 = px.pie(
    severity_counts,
    names="Severity",
    values="Count",
    title="Incident Severity Distribution"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# -----------------------------------
# LOW RELIABILITY REQUESTS
# -----------------------------------

st.subheader("⚠️ Low Reliability Requests")

low_reliability = data[
    data["reliability_score"] < 70
]

if len(low_reliability) > 0:

    st.dataframe(
        low_reliability,
        use_container_width=True
    )

else:

    st.success(
        "No low reliability requests found."
    )

# -----------------------------------
# TELEMETRY LOGS
# -----------------------------------

st.subheader("📄 Telemetry Logs")

st.dataframe(
    data,
    use_container_width=True
)

# -----------------------------------
# ROOT CAUSE ANALYSIS
# -----------------------------------

if "root_cause" in data.columns:

    st.subheader("🧠 Root Cause Analysis")

    rca = data[
        data["anomaly"] == "Anomaly"
    ][[
        "request_id",
        "root_cause",
        "severity"
    ]]

    st.dataframe(
        rca,
        use_container_width=True
    )

# -----------------------------------
# AI EXPLANATIONS
# -----------------------------------

if "ai_explanation" in data.columns:

    st.subheader("🤖 AI Incident Explanations")

    incident_data = data[
        data["anomaly"] == "Anomaly"
    ]

    for _, row in incident_data.iterrows():

        st.info(
            f"""
Request ID: {row['request_id']}

Severity: {row['severity']}

AI Explanation:

{row['ai_explanation']}
"""
        )

# -----------------------------------
# RECOMMENDATIONS
# -----------------------------------

if "recommendation" in data.columns:

    st.subheader("💡 Recommended Actions")

    incident_data = data[
        data["anomaly"] == "Anomaly"
    ]

    for _, row in incident_data.iterrows():

        st.warning(
            f"""
Request ID: {row['request_id']}

Recommendation:

{row['recommendation']}
"""
        )

cpu = psutil.cpu_percent()

memory = psutil.virtual_memory().percent

col5, col6 = st.columns(2)

with col5:
    st.metric(
        "CPU Usage",
        f"{cpu}%"
    )

with col6:
    st.metric(
        "Memory Usage",
        f"{memory}%"
    )

resource_df = pd.DataFrame({
    "Metric":[
        "CPU",
        "Memory"
    ],
    "Usage":[
        cpu,
        memory
    ]
})

fig_resource = px.bar(
    resource_df,
    x="Metric",
    y="Usage",
    title="System Resource Utilization"
)

st.plotly_chart(
    fig_resource,
    use_container_width=True
)

throughput = len(data)

st.metric(
    "Request Throughput",
    throughput
)

error_rate = round(
    (
        data["error_status"].sum()
        /
        len(data)
    ) * 100,
    2
)

st.metric(
    "Error Rate",
    f"{error_rate}%"
)

# -----------------------------------
# GEMINI INCIDENT INTELLIGENCE
# -----------------------------------

st.subheader("🤖 Gemini Incident Intelligence")

try:

    with open(
        "datasets/incident_summary.txt",
        "r",
        encoding="utf-8"
    ) as f:

        summary = f.read()

    st.info(summary)

except FileNotFoundError:

    st.warning(
        "No Gemini summary available."
    )
