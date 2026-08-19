import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import psutil
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import json

# ------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------

st.markdown("""
<style>
.block-container{
    max-width: 95%;
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(
    page_title="MedIntelOps Command Center",
    page_icon="🏥",
    layout="wide"
)

# ------------------------------------------------
# AUTO REFRESH
# ------------------------------------------------

st_autorefresh(
    interval=5000,
    key="refresh"
)

# ------------------------------------------------
# DATABASE LOADER
# ------------------------------------------------

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

def load_unified_incident(request_id):

    conn = sqlite3.connect(
        "database/logs.db"
    )

    telemetry = pd.read_sql_query(
        """
        SELECT *
        FROM telemetry
        WHERE request_id = ?
        """,
        conn,
        params=(request_id,)
    )

    shap = pd.read_sql_query(
        """
        SELECT *
        FROM shap_explanations
        WHERE request_id = ?
        """,
        conn,
        params=(request_id,)
    )

    rag = pd.read_sql_query(
        """
        SELECT *
        FROM rag_analysis
        WHERE request_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        conn,
        params=(request_id,)
    )

    conn.close()

    return telemetry, shap, rag

# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

data = load_data()

# ------------------------------------------------
# BASIC METRICS
# ------------------------------------------------

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

trust_score = min(
    round(health_score + 8, 2),
    100
)

if trust_score > 100:
    trust_score = 100

avg_latency = round(
    data["latency"].mean(),
    2
)

cpu = psutil.cpu_percent()

memory = psutil.virtual_memory().percent

# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------

with st.sidebar:

    st.title("🏥 MedIntelOps")

    st.metric(
        "System Health",
        f"{health_score}%"
    )

    st.metric(
        "Active Incidents",
        anomalies
    )

    st.metric(
        "Critical Alerts",
        critical_incidents
    )

    st.metric(
        "CPU Usage",
        f"{cpu}%"
    )

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.markdown("""
<div style='text-align:center;padding:15px;'>

<h1>
🏥 MedIntelOps Command Center
</h1>

<h4 style='color:#94A3B8;'>
Intelligent Medical AI Monitoring & Incident Intelligence Platform
</h4>

</div>
""", unsafe_allow_html=True)

# ------------------------------------------------
# SYSTEM STATUS
# ------------------------------------------------

if health_score >= 85:
    st.success("🟢 System Status: Operational")

elif health_score >= 70:
    st.warning("🟡 System Status: Warning")

else:
    st.error("🔴 System Status: Critical")

# ------------------------------------------------
# TABS
# ------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "📊 Monitoring",
    "🚨 Incident Center",
    "📄 Telemetry"
])

# ==================================================
# MONITORING TAB
# ==================================================

with tab1:

