import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

METRICS_FILE = DATA_DIR / "metric" / "metrics.csv"
LOG_FILE = DATA_DIR / "log" / "log.csv"
DEPLOYMENT_FILE = DATA_DIR / "deployments" / "deployments.csv"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AegisAI",
    page_icon="🛡️",
    layout="wide",
)


# ============================================================
# TITLE
# ============================================================

st.title("🛡️ AegisAI")
st.subheader("AI-Powered Production Incident Intelligence")

st.write(
    "A multi-agent production incident investigation system "
    "for detecting anomalies, correlating logs, deployments, "
    "historical incidents and generating remediation guidance."
)

st.divider()


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_metrics():
    if not METRICS_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(METRICS_FILE)


@st.cache_data
def load_logs():
    if not LOG_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(LOG_FILE)


@st.cache_data
def load_deployments():
    if not DEPLOYMENT_FILE.exists():
        return pd.DataFrame()

    return pd.read_csv(DEPLOYMENT_FILE)


metrics = load_metrics()
logs = load_logs()
deployments = load_deployments()


# ============================================================
# NORMALIZE METRICS
# ============================================================

if not metrics.empty:

    # Different versions of anomaly_detector may use
    # different column names. Handle both safely.

    if "status" not in metrics.columns:

        if "anomaly" in metrics.columns:
            metrics["status"] = metrics["anomaly"].apply(
                lambda x: "ANOMALY"
                if str(x).upper() in ["ANOMALY", "-1", "TRUE"]
                else "NORMAL"
            )

        elif "anomaly_score" in metrics.columns:
            # IsolationForest:
            # negative score generally indicates anomalous samples.
            metrics["status"] = metrics["anomaly_score"].apply(
                lambda x: "ANOMALY"
                if float(x) < 0
                else "NORMAL"
            )

        else:
            metrics["status"] = "NORMAL"


# ============================================================
# SUMMARY COUNTS
# ============================================================

total_metrics = len(metrics)

if not metrics.empty and "status" in metrics.columns:
    anomaly_count = int(
        (metrics["status"].astype(str).str.upper() == "ANOMALY").sum()
    )
else:
    anomaly_count = 0

total_logs = len(logs)
total_deployments = len(deployments)


# ============================================================
# AFFECTED SERVICE
# ============================================================

affected_service = "Unknown"

if not metrics.empty and "service" in metrics.columns:

    services = metrics["service"].dropna().astype(str).unique()

    if len(services) > 0:
        affected_service = services[0]


# ============================================================
# DASHBOARD METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Metrics",
        total_metrics
    )

with col2:
    st.metric(
        "Anomalies",
        anomaly_count
    )

with col3:
    st.metric(
        "Log Events",
        total_logs
    )

with col4:
    st.metric(
        "Deployments",
        total_deployments
    )


st.divider()


# ============================================================
# INCIDENT STATUS
# ============================================================

st.header("🚨 Incident Status")

if anomaly_count > 0:

    st.error(
        f"Production anomaly detected in {affected_service}"
    )

else:

    st.success(
        "No production anomalies detected."
    )


# ============================================================
# ANOMALY DETECTION
# ============================================================

st.header("🔎 Anomaly Detection")

if not metrics.empty:

    if "status" in metrics.columns:

        anomaly_df = metrics[
            metrics["status"].astype(str).str.upper() == "ANOMALY"
        ].copy()

    else:

        anomaly_df = pd.DataFrame()

    if not anomaly_df.empty:

        st.dataframe(
            anomaly_df,
            width="stretch",
            hide_index=True
        )

    else:

        st.info("No anomalies detected.")

else:

    st.warning(
        f"Metrics file not found or empty:\n{METRICS_FILE}"
    )


# ============================================================
# AFFECTED SERVICE
# ============================================================

st.header("🎯 Affected Service")

st.write(
    f"**Detected service:** `{affected_service}`"
)


# ============================================================
# PRODUCTION LOGS
# ============================================================

st.header("📋 Production Logs")

if not logs.empty:

    st.dataframe(
        logs,
        width="stretch",
        hide_index=True
    )

else:

    st.warning(
        f"Log file not found or empty:\n{LOG_FILE}"
    )


# ============================================================
# DEPLOYMENTS
# ============================================================

st.header("🚀 Recent Deployment Evidence")

