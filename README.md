# 🔍 CompliNet

### Network Configuration Drift Detection & Compliance Tool

**CompliNet** is a lightweight network automation tool designed to detect **configuration drift** and **compliance issues** on routers and switches.

It periodically collects device configurations and uses **static analysis** to compare them against Git-managed approved baselines and YAML-based compliance rules.

---

## ⚙️ How It Works

```text
Network Devices
      │
      ▼
   Netmiko
      │
      ▼
Collect Running Config
      │
      ▼
┌─────────────────┬─────────────────┐
│  Git Baseline   │   YAML Rules    │
└────────┬────────┴────────┬────────┘
         ▼                 ▼
    Drift Check      Compliance Check
         │                 │
         └────────┬────────┘
                  ▼
          Score + Report
```

---

## 🛠️ Built With

* **Python**
* **Netmiko**
* **YAML**
* **Git**
* **EVE-NG / GNS3**
* **Virtual Routers & Switches**

---

## 🎯 Project Goal

CompliNet explores how simple network automation can:

* 🔍 Detect unnoticed configuration changes
* ✅ Identify compliant and non-compliant devices
* ⚡ Speed up network configuration audits
* 🛡️ Reduce risks caused by configuration drift
* 🔧 Recommend remediation without automatically modifying devices

---

### Detect → Compare → Evaluate → Report

> Developed and tested using virtual network devices in a lab environment.