# ==================================================
# SYSTEM HEALTH OVERVIEW
# ==================================================

    st.markdown("### 🖥️ System Health Overview")

    total_requests = len(data)

    avg_latency = round(
        data["latency"].mean(),
        3
    )

    avg_reliability = round(
        data["reliability_score"].mean(),
        2
    )

    total_anomalies = len(
        data[
            data["anomaly"] == "Anomaly"
        ]
    )

    system_health = round(
        (
            len(
                data[
                    data["decision_class"].isin(
                        ["Normal", "Monitor"]
                    )
                ]
            )
            / total_requests
        ) * 100,
        2
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric(
            "Total Requests",
            total_requests
        )

    with m2:
        st.metric(
            "Avg Latency",
            f"{avg_latency}s"
        )

    with m3:
        st.metric(
            "Avg Reliability",
            f"{avg_reliability}%"
        )

    with m4:
        st.metric(
            "Anomalies",
            total_anomalies
        )

    with m5:
        st.metric(
            "System Health",
            f"{system_health}%"
        )

    st.divider()


# ==================================================
# SYSTEM PERFORMANCE TRENDS
# ==================================================

    st.markdown("### 📈 System Performance Trends")

    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:

        fig_latency = px.line(
            data,
            x="request_id",
            y="latency",
            markers=False,
            title="Inference Latency"
        )

        fig_latency.update_layout(
            height=350,
            xaxis_title="Request ID",
            yaxis_title="Latency (seconds)"
        )

        st.plotly_chart(
            fig_latency,
            use_container_width=True
        )


    with trend_col2:

        fig_reliability = px.line(
            data,
            x="request_id",
            y="reliability_score",
            markers=False,
            title="Reliability Trend"
        )

        fig_reliability.update_layout(
            height=350,
            xaxis_title="Request ID",
            yaxis_title="Reliability (%)"
        )

        st.plotly_chart(
            fig_reliability,
            use_container_width=True
        )

    st.divider()


# ==================================================
# ANOMALY MONITORING
# ==================================================

    st.markdown("### 🔎 Anomaly Monitoring")

    anomaly_data = (
        data["anomaly"]
        .value_counts()
        .reset_index()
    )

    anomaly_data.columns = [
        "Status",
        "Count"
    ]

    fig_anomaly = px.bar(
        anomaly_data,
        x="Status",
        y="Count",
        text="Count",
        title="Normal vs Anomalous Requests"
    )

    fig_anomaly.update_layout(
        height=350,
        xaxis_title="Request Status",
        yaxis_title="Number of Requests"
    )

    fig_anomaly.update_traces(
        textposition="outside"
    )

    st.plotly_chart(
        fig_anomaly,
        use_container_width=True
    )

    st.divider()

# ==================================================
# INCIDENT HEALTH SUMMARY
# ==================================================

    st.markdown("### 🚦 Incident Health Summary")

    decision_counts = (
        data["decision_class"]
        .value_counts()
    )

    decision_summary = pd.DataFrame({
        "Decision": [
            "Critical",
            "Investigate",
            "Monitor",
            "Normal"
        ],
        "Count": [
            decision_counts.get("Critical", 0),
            decision_counts.get("Investigate", 0),
            decision_counts.get("Monitor", 0),
            decision_counts.get("Normal", 0)
        ]
    })

    fig_health = px.pie(
        decision_summary,
        names="Decision",
        values="Count",
        title="Incident Classification"
    )

    fig_health.update_layout(
        height=400
    )

    st.plotly_chart(
        fig_health,
        use_container_width=True
    )

    st.divider()


    # KPI CARDS
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric("🏥 Health Score", f"{health_score}%")

    with k2:
        st.metric("🤖 Trust Score", f"{trust_score}%")

    with k3:
        st.metric("🚨 Incidents", anomalies)

    with k4:
        st.metric("⚡ Avg Latency", f"{avg_latency}s")

    st.divider()

    # ROW 1
    left, right = st.columns(2)

    with left:

        st.subheader("🤖 AI Intelligence")

        st.success(f"""
🟢 Monitoring Active

Health Score: {health_score}%

Trust Score: {trust_score}%

Active Incidents: {anomalies}

Critical Alerts: {critical_incidents}
""")

        st.subheader("📊 System Snapshot")

        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric(
                "Critical Incidents",
                critical_incidents
            )

        with s2:
            st.metric(
                "Total Anomalies",
                anomalies
            )

        with s3:
            st.metric(
                "System Reliability",
                f"{health_score}%"
            )

        st.subheader("⚡ Quick Insights")

        st.info(f"""
• Health Score: {health_score}%

• Trust Score: {trust_score}%

• Average Latency: {avg_latency}s

• Monitoring Status: ACTIVE
""")

    with right:

        st.subheader("📈 Reliability Trend")

        fig_reliability = px.line(
            data,
            x="request_id",
            y="reliability_score",
            markers=True
        )

        fig_reliability.update_layout(
            height=300,
            showlegend=False
        )

        st.plotly_chart(
            fig_reliability,
            use_container_width=True
        )

    st.divider()

    # ROW 2
    left, right = st.columns(2)

    with left:

        st.subheader(
            "🚨 Severity Distribution"
        )

        severity_counts = (
            data["severity"]
            .value_counts()
            .reset_index()
        )

        severity_counts.columns = [
            "Severity",
            "Count"
        ]

        fig_severity = px.pie(
            severity_counts,
            names="Severity",
            values="Count",
            hole=0.6
        )

        st.plotly_chart(
            fig_severity,
            use_container_width=True
        )

    with right:

        st.subheader(
            "🤖 AI Incident Intelligence"
        )

        try:

            with open(
                "datasets/incident_summary.txt",
                "r",
                encoding="utf-8"
            ) as f:

                summary = f.read()

            st.info(summary)

        except:

            st.warning(
                "No AI incident summary available."
            )

        st.metric(
            "AI Analysis Status",
            "ACTIVE"
        )

    st.divider()

    # ROW 3
    left, right = st.columns(2)

    with left:

        st.subheader(
            "🏥 System Overview"
        )

        overview = pd.DataFrame({
            "Metric": [
                "Health Score",
                "Trust Score",
                "Active Incidents",
                "Critical Alerts",
                "Average Latency"
            ],
            "Value": [
                f"{health_score}%",
                f"{trust_score}%",
                anomalies,
                critical_incidents,
                f"{avg_latency}s"
            ]
        })

        st.dataframe(
            overview,
            use_container_width=True,
            hide_index=True
        )

    with right:

        st.subheader(
            "🖥 Resource Monitoring"
        )

        st.metric(
            "CPU Usage",
            f"{cpu}%"
        )

        st.progress(
            min(int(cpu), 100)
        )

        st.metric(
            "Memory Usage",
            f"{memory}%"
        )

        st.progress(
            min(int(memory), 100)
        )

    st.divider()

    st.subheader("🚨 Live Alerts")

    critical_data = data[
        data["severity"] == "Critical"
    ]

    if len(critical_data) > 0:

        for _, row in critical_data.iterrows():

            st.error(
                f"Request ID: {row['request_id']} | Severity: {row['severity']} | Reliability: {row['reliability_score']}%"
            )

    else:

        st.success(
            "No critical alerts detected."
        )
        
with tab2:

    # ==================================================
# INCIDENT DECISION OVERVIEW
# ==================================================

    st.markdown("### 🚦 Incident Decision Overview")

    decision_counts = (
    data["decision_class"]
    .value_counts()
)

    critical_count = decision_counts.get("Critical", 0)
    investigate_count = decision_counts.get("Investigate", 0)
    monitor_count = decision_counts.get("Monitor", 0)
    normal_count = decision_counts.get("Normal", 0)

    d1, d2, d3, d4 = st.columns(4)

    with d1:
        st.metric(
        "🔴 Critical",
        critical_count
    )

    with d2:
        st.metric(
        "🟠 Investigate",
        investigate_count
    )

    with d3:
        st.metric(
        "🟡 Monitor",
        monitor_count
    )

    with d4:
        st.metric(
        "🟢 Normal",
        normal_count
    )

    st.divider()

    # ==================================================
# INCIDENT DECISION DISTRIBUTION
# ==================================================

    st.markdown("### 📊 Decision Distribution")

    decision_chart = pd.DataFrame({
    "Decision": [
        "Critical",
        "Investigate",
        "Monitor",
        "Normal"
    ],
    "Count": [
        critical_count,
        investigate_count,
        monitor_count,
        normal_count
    ]
})

    fig_decision = px.bar(
        decision_chart,
        x="Decision",
        y="Count",
        text="Count"
)

    fig_decision.update_layout(
        height=350,
        xaxis_title="Incident Classification",
        yaxis_title="Number of Requests"
)

    fig_decision.update_traces(
        textposition="outside"
)

    st.plotly_chart(
        fig_decision,
        use_container_width=True
)

    st.divider()


    # ==================================================
# INCIDENT PRIORITY QUEUE
# ==================================================

    st.markdown("### 🚨 Incident Priority Queue")

    priority_order = {
    "Critical": 1,
    "Investigate": 2,
    "Monitor": 3,
    "Normal": 4
}

    priority_data = data.copy()

    priority_data["priority"] = (
    priority_data["decision_class"]
    .map(priority_order)
)

    priority_data = priority_data.sort_values(
    ["priority", "final_hallucination_score"],
    ascending=[True, False]
)

    incident_queue = priority_data[
    [
        "request_id",
        "decision_class",
        "decision_action",
        "severity",
        "final_hallucination_score",
        "evidence_score",
        "nli_contradiction",
        "reliability_score"
    ]
].head(20)

    st.dataframe(
    incident_queue,
    use_container_width=True,
    hide_index=True
)

    st.caption(
    "Showing the 20 highest-priority incidents based on automated decision classification."
)

    st.divider()


    st.subheader(
        "🤖 Gemini Incident Intelligence"
    )

    try:

        with open(
            "datasets/incident_summary.txt",
            "r",
            encoding="utf-8"
        ) as f:

            summary = f.read()

        st.markdown("## 🤖 AI Incident Intelligence")

        st.info(summary)

    except:

        st.warning(
            "No Gemini incident summary found."
        )

    st.divider()

    # --------------------------------------------
    # CRITICAL INCIDENT FEED
    # --------------------------------------------

    st.subheader(
        "🚨 Critical Incident Feed"
    )

    critical_data = data[
        data["severity"] == "Critical"
    ]

    if len(critical_data) > 0:

        for _, row in critical_data.iterrows():

         st.markdown(f"""
### 🚨 Incident #{row['request_id']}

**Severity:** {row['severity']}

**Reliability Score:** {row['reliability_score']}%

**Latency:** {row['latency']} sec

**Tokens Used:** {row['tokens_used']}
""")

        st.divider()

    else:

        st.success(
            "No critical incidents detected."
        )

    st.divider()

    # --------------------------------------------
    # ACTIVE ANOMALIES
    # --------------------------------------------

    st.subheader(
        "⚠ Active Anomalies"
    )

    anomaly_data = data[
        data["anomaly"] == "Anomaly"
    ]

    if len(anomaly_data) > 0:

        for _, row in anomaly_data.iterrows():

            st.warning(
                f"""
Request ID:
{row['request_id']}

Reliability:
{row['reliability_score']}%

Latency:
{row['latency']} sec

Confidence:
{row['confidence']}
"""
            )

    else:

        st.success(
            "No anomalies detected."
        )

    st.divider()

    # --------------------------------------------
    # INCIDENT SUMMARY
    # --------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Critical Incidents",
            critical_incidents
        )

    with col2:

        st.metric(
            "Total Anomalies",
            anomalies
        )

    with col3:

        st.metric(
            "System Reliability",
            f"{health_score}%"
        )