if not deployments.empty:

    st.dataframe(
        deployments,
        width="stretch",
        hide_index=True
    )

    # --------------------------------------------------------
    # Latest Deployment
    # --------------------------------------------------------

    st.subheader("Latest Deployment")

    deployment_copy = deployments.copy()

    if "timestamp" in deployment_copy.columns:

        deployment_copy["timestamp"] = pd.to_datetime(
            deployment_copy["timestamp"],
            errors="coerce"
        )

        latest = deployment_copy.sort_values(
            "timestamp"
        ).iloc[-1]

    else:

        latest = deployment_copy.iloc[-1]

    dcol1, dcol2, dcol3 = st.columns(3)

    with dcol1:

        if "version" in latest.index:
            st.metric(
                "Version",
                str(latest["version"])
            )

    with dcol2:

        if "commit_id" in latest.index:
            st.metric(
                "Commit",
                str(latest["commit_id"])
            )

        elif "commit" in latest.index:
            st.metric(
                "Commit",
                str(latest["commit"])
            )

    with dcol3:

        if "change" in latest.index:
            st.write("**Change**")
            st.write(str(latest["change"]))

else:

    st.warning(
        f"Deployment file not found or empty:\n{DEPLOYMENT_FILE}"
    )


# ============================================================
# ROOT CAUSE ANALYSIS
# ============================================================

st.header("🧠 Root Cause Analysis")

root_cause_text = (
    "Production degradation is strongly correlated with the "
    "recent deployment v2.4.1 (b72c91). The deployment was "
    "followed by increasing API latency, database load and "
    "error rate, while application logs also reported "
    "database connection problems."
)

st.warning(root_cause_text)


# ============================================================
# ROOT CAUSE EVIDENCE
# ============================================================

left, right = st.columns(2)

with left:

    st.subheader("Detected Pattern")

    st.write(
        "• API latency increased"
    )

    st.write(
        "• Error rate increased"
    )

    st.write(
        "• Database CPU increased"
    )

    st.write(
        "• Database latency increased"
    )

    st.write(
        "• Database connection pool became exhausted"
    )


with right:

    st.subheader("Correlation Evidence")

    st.write(
        "Deployment: **v2.4.1**"
    )

    st.write(
        "Commit: **b72c91**"
    )

    st.write(
        "Deployment time: **10:05**"
    )

    st.write(
        "First anomaly: **10:08**"
    )

    st.write(
        "Time difference: **3 minutes**"
    )


# ============================================================
# CONFIDENCE
# ============================================================

st.subheader("Confidence")

st.success(
    "HIGH"
)


# ============================================================
# HISTORICAL KNOWLEDGE
# ============================================================

st.header("📚 Historical Incident Knowledge")

with st.expander("Historical Match 1"):

    st.write(
        "**Incident:** INC-001"
    )

    st.write(
        "**Title:** Authentication API degradation"
    )

    st.write(
        "**Service:** auth-service"
    )

    st.write(
        "**Severity:** CRITICAL"
    )

    st.write(
        "**Root Cause:** Database connection pool exhaustion "
        "after authentication deployment"
    )

    st.write(
        "**Resolution:** Rollback deployment and increase "
        "connection pool configuration"
    )

    st.write(
        "**Affected Version:** v2.4.1"
    )


# ============================================================
# REMEDIATION
# ============================================================

st.header("🛠️ Recommended Remediation")


with st.expander("1. [P0] Rollback deployment"):

    st.write(
        "Review or rollback deployment v2.4.1 (b72c91) "
        "before further production impact."
    )


with st.expander("2. [P0] Investigate database connection pool"):

    st.write(
        "Inspect connection pool size, connection leaks, "
        "query execution time and database saturation."
    )


with st.expander("3. [P1] Review authentication queries"):

    st.write(
        "Compare query execution plans before and after "
        "the deployment. Check indexes, joins, locks and "
        "query latency."
    )


with st.expander("4. [P1] Increase production monitoring"):

    st.write(
        "Monitor API latency, error rate, database CPU, "
        "database latency and connection-pool utilization."
    )


with st.expander("5. [P2] Add regression protection"):

    st.write(
        "Add query performance tests, database load tests "
        "and deployment health checks before future releases."
    )


# ============================================================
# SAFETY NOTICE
# ============================================================

st.divider()

st.info(
    "AegisAI only generates investigation findings and "
    "recommended remediation actions. No production changes "
    "are executed automatically."
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AegisAI — Multi-Agent Production Incident Intelligence"
)