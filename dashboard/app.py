from pathlib import Path
import sys
import textwrap

import pandas as pd
import streamlit as st
import plotly.express as px


# ============================================================
# AEGISAI - PRODUCTION INCIDENT INTELLIGENCE DASHBOARD
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AegisAI | Incident Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HTML RENDER HELPER
# ============================================================

def render_html(content):
    st.markdown(
        textwrap.dedent(content),
        unsafe_allow_html=True
    )


# ============================================================
# CUSTOM CSS
# ============================================================

render_html(
    """
    <style>

    .stApp {
        background: #0b0f14;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, h4 {
        letter-spacing: -0.3px;
    }

    section[data-testid="stSidebar"] {
        background: #10151d;
        border-right: 1px solid #202733;
    }

    .sidebar-brand {
        padding: 10px 4px 22px 4px;
    }

    .sidebar-title {
        font-size: 22px;
        font-weight: 700;
        color: #f4f7fb;
    }

    .sidebar-subtitle {
        font-size: 12px;
        color: #8c98a8;
        line-height: 1.5;
        margin-top: 6px;
    }

    .sidebar-section {
        color: #8c98a8;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 20px;
        margin-bottom: 8px;
        font-weight: 700;
    }

    .sidebar-stat {
        background: #151b24;
        border: 1px solid #252e3b;
        border-radius: 8px;
        padding: 9px 11px;
        margin-bottom: 7px;
        color: #dbe3ed;
        font-size: 13px;
    }

    .hero {
        padding: 4px 0 22px 0;
    }

    .hero-title {
        font-size: 36px;
        font-weight: 750;
        color: #f5f7fa;
        margin-bottom: 3px;
    }

    .hero-subtitle {
        color: #8995a6;
        font-size: 14px;
    }

    .metric-card {
        background: #111720;
        border: 1px solid #252e3a;
        border-radius: 10px;
        padding: 18px 20px;
        min-height: 105px;
    }

    .metric-label {
        color: #8e9aaa;
        font-size: 12px;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #f5f7fa;
        font-size: 28px;
        font-weight: 700;
    }

    .metric-description {
        color: #687587;
        font-size: 11px;
        margin-top: 5px;
    }

    .incident-card {
        background: #131a22;
        border: 1px solid #394554;
        border-radius: 12px;
        padding: 20px 22px;
        margin-top: 5px;
        margin-bottom: 20px;
    }

    .incident-card.incident {
        border-left: 4px solid #d94a4a;
    }

    .incident-card.healthy {
        border-left: 4px solid #35b56b;
    }

    .incident-title {
        color: #f2f5f8;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .incident-detail {
        color: #aab5c3;
        font-size: 13px;
        margin: 5px 0;
    }

    .status-badge {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }

    .status-danger {
        color: #ffb4b4;
        background: #321c21;
        border: 1px solid #66313a;
    }

    .status-success {
        color: #a8e6bf;
        background: #173024;
        border: 1px solid #285f40;
    }

    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #f0f3f7;
        margin-top: 28px;
        margin-bottom: 12px;
    }

    .evidence-card {
        background: #111820;
        border: 1px solid #26313e;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }

    .evidence-title {
        color: #e5ebf2;
        font-weight: 650;
        font-size: 15px;
        margin-bottom: 8px;
    }

    .evidence-text {
        color: #9da9b8;
        font-size: 13px;
        line-height: 1.65;
    }

    .root-cause {
        background: #121c27;
        border: 1px solid #29435e;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 14px;
    }

    .root-cause-title {
        color: #e9f1f8;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .root-cause-text {
        color: #aeb9c7;
        line-height: 1.7;
        font-size: 13px;
    }

    .confidence {
        display: inline-block;
        margin-top: 12px;
        padding: 5px 10px;
        border-radius: 6px;
        background: #173224;
        color: #9be0b7;
        border: 1px solid #2b6544;
        font-size: 11px;
        font-weight: 700;
    }

    .remediation {
        background: #141b23;
        border: 1px solid #303b48;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 10px;
    }

    .remediation-number {
        color: #91b8df;
        font-weight: 700;
        margin-right: 8px;
    }

    .remediation-text {
        color: #c2cad4;
        font-size: 13px;
        line-height: 1.6;
    }

    .footer {
        text-align: center;
        color: #586575;
        font-size: 11px;
        padding: 30px 0 10px 0;
    }

    </style>
    """
)