# ==================================================
# INCIDENT INTELLIGENCE — RAG / SHAP / HALLUCINATION
# ==================================================
    st.divider()
      # ==================================================
    # RAG INCIDENT INTELLIGENCE
    # ==================================================

    st.subheader("🧠 RAG Incident Intelligence")

    st.caption(
        "Grounded incident analysis using similar historical "
        "incidents retrieved from MedIntelOps memory."
    )

    # --------------------------------------------------
    # LOAD AVAILABLE RAG ANALYSES
    # --------------------------------------------------

    rag_conn = sqlite3.connect(
        "database/logs.db"
    )

    rag_data = pd.read_sql_query(
        """
        SELECT
            id,
            request_id,
            incident_assessment,
            likely_root_cause,
            historical_pattern,
            recommended_actions,
            expected_outcome,
            evidence_request_ids,
            confidence,
            retrieved_incidents,
            generated_at
        FROM rag_analysis
        ORDER BY id DESC
        """,
        rag_conn
    )

    rag_conn.close()

    if not rag_data.empty:

        # --------------------------------------------------
        # Keep only latest analysis for each request
        # --------------------------------------------------

        latest_rag = (
            rag_data
            .drop_duplicates(
                subset=["request_id"],
                keep="first"
            )
        )

        available_requests = (
            latest_rag["request_id"]
            .tolist()
        )

        selected_rag_request = st.selectbox(
            "Select incident for RAG analysis",
            available_requests,
            key="rag_incident_selector"
        )

        selected_rag = latest_rag[
            latest_rag["request_id"]
            == selected_rag_request
        ].iloc[0]

        # ==================================================
        # INCIDENT INFORMATION
        # ==================================================

        incident_match = data[
            data["request_id"]
            == selected_rag_request
        ]

        if not incident_match.empty:

            incident_row = (
                incident_match.iloc[0]
            )

            rag_col1, rag_col2, rag_col3, rag_col4 = (
                st.columns(4)
            )

            with rag_col1:

                st.metric(
                    "Request ID",
                    selected_rag_request
                )

            with rag_col2:

                st.metric(
                    "Severity",
                    incident_row["severity"]
                )

            with rag_col3:

                st.metric(
                    "Reliability",
                    f"{float(incident_row['reliability_score']):.2f}%"
                )

            with rag_col4:

                st.metric(
                    "Latency",
                    f"{float(incident_row['latency']):.3f}s"
                )

        st.divider()

        # ==================================================
        # AI ASSESSMENT + ROOT CAUSE
        # ==================================================

        assessment_col, cause_col = st.columns(2)

        with assessment_col:

            st.markdown(
                "### 🔎 Incident Assessment"
            )

            st.info(
                selected_rag[
                    "incident_assessment"
                ]
            )

        with cause_col:

            st.markdown(
                "### 🎯 Likely Root Cause"
            )

            st.warning(
                selected_rag[
                    "likely_root_cause"
                ]
            )

        # ==================================================
        # HISTORICAL PATTERN
        # ==================================================

        st.markdown(
            "### 🔁 Historical Pattern"
        )

        st.write(
            selected_rag[
                "historical_pattern"
            ]
        )

        st.divider()

        # ==================================================
        # RETRIEVED HISTORICAL EVIDENCE
        # ==================================================

        st.markdown(
            "### 🔗 Retrieved Historical Evidence"
        )

        try:

            retrieved_incidents = json.loads(
                selected_rag[
                    "retrieved_incidents"
                ]
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            retrieved_incidents = []

        if retrieved_incidents:

            evidence_columns = st.columns(
                min(
                    len(retrieved_incidents),
                    5
                )
            )

            for index, incident in enumerate(
                retrieved_incidents[:5]
            ):

                with evidence_columns[index]:

                    request_id = incident.get(
                        "request_id",
                        "N/A"
                    )

                    similarity = float(
                        incident.get(
                            "similarity_score",
                            0
                        )
                    )

                    st.metric(
                        f"Request {request_id}",
                        f"{similarity * 100:.2f}%"
                    )

            st.caption(
                "Scores represent semantic vector similarity "
                "between operational incident patterns. "
                "They are not probabilities."
            )

        else:

            st.info(
                "No retrieved historical evidence "
                "is available for this analysis."
            )

        st.divider()

        # ==================================================
        # RECOMMENDED ACTIONS
        # ==================================================

        action_col, outcome_col = st.columns(2)

        with action_col:

            st.markdown(
                "### 🛠 Recommended Actions"
            )

            try:

                recommended_actions = json.loads(
                    selected_rag[
                        "recommended_actions"
                    ]
                )

            except (
                json.JSONDecodeError,
                TypeError
            ):

                recommended_actions = []

            if recommended_actions:

                for action_number, action in enumerate(
                    recommended_actions,
                    start=1
                ):

                    st.write(
                        f"**{action_number}.** {action}"
                    )

            else:

                st.write(
                    "No recommendations available."
                )

        with outcome_col:

            st.markdown(
                "### 📈 Expected Outcome"
            )

            st.success(
                selected_rag[
                    "expected_outcome"
                ]
            )

        # ==================================================
        # ANALYSIS METADATA
        # ==================================================

        st.divider()

        confidence_col, generated_col = (
            st.columns(2)
        )

        with confidence_col:

            st.metric(
                "AI Analysis Confidence",
                selected_rag[
                    "confidence"
                ]
            )

        with generated_col:

            st.metric(
                "Analysis Generated",
                str(
                    selected_rag[
                        "generated_at"
                    ]
                )
            )

        st.caption(
            "RAG analysis is grounded in retrieved synthetic "
            "historical incident records and is intended for "
            "operational AI-system monitoring."
        )

    else:

        st.warning(
            "No RAG incident analyses are available yet."
        )

        st.caption(
            "Run backend/rag_gemini_analyzer.py "
            "to generate an analysis."
        )

    st.divider()


    # ==========================================
    # EXPLAINABLE AI — SHAP
    # ==========================================

    st.subheader("🧠 Explainable AI — Anomaly Analysis")

    st.caption(
        "Understand which telemetry factors influenced "
        "the anomaly detection model."
    )

    shap_conn = sqlite3.connect(
        "database/logs.db"
    )

    shap_data = pd.read_sql_query(
        """
        SELECT
            request_id,
            predicted_anomaly,
            anomaly_probability,
            latency_shap,
            tokens_used_shap,
            confidence_shap,
            error_status_shap,
            strongest_feature,
            strongest_contribution,
            explanation_text
        FROM shap_explanations
        ORDER BY request_id
        """,
        shap_conn
    )

    shap_conn.close()

    if not shap_data.empty:

        anomalous_shap = shap_data[
            shap_data["predicted_anomaly"] == 1
        ]

        if not anomalous_shap.empty:

            selected_request = st.selectbox(
                "Select an anomalous request",
                anomalous_shap["request_id"].tolist(),
                key="shap_request_selector"
            )

            selected_shap = anomalous_shap[
                anomalous_shap["request_id"]
                == selected_request
            ].iloc[0]

            # ==========================================
            # SHAP KPI CARDS
            # ==========================================

            shap_col1, shap_col2, shap_col3 = st.columns(3)

            with shap_col1:

                st.metric(
                    "Anomaly Probability",
                    f"{selected_shap['anomaly_probability'] * 100:.1f}%"
                )

            with shap_col2:

                feature_name = (
                    str(selected_shap["strongest_feature"])
                    .replace("_", " ")
                    .title()
                )

                st.metric(
                    "Strongest Factor",
                    feature_name
                )

            with shap_col3:

                contribution = float(
                    selected_shap[
                        "strongest_contribution"
                    ]
                )

                st.metric(
                    "SHAP Contribution",
                    f"{contribution:+.3f}"
                )

            # ==========================================
            # EXPLANATION
            # ==========================================

            st.info(
                selected_shap["explanation_text"]
            )

            # ==========================================
            # SHAP CONTRIBUTION DATA
            # ==========================================

            shap_features = [
                "Latency",
                "Token Usage",
                "Confidence",
                "Error Status"
            ]

            shap_values = [
                selected_shap["latency_shap"],
                selected_shap["tokens_used_shap"],
                selected_shap["confidence_shap"],
                selected_shap["error_status_shap"]
            ]

            shap_chart_data = pd.DataFrame({
                "Feature": shap_features,
                "SHAP Value": shap_values
            })

            shap_chart_data[
                "Absolute Impact"
            ] = shap_chart_data[
                "SHAP Value"
            ].abs()

            shap_chart_data = (
                shap_chart_data
                .sort_values(
                    "Absolute Impact",
                    ascending=True
                )
            )

            # ==========================================
            # SHAP WATERFALL-STYLE CHART
            # ==========================================

            colors = [
                "#ef4444" if value > 0
                else "#22c55e"
                for value in shap_chart_data[
                    "SHAP Value"
                ]
            ]

            fig_shap = go.Figure()

            fig_shap.add_trace(
                go.Bar(
                    x=shap_chart_data[
                        "SHAP Value"
                    ],
                    y=shap_chart_data[
                        "Feature"
                    ],
                    orientation="h",
                    marker_color=colors,
                    text=[
                        f"{value:+.3f}"
                        for value in shap_chart_data[
                            "SHAP Value"
                        ]
                    ],
                    textposition="outside"
                )
            )

            fig_shap.add_vline(
                x=0,
                line_width=1
            )

            fig_shap.update_layout(
                title=(
                    f"Feature Contributions — "
                    f"Request {selected_request}"
                ),
                xaxis_title="SHAP Contribution",
                yaxis_title="",
                height=380,
                showlegend=False,
                margin=dict(
                    l=20,
                    r=40,
                    t=60,
                    b=40
                )
            )

            st.plotly_chart(
                fig_shap,
                use_container_width=True
            )

            st.caption(
                "Positive SHAP values push the model toward "
                "an anomaly prediction. Negative values push "
                "the prediction toward normal behaviour."
            )

        else:

            st.success(
                "The SHAP model currently predicts no anomalous requests."
            )

    else:

        st.warning(
            "No SHAP explanations are available. "
            "Run backend/shap_anomaly.py first."
        )
    st.divider()

    st.subheader("🧠 Hallucination Intelligence")

    hall_conn = sqlite3.connect(
        "database/logs.db"
    )

    hall_data = pd.read_sql_query(
        """
        SELECT
            request_id,
            hallucination_score,
            hallucination_risk,
            hallucination_type,
            evidence_score,
            supported_claims,
            unsupported_claims,
            contradicted_claims,
            final_hallucination_score,
            final_hallucination_risk,
            nli_contradiction,
            nli_entailment,
            nli_neutral
        FROM telemetry
        ORDER BY request_id
        """,
        hall_conn
    )

    hall_conn.close()

    # ==================================================
    # FINAL HALLUCINATION INTELLIGENCE — KPI CARDS
    # ==================================================

    avg_final_hall = round(
        hall_data["final_hallucination_score"].mean(),
        3
    )

    avg_evidence = round(
        hall_data["evidence_score"].mean(),
        3
    )

    critical_final = len(
        hall_data[
            hall_data["final_hallucination_risk"] == "Critical"
        ]
    )

    high_final = len(
        hall_data[
            hall_data["final_hallucination_risk"] == "High"
        ]
    )

    final_hall_rate = round(
        (
            len(
                hall_data[
                    hall_data["final_hallucination_score"] >= 0.20
                ]
            )
            / len(hall_data)
        ) * 100,
        2
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "Hallucination Rate",
            f"{final_hall_rate}%"
        )

    with c2:

        st.metric(
            "Avg Final Score",
            avg_final_hall
        )

    with c3:

        st.metric(
            "Avg Evidence",
            avg_evidence
        )

    with c4:

        st.metric(
            "Critical Risk",
            critical_final
        )
    # ==================================================
    # RISK DISTRIBUTION
    # ==================================================

    st.markdown("### 📊 Hallucination Risk Distribution")

    risk_counts = (
        hall_data["hallucination_risk"]
        .value_counts()
        .reindex(
            [
                "Low",
                "Medium",
                "High",
                "Critical"
            ],
            fill_value=0
        )
    )

    fig_risk = px.bar(

        x=risk_counts.index,

        y=risk_counts.values,

        labels={

            "x": "Risk Level",

            "y": "Number of Requests"

        },

        color=risk_counts.index,

        text=risk_counts.values

    )

    fig_risk.update_layout(

        height=420,

        showlegend=False

    )

    st.plotly_chart(

        fig_risk,

        use_container_width=True

    )

    # ==================================================
    # HALLUCINATION TYPE PIE CHART
    # ==================================================

    st.markdown("### 🥧 Hallucination Type Distribution")

    type_counts = (
        hall_data["hallucination_type"]
        .value_counts()
    )

    fig_type = px.pie(

        values=type_counts.values,

        names=type_counts.index,

        hole=0.45

    )

    fig_type.update_layout(

        height=450

    )

    st.plotly_chart(

        fig_type,

        use_container_width=True

    )

    # ==================================================
    # TOP HIGH RISK REQUESTS
    # ==================================================

    st.markdown("### 🚨 Highest Hallucination Risk Requests")

    high_risk = hall_data.sort_values(
        "hallucination_score",
        ascending=False
    ).head(10)

    st.dataframe(

        high_risk[
            [
                "request_id",
                "hallucination_score",
                "hallucination_risk",
                "hallucination_type",
                "evidence_score"
            ]
        ],

        use_container_width=True,

        hide_index=True

    )

    # ==================================================
    # EVIDENCE SCORE TREND
    # ==================================================

    st.markdown("### 📈 Evidence Score Trend")

    fig_evidence = px.line(

        hall_data,

        x="request_id",

        y="evidence_score",

        markers=True

    )

    fig_evidence.update_layout(

        height=400,

        xaxis_title="Request ID",

        yaxis_title="Evidence Score"

    )

    st.plotly_chart(

        fig_evidence,

        use_container_width=True

    )

    # ==================================================
    # FINAL HALLUCINATION SCORE TREND
    # ==================================================

    st.markdown("### 📉 Final Hallucination Score Trend")

    fig_hall = px.line(

        hall_data,

        x="request_id",

        y="final_hallucination_score",

        markers=True

    )

    fig_hall.update_layout(

        height=400,

        xaxis_title="Request ID",

        yaxis_title="Final Hallucination Score"

    )

    st.plotly_chart(

        fig_hall,

        use_container_width=True

    )

    # ==================================================
    # CRITICAL HALLUCINATIONS
    # ==================================================

    st.markdown("### 🔴 Critical Hallucination Feed")

    critical_rows = hall_data[
        hall_data["final_hallucination_risk"] == "Critical"
    ]

    if len(critical_rows) > 0:

        for _, row in critical_rows.iterrows():

            st.error(
    f"""
    Request ID: {row['request_id']}

    Final Hallucination Score: {row['final_hallucination_score']:.3f}

    Final Risk: {row['final_hallucination_risk']}

    Evidence Score: {row['evidence_score']}

    NLI Contradiction: {row['nli_contradiction']:.3f}

    NLI Entailment: {row['nli_entailment']:.3f}

    NLI Neutral: {row['nli_neutral']:.3f}

    Type: {row['hallucination_type']}
    """
            )

    else:

        st.success(
            "No critical hallucinations detected."
        )


    # ==================================================
    # UNIFIED INCIDENT INTELLIGENCE
    # ==================================================

    st.divider()

    st.subheader("🧠 Unified Incident Intelligence")

    st.caption(
        "Combines telemetry, SHAP explainability, "
        "hallucination analysis, RAG retrieval, and Gemini reasoning."
    )

    # ------------------------------------------
    # INCIDENT SELECTOR
    # ------------------------------------------

    incident_ids = (
        data["request_id"]
        .dropna()
        .astype(int)
        .sort_values()
        .tolist()
    )

    selected_incident = st.selectbox(
        "Select Incident",
        incident_ids,
        index=incident_ids.index(214)
        if 214 in incident_ids else 0,
        key="unified_incident_selector"
    )

    telemetry_u, shap_u, rag_u = load_unified_incident(
        selected_incident
    )

    # ------------------------------------------
    # TELEMETRY
    # ------------------------------------------

    if not telemetry_u.empty:

        incident = telemetry_u.iloc[0]

        st.markdown("### 🚨 Incident Overview")

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.metric(
                "Severity",
                incident["severity"]
            )

        with c2:
            st.metric(
                "Latency",
                f"{incident['latency']:.3f} sec"
            )

        with c3:
            st.metric(
                "Reliability",
                f"{incident['reliability_score']:.2f}%"
            )

        with c4:
            st.metric(
                "Model Confidence",
                f"{incident['confidence']:.3f}"
            )
        with c5:
            st.metric(
            "Decision",
            incident["decision_class"]
        )
    # ------------------------------------------
    # AUTOMATED INCIDENT DECISION
    # ------------------------------------------

    st.markdown("### 🚦 Automated Incident Decision")

    decision = incident["decision_class"]
    action = incident["decision_action"]
    reason = incident["decision_reason"]

    if decision == "Critical":

        st.error(
            f"🔴 {action}\n\n{reason}"
        )

    elif decision == "Investigate":

        st.warning(
            f"🟠 {action}\n\n{reason}"
        )

    elif decision == "Monitor":

        st.info(
            f"🟡 {action}\n\n{reason}"
        )

    else:

        st.success(
            f"🟢 {action}\n\n{reason}"
        )

    # ------------------------------------------
    # HALLUCINATION INTELLIGENCE
    # ------------------------------------------

    st.markdown("### 🩺 Medical Response Trustworthiness")

    h1, h2, h3, h4 = st.columns(4)

    with h1:
        st.metric(
            "Final Hallucination Score",
            f"{incident['final_hallucination_score']:.3f}"
        )

    with h2:
        st.metric(
            "Hallucination Risk",
            incident["final_hallucination_risk"]
        )

    with h3:
        st.metric(
            "Evidence Score",
            f"{incident['evidence_score']:.2f}"
        )

    with h4:
        st.metric(
            "NLI Contradiction",
            f"{incident['nli_contradiction']:.3f}"
        )

    # ------------------------------------------
    # SHAP EXPLANATION
    # ------------------------------------------

    if not shap_u.empty:

        shap_row = shap_u.iloc[0]

        st.markdown("### 🔎 Why Was This Incident Anomalous?")

        s1, s2, s3 = st.columns(3)

        with s1:
            st.metric(
                "Anomaly Probability",
                f"{shap_row['anomaly_probability'] * 100:.1f}%"
            )

        with s2:
            feature_name = (
                str(shap_row["strongest_feature"])
                .replace("_", " ")
                .title()
            )

            st.metric(
                "Strongest Factor",
                feature_name
            )

        with s3:
            st.metric(
                "SHAP Contribution",
                f"{float(shap_row['strongest_contribution']):+.3f}"
            )

        st.info(
            shap_row["explanation_text"]
        )

    # ------------------------------------------
    # RAG + GEMINI
    # ------------------------------------------

    if not rag_u.empty:

        rag = rag_u.iloc[0]

        st.markdown("### 🤖 RAG + Gemini Incident Intelligence")

        st.markdown("#### Incident Assessment")

        st.info(
            rag["incident_assessment"]
        )

        st.markdown("#### Likely Root Cause")

        st.warning(
            rag["likely_root_cause"]
        )

        st.markdown("#### Historical Pattern")

        st.write(
            rag["historical_pattern"]
        )

        st.markdown("#### Recommended Actions")

        try:

            actions = json.loads(
                rag["recommended_actions"]
            )

            for action in actions:

                st.success(
                    f"✓ {action}"
                )

        except:

            st.write(
                rag["recommended_actions"]
            )

        st.markdown("#### Expected Outcome")

        st.info(
            rag["expected_outcome"]
        )

        st.caption(
            f"Gemini Confidence: {rag['confidence']}"
        )

    else:

        st.warning(
            "No RAG/Gemini analysis is available for this incident."
        )

with tab3:


# ==================================================
# TELEMETRY SUMMARY
# ==================================================

    st.markdown("### 📋 Telemetry Summary")

    total_records = len(data)

    successful_requests = len(
    data[data["error_status"] == 0]
    )

    failed_requests = len(
    data[data["error_status"] != 0]
    )

    avg_latency = round(
        data["latency"].mean(),
        3
    )

    avg_tokens = round(
        data["tokens_used"].mean(),
        0
    )

    t1, t2, t3, t4, t5 = st.columns(5)

    with t1:
        st.metric(
            "Total Records",
            total_records
        )

    with t2:
        st.metric(
            "Successful",
            successful_requests
        )

    with t3:
        st.metric(
            "Failed",
            failed_requests
        )

    with t4:
        st.metric(
            "Avg Latency",
            f"{avg_latency}s"
        )

    with t5:
        st.metric(
            "Avg Tokens",
            int(avg_tokens)
        )

    st.divider()

    st.subheader(
        "📄 Telemetry Logs"
    )

    search = st.text_input(
        "Search Request ID"
    )

    if search:

        filtered = data[
            data["request_id"]
            .astype(str)
            .str.contains(
                search,
                case=False
            )
        ]

        st.dataframe(
            filtered,
            use_container_width=True
        )

    else:

        st.dataframe(
            data,
            use_container_width=True
        )

    st.divider()

    # --------------------------------------------
    # LOW RELIABILITY REQUESTS
    # --------------------------------------------

    st.subheader(
        "⚠ Low Reliability Requests"
    )

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

    st.divider()

    # --------------------------------------------
    # DATA SUMMARY
    # --------------------------------------------

    st.subheader(
        "📊 Dataset Summary"
    )

    summary_df = pd.DataFrame({
        "Metric":[
            "Total Requests",
            "Anomalies",
            "Critical Incidents",
            "Average Latency",
            "Average Reliability"
        ],
        "Value":[
            total_requests,
            anomalies,
            critical_incidents,
            round(
                data["latency"].mean(),
                2
            ),
            round(
                data["reliability_score"].mean(),
                2
            )
        ]
    })

    st.dataframe(
        summary_df,
        use_container_width=True
    )
st.divider()

st.markdown("""
<div style='text-align:center;
padding:10px;
color:#94A3B8;'>

MedIntelOps v1.0

AI-Powered Medical LLM Monitoring &
Incident Intelligence Platform

</div>
""", unsafe_allow_html=True)