# AegisAI

## AI-Powered Production Incident Investigation & Root Cause Analysis

AegisAI is an intelligent production incident investigation system that combines Machine Learning, multi-agent investigation, log analysis, deployment correlation, and an AI Incident Copilot to identify the likely root cause of production failures.

---
## 🚀 Live Demo

https://aegisai-incident-intelligence.streamlit.app/

## 🚀 What AegisAI Does

AegisAI analyzes production telemetry from multiple sources:

- Application metrics
- Application logs
- Deployment history
- Database performance indicators

It then:

1. Detects abnormal production behavior using Machine Learning
2. Identifies the affected service
3. Correlates anomalies with application logs
4. Correlates incidents with recent deployments
5. Generates a root-cause explanation
6. Provides an AI Incident Copilot for natural-language investigation

---

## 🧠 System Architecture

```text
                    ┌──────────────────────┐
                    │   Production Data   │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
        Metrics CSV        Logs CSV       Deployments CSV
             │                 │                 │
             ▼                 ▼                 ▼
      ┌────────────┐    ┌────────────┐    ┌───────────────┐
      │ ML Anomaly │    │ Log Agent  │    │ Deployment    │
      │ Detector   │    │            │    │ Agent         │
      └─────┬──────┘    └─────┬──────┘    └──────┬────────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               ▼
                    ┌────────────────────┐
                    │ Investigation Agent│
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Root Cause Analysis│
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Incident Copilot   │
                    └──────────┬─────────┘
                               │
                               ▼
                    ┌────────────────────┐
                    │ Streamlit Dashboard│
                    └────────────────────┘
