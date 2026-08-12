# Network Configuration Drift Detection & Compliance Tool Using Static Analysis

This project is a simple network automation framework for detecting configuration drift and validating Cisco IOS device compliance against approved baselines and static YAML rules.

## Purpose

The tool collects running configuration from lab routers/switches, compares the runtime config against a Git-managed approved baseline, evaluates static compliance rules, and generates a human-readable HTML report.

## Architecture

```
Cisco Devices
      |
      v
   Netmiko
      |
      v
Current Config
      |
      +------------------+
      |                  |
      v                  v
Baseline Config     Compliance Rules
      |                  |
      +--------+---------+
               |
               v
         Static Analysis
               |
               v
       Score + Drift Diff
               |
               v
             HTML
            Report
```

## Directory structure

- `baselines/` - Approved configuration standards stored in Git.
- `compliance/` - YAML rule definitions used by the analyzer.
- `inventory/` - Device inventory and baseline mapping.
- `collected/` - Runtime configs retrieved from devices.
- `reports/` - Generated HTML compliance reports.
- `scripts/` - Python modules for collection, analysis, and reporting.
- `tests/` - Unit tests for analyzer functionality.

## Installation

### Create a Python virtual environment on Windows

Open PowerShell and run:

```powershell
cd C:\Users\saha\Documents\APNIC26\network-compliance
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Install requirements

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Baseline configs

Baseline configurations are stored in `baselines/`. These represent the approved standard for a device type. The analyzer and drift detection compare runtime config against the approved baseline.

## Compliance rules

Rules are defined in `compliance/rules.yaml` and support the following types:

- `required` - the config line must exist.
- `forbidden` - the config line must not exist.

The analyzer evaluates each rule and applies severity-based scoring.

## Netmiko collection

The collection module in `scripts/collect.py` reads `inventory/devices.yaml`, uses `NETMIKO_USERNAME` and `NETMIKO_PASSWORD` from the environment, connects to devices, and saves `show running-config` into `collected/<device_name>/current.cfg`.

> Credentials are not stored in Git.

## Run the analyzer

Use `scripts/main.py` to collect device configs, compare against baselines, run compliance rules, and generate HTML reports:

```powershell
python scripts/main.py
```

If the device is unreachable or credentials are missing, the tool exits gracefully with a clear error message.

## Run tests

From the project root:

```powershell
pytest
```

## Git usage

Use Git to version-control approved baselines, compliance rules, inventory, scripts, and documentation. The `collected/` and `reports/` directories are ignored to avoid storing runtime data.

### Initial commit example

```powershell
git init
git add .
git commit -m "Initial project scaffold for network configuration drift detection and compliance"
```