# ============================================================
# DATA LOADERS
# ============================================================

@st.cache_data
def load_metrics():

    path = PROJECT_ROOT / "data" / "metric" / "metrics.csv"

    if not path.exists():
        path = PROJECT_ROOT / "data" / "metrics" / "metrics.csv"

    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


@st.cache_data
def load_logs():

    path = PROJECT_ROOT / "data" / "log" / "log.csv"

    if not path.exists():
        path = PROJECT_ROOT / "data" / "logs" / "logs.csv"

    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


@st.cache_data
def load_deployments():

    path = PROJECT_ROOT / "data" / "deployments" / "deployments.csv"

    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


# ============================================================
# ANOMALY DETECTION
# ============================================================

def detect_anomalies(metrics):

    if metrics.empty:
        return pd.DataFrame()

    try:
        from sklearn.ensemble import IsolationForest
    except ImportError:
        return pd.DataFrame()

    feature_columns = [
        "cpu_percent",
        "memory_percent",
        "request_count",
        "avg_latency_ms",
        "error_rate",
        "db_cpu_percent",
        "db_latency_ms",
    ]

    available = [
        column
        for column in feature_columns
        if column in metrics.columns
    ]

    if len(available) < 2 or len(metrics) < 5:
        return pd.DataFrame()

    working = metrics.copy()

    for column in available:
        working[column] = pd.to_numeric(
            working[column],
            errors="coerce"
        )

    working = working.dropna(subset=available)

    if len(working) < 5:
        return pd.DataFrame()

    model = IsolationForest(
        contamination=0.30,
        random_state=42
    )

    predictions = model.fit_predict(
        working[available]
    )

    scores = model.decision_function(
        working[available]
    )

    working["anomaly_prediction"] = predictions
    working["anomaly_score"] = scores

    anomalies = working[
        working["anomaly_prediction"] == -1
    ].copy()

    anomalies = anomalies.sort_values("timestamp")

    return anomalies


# ============================================================
# CORRELATION
# ============================================================

def correlate_logs(logs, first_anomaly):

    if logs.empty or first_anomaly is None:
        return pd.DataFrame()

    logs = logs.copy()

    if "timestamp" not in logs.columns:
        return pd.DataFrame()

    start = first_anomaly - pd.Timedelta(minutes=3)
    end = first_anomaly + pd.Timedelta(minutes=3)

    relevant = logs[
        (logs["timestamp"] >= start)
        & (logs["timestamp"] <= end)
    ].copy()

    return relevant.sort_values("timestamp")


def correlate_deployments(deployments, first_anomaly):

    if deployments.empty or first_anomaly is None:
        return pd.DataFrame()

    deployments = deployments.copy()

    if "timestamp" not in deployments.columns:
        return pd.DataFrame()

    window_start = first_anomaly - pd.Timedelta(hours=2)

    relevant = deployments[
        (deployments["timestamp"] <= first_anomaly)
        & (deployments["timestamp"] >= window_start)
    ].copy()

    return relevant.sort_values("timestamp")


# ============================================================
# ROOT CAUSE
# ============================================================

