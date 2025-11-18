# AI-WiFence — AI-Powered Intrusion Detection System for Home WiFi

## Overview
Lightweight IDS that captures home network metadata, extracts per-device features, runs an IsolationForest model to detect anomalies, sends alerts via FastAPI, and shows a simple dashboard.

> Use only on networks you own. This program does not contain exploit code.

## Quick Start (local)
1. Create and activate venv:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