def generate_root_cause(
    anomalies,
    relevant_logs,
    relevant_deployments
):

    if anomalies.empty:

        return {
            "service": "N/A",
            "first_anomaly": None,
            "root_cause": "No production anomaly detected.",
            "confidence": "LOW",
        }

    first = anomalies.iloc[0]

    service = first.get(
        "service",
        "unknown"
    )

    first_anomaly = first["timestamp"]

    deployment_text = (
        "No recent deployment was correlated."
    )

    confidence = "MEDIUM"

    if not relevant_deployments.empty:

        latest = relevant_deployments.iloc[-1]

        deployment_time = latest["timestamp"]

        minutes_before = (
            first_anomaly - deployment_time
        ).total_seconds() / 60

        version = latest.get(
            "version",
            "unknown"
        )

        commit = latest.get(
            "commit_id",
            "unknown"
        )

        deployment_text = (
            f"Production degradation is strongly correlated "
            f"with deployment {version} ({commit}). "
            f"The deployment occurred "
            f"{minutes_before:.2f} minutes before the "
            f"first anomaly."
        )

        confidence = "HIGH"

    if not relevant_logs.empty:

        log_messages = []

        for _, row in relevant_logs.iterrows():

            level = str(
                row.get("level", "")
            ).upper()

            message = str(
                row.get("message", "")
            ).lower()

            if (
                level in [
                    "ERROR",
                    "CRITICAL",
                    "WARN",
                    "WARNING"
                ]
                or "database" in message
                or "timeout" in message
            ):
                log_messages.append(message)

        if log_messages:

            database_related = any(
                (
                    "database" in message
                    or "connection" in message
                    or "timeout" in message
                )
                for message in log_messages
            )

            if database_related:

                deployment_text += (
                    " Application logs show database "
                    "connection-pool and timeout failures."
                )

                confidence = "HIGH"

    return {
        "service": service,
        "first_anomaly": first_anomaly,
        "root_cause": deployment_text,
        "confidence": confidence,
    }


# ============================================================
# REMEDIATION
# ============================================================

def generate_remediation(
    root_cause,
    relevant_deployments
):

    recommendations = []

    if not relevant_deployments.empty:

        latest = relevant_deployments.iloc[-1]

        version = latest.get(
            "version",
            "recent deployment"
        )

        recommendations.append(
            f"Review deployment {version} and compare "
            "database-query behavior before and after release."
        )

    recommendations.extend(
        [
            "Inspect database connection-pool configuration "
            "and current pool utilization.",

            "Review slow authentication queries and database "
            "execution plans introduced by the recent change.",

            "Temporarily reduce database pressure and monitor "
            "authentication latency and timeout rate.",

            "Validate the remediation in a staging environment "
            "before production rollout.",

            "Add an alert for connection-pool saturation and "
            "authentication timeout spikes.",
        ]
    )

    return recommendations


# ============================================================
# LOAD DATA
# ============================================================

metrics = load_metrics()
logs = load_logs()
deployments = load_deployments()

anomalies = detect_anomalies(metrics)

first_anomaly = None

if not anomalies.empty:
    first_anomaly = anomalies.iloc[0]["timestamp"]

relevant_logs = correlate_logs(
    logs,
    first_anomaly
)

relevant_deployments = correlate_deployments(
    deployments,
    first_anomaly
)

analysis = generate_root_cause(
    anomalies,
    relevant_logs,
    relevant_deployments
)

remediation = generate_remediation(
    analysis,
    relevant_deployments
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html(
        """
        <div class="sidebar-brand">
            <div class="sidebar-title">🛡️ AegisAI</div>

            <div class="sidebar-subtitle">
                Production incident investigation
                and root-cause intelligence.
            </div>
        </div>
        """
    )

    st.divider()

    render_html(
        """
        <div class="sidebar-section">
            System Status
        </div>
        """
    )

    if not anomalies.empty:

        render_html(
            """
            <div class="status-badge status-danger">
                ● INCIDENT DETECTED
            </div>
            """
        )

    else:

        render_html(
            """
            <div class="status-badge status-success">
                ● SYSTEM HEALTHY
            </div>
            """
        )

    render_html(
        """
        <div class="sidebar-section">
            Platform Metrics
        </div>
        """
    )

    render_html(
        f"""
        <div class="sidebar-stat">
            Metrics&nbsp;&nbsp;: <b>{len(metrics)}</b>
        </div>

        <div class="sidebar-stat">
            Logs&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <b>{len(logs)}</b>
        </div>

        <div class="sidebar-stat">
            Deployments : <b>{len(deployments)}</b>
        </div>

        <div class="sidebar-stat">
            Anomalies&nbsp;&nbsp;: <b>{len(anomalies)}</b>
        </div>
        """
    )

    render_html(
        """
        <div class="sidebar-section">
            Engine
        </div>
        """
    )

    st.caption("ML Anomaly Detection")
    st.caption("Log Correlation")
    st.caption("Deployment Correlation")
    st.caption("Root Cause Analysis")
    st.caption("Remediation Intelligence")


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="hero-title">
            🛡️ AegisAI
        </div>

        <div class="hero-subtitle">
            Autonomous AI-Powered Production Incident
            Intelligence Platform
        </div>

    </div>
    """
)


# ============================================================
# PRODUCTION OVERVIEW
# ============================================================

render_html(
    """
    <div class="section-title">
        📊 Production Overview
    </div>
    """
)

affected_service = "N/A"

if not anomalies.empty and "service" in anomalies.columns:

    services = anomalies["service"].dropna().unique()

    if len(services) > 0:
        affected_service = str(services[0])


c1, c2, c3, c4, c5 = st.columns(5)


with c1:

    render_html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Total Metrics
            </div>

            <div class="metric-value">
                {len(metrics)}
            </div>

            <div class="metric-description">
                Production observations
            </div>

        </div>
        """
    )


with c2:

    render_html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Anomalies
            </div>

            <div class="metric-value">
                {len(anomalies)}
            </div>

            <div class="metric-description">
                ML detected anomalies
            </div>

        </div>
        """
    )


with c3:

    render_html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Log Events
            </div>

            <div class="metric-value">
                {len(logs)}
            </div>

            <div class="metric-description">
                Application events
            </div>

        </div>
        """
    )


with c4:

    render_html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Deployments
            </div>

            <div class="metric-value">
                {len(deployments)}
            </div>

            <div class="metric-description">
                Recent releases
            </div>

        </div>
        """
    )


with c5:

    render_html(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Affected Service
            </div>

            <div
                class="metric-value"
                style="font-size:21px;"
            >
                {affected_service}
            </div>

            <div class="metric-description">
                Impacted production service
            </div>

        </div>
        """
    )


# ============================================================
# INCIDENT STATUS
# ============================================================

render_html(
    """
    <div class="section-title">
        🚨 Incident Status
    </div>
    """
)

if not anomalies.empty:

    first_time_text = (
        first_anomaly.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        if first_anomaly is not None
        else "Unknown"
    )

    render_html(
        f"""
        <div class="incident-card incident">

            <div class="status-badge status-danger">
                INCIDENT DETECTED
            </div>

            <div class="incident-title">
                Production degradation detected
            </div>

            <div class="incident-detail">
                <b>Service:</b> {affected_service}
            </div>

            <div class="incident-detail">
                <b>First anomaly:</b> {first_time_text}
            </div>

            <div class="incident-detail">
                <b>Anomalies detected:</b> {len(anomalies)}
            </div>

        </div>
        """
    )

else:

    render_html(
        """
        <div class="incident-card healthy">

            <div class="status-badge status-success">
                SYSTEM HEALTHY
            </div>

            <div class="incident-title">
                No production incident detected
            </div>

            <div class="incident-detail">
                Current production metrics are within
                the detected baseline.
            </div>

        </div>
        """
    )


# ============================================================
# DETECTED ANOMALIES
# ============================================================

if not anomalies.empty:

    render_html(
        """
        <div class="section-title">
            🔎 Detected Anomalies
        </div>
        """
    )

    display_columns = [
        "timestamp",
        "service",
        "avg_latency_ms",
        "error_rate",
        "db_cpu_percent",
        "db_latency_ms",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in anomalies.columns
    ]

    anomaly_table = anomalies[
        available_columns
    ].copy()

    if "timestamp" in anomaly_table.columns:

        anomaly_table["timestamp"] = (
            anomaly_table["timestamp"]
            .dt.strftime("%Y-%m-%d %H:%M:%S")
        )

    rename_map = {
        "timestamp": "Timestamp",
        "service": "Service",
        "avg_latency_ms": "Latency (ms)",
        "error_rate": "Error Rate (%)",
        "db_cpu_percent": "DB CPU (%)",
        "db_latency_ms": "DB Latency (ms)",
    }

    anomaly_table = anomaly_table.rename(
        columns=rename_map
    )

    st.dataframe(
        anomaly_table,
        width="stretch",
        hide_index=True
    )


# ============================================================
# PRODUCTION METRICS
# ============================================================

if not metrics.empty:

    render_html(
        """
        <div class="section-title">
            📈 Production Metrics
        </div>
        """
    )

    chart_left, chart_right = st.columns(2)

    chart_data = metrics.copy()


    # --------------------------------------------------------
    # LATENCY
    # --------------------------------------------------------

    with chart_left:

        if {
            "timestamp",
            "avg_latency_ms"
        }.issubset(chart_data.columns):

            fig = px.line(
                chart_data,
                x="timestamp",
                y="avg_latency_ms",
                markers=True,
                title="Average Latency",
                labels={
                    "timestamp": "Time",
                    "avg_latency_ms": "Latency (ms)",
                }
            )

            fig.update_layout(
                template="plotly_dark",
                height=340,
                margin=dict(
                    l=10,
                    r=10,
                    t=45,
                    b=10
                ),
                paper_bgcolor="#0b0f14",
                plot_bgcolor="#0b0f14",
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


    # --------------------------------------------------------
    # ERROR RATE
    # --------------------------------------------------------

    with chart_right:

        if {
            "timestamp",
            "error_rate"
        }.issubset(chart_data.columns):

            fig = px.line(
                chart_data,
                x="timestamp",
                y="error_rate",
                markers=True,
                title="Error Rate",
                labels={
                    "timestamp": "Time",
                    "error_rate": "Error Rate (%)",
                }
            )

            fig.update_layout(
                template="plotly_dark",
                height=340,
                margin=dict(
                    l=10,
                    r=10,
                    t=45,
                    b=10
                ),
                paper_bgcolor="#0b0f14",
                plot_bgcolor="#0b0f14",
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


    chart_left, chart_right = st.columns(2)


    # --------------------------------------------------------
    # DATABASE CPU
    # --------------------------------------------------------

    with chart_left:

        if {
            "timestamp",
            "db_cpu_percent"
        }.issubset(chart_data.columns):

            fig = px.line(
                chart_data,
                x="timestamp",
                y="db_cpu_percent",
                markers=True,
                title="Database CPU",
                labels={
                    "timestamp": "Time",
                    "db_cpu_percent": "DB CPU (%)",
                }
            )

            fig.update_layout(
                template="plotly_dark",
                height=340,
                margin=dict(
                    l=10,
                    r=10,
                    t=45,
                    b=10
                ),
                paper_bgcolor="#0b0f14",
                plot_bgcolor="#0b0f14",
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


    # --------------------------------------------------------
    # DATABASE LATENCY
    # --------------------------------------------------------

    with chart_right:

        if {
            "timestamp",
            "db_latency_ms"
        }.issubset(chart_data.columns):

            fig = px.line(
                chart_data,
                x="timestamp",
                y="db_latency_ms",
                markers=True,
                title="Database Latency",
                labels={
                    "timestamp": "Time",
                    "db_latency_ms": "DB Latency (ms)",
                }
            )

            fig.update_layout(
                template="plotly_dark",
                height=340,
                margin=dict(
                    l=10,
                    r=10,
                    t=45,
                    b=10
                ),
                paper_bgcolor="#0b0f14",
                plot_bgcolor="#0b0f14",
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )


# ============================================================
# ROOT CAUSE ANALYSIS
# ============================================================

render_html(
    """
    <div class="section-title">
        🧠 Root Cause Analysis
    </div>
    """
)

render_html(
    f"""
    <div class="root-cause">

        <div class="root-cause-title">
            Most Likely Root Cause
        </div>

        <div class="root-cause-text">
            {analysis["root_cause"]}
        </div>

        <div class="confidence">
            CONFIDENCE: {analysis["confidence"]}
        </div>

    </div>
    """
)


# ============================================================
# DEPLOYMENT EVIDENCE
# ============================================================

render_html(
    """
    <div class="section-title">
        🚀 Deployment Evidence
    </div>
    """
)

if not relevant_deployments.empty:

    for _, deployment in relevant_deployments.iterrows():

        deployment_time = deployment.get(
            "timestamp",
            "Unknown"
        )

        if hasattr(
            deployment_time,
            "strftime"
        ):

            deployment_time = deployment_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        version = deployment.get(
            "version",
            "Unknown"
        )

        commit = deployment.get(
            "commit_id",
            "Unknown"
        )

        developer = deployment.get(
            "developer",
            "Unknown"
        )

        change = deployment.get(
            "change",
            "Unknown"
        )

        minutes_before = ""

        if first_anomaly is not None:

            try:

                diff = (
                    first_anomaly
                    - deployment["timestamp"]
                ).total_seconds() / 60

                minutes_before = (
                    f"{diff:.2f} minutes before first anomaly"
                )

            except Exception:
                pass

        render_html(
            f"""
            <div class="evidence-card">

                <div class="evidence-title">
                    Deployment {version}
                </div>

                <div class="evidence-text">

                    <b>Time:</b> {deployment_time}<br>

                    <b>Commit:</b> {commit}<br>

                    <b>Developer:</b> {developer}<br>

                    <b>Change:</b> {change}<br>

                    <b>Correlation:</b> {minutes_before}

                </div>

            </div>
            """
        )

else:

    st.info(
        "No correlated deployments found."
    )


# ============================================================
# APPLICATION LOG EVIDENCE
# ============================================================

render_html(
    """
    <div class="section-title">
        📋 Application Log Evidence
    </div>
    """
)

if not relevant_logs.empty:

    log_display = relevant_logs.copy()

    if "timestamp" in log_display.columns:

        log_display["timestamp"] = (
            log_display["timestamp"]
            .dt.strftime("%Y-%m-%d %H:%M:%S")
        )

    preferred_columns = [
        "timestamp",
        "service",
        "level",
        "message",
    ]

    available_columns = [
        column
        for column in preferred_columns
        if column in log_display.columns
    ]

    log_display = log_display[
        available_columns
    ]

    st.dataframe(
        log_display,
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "No correlated application logs found."
    )


# ============================================================
# REMEDIATION
# ============================================================

render_html(
    """
    <div class="section-title">
        🛠️ Recommended Remediation
    </div>
    """
)

for index, recommendation in enumerate(
    remediation,
    start=1
):

    render_html(
        f"""
        <div class="remediation">

            <span class="remediation-number">
                {index:02d}
            </span>

            <span class="remediation-text">
                {recommendation}
            </span>

        </div>
        """
    )


# ============================================================
# INCIDENT SUMMARY
# ============================================================

render_html(
    """
    <div class="section-title">
        📌 Investigation Summary
    </div>
    """
)

summary_left, summary_right = st.columns(2)


with summary_left:

    render_html(
        f"""
        <div class="evidence-card">

            <div class="evidence-title">
                Investigation Coverage
            </div>

            <div class="evidence-text">

                Metrics analyzed:
                <b>{len(metrics)}</b><br>

                ML anomalies:
                <b>{len(anomalies)}</b><br>

                Relevant logs:
                <b>{len(relevant_logs)}</b><br>

                Relevant deployments:
                <b>{len(relevant_deployments)}</b>

            </div>

        </div>
        """
    )


with summary_right:

    status = (
        "INCIDENT_DETECTED"
        if not anomalies.empty
        else "HEALTHY"
    )

    render_html(
        f"""
        <div class="evidence-card">

            <div class="evidence-title">
                Incident Context
            </div>

            <div class="evidence-text">

                Affected service:
                <b>{affected_service}</b><br>

                Investigation confidence:
                <b>{analysis["confidence"]}</b><br>

                Status:
                <b>{status}</b>

            </div>

        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

render_html(
    """
    <div class="footer">

        AegisAI — Multi-Agent Production Incident Intelligence

        <br>

        ML Detection • Log Correlation • Deployment Analysis
        • Root Cause Intelligence • Remediation

    </div>
    """
)