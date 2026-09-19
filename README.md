# CompliNet

CompliNet is a network compliance and configuration-drift platform for FRRouting (FRR) devices running in Containerlab, with support for real devices through Netmiko.

It collects live configurations, evaluates YAML compliance policies, compares them with Git-managed baselines, explains findings, and presents the results in a React dashboard. Approved remediation can be executed through Ansible and verified by recollecting the device configuration.

## What It Includes

- FRR/Containerlab configuration collection is implemented; the Netmiko collector is retained for future real-device use.
- Static compliance rules and baseline drift comparison.
- Explainable findings with expected values, actual values, reasons, severity, and remediation guidance.
- FastAPI backend and React/Vite dashboard.
- Manual compliance audits through **Run Compliance Audit**.
- Linux controller health monitoring through psutil.
- SQLite audit events.
- Human-approved Ansible remediation for hostname, syslog, IPv6, and OSPF.
- Post-remediation recollection and verification.

## Quick Start

The backend must run in the same WSL distribution as the Containerlab Docker daemon. In this project that is the `Containerlab` distribution.

### Start the lab and backend

```bash
cd /mnt/d/APNIC/CompliNet/network-compliance
containerlab deploy -t lab/complinet.clab.yml

cd /mnt/d/APNIC/CompliNet/complinet-dashboard/backend
python3 -m venv /tmp/complinet-backend-venv
source /tmp/complinet-backend-venv/bin/activate
python -m pip install -r requirements.txt
export PYTHONPATH=.
export LANG=C.UTF-8
export LC_ALL=C.UTF-8
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Start the frontend

```powershell
cd D:\APNIC\CompliNet\complinet-dashboard\frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`.

### Run an audit

The dashboard does not audit automatically. Press **Run Compliance Audit** to collect, analyze, and display current results.

API documentation is available at `http://localhost:8000/docs`.

## Repository Layout

```text
CompliNet/
|-- README.md                         This overview
|-- PROJECT_DOCUMENTATION.md          Full setup, architecture, technology, and troubleshooting guide
|-- complinet-dashboard/
|   |-- ansible/                      Lab inventory and remediation playbooks
|   |-- backend/                      FastAPI API and services
|   |-- frontend/                     React/Vite dashboard
|   `-- dist/                         Built frontend output
|-- network-compliance/
|   |-- baselines/                    Approved configurations
|   |-- compliance/                   YAML compliance rules
|   |-- inventory/                    Device inventory
|   |-- collectors/                   Containerlab and Netmiko collectors
|   |-- scripts/                      Analysis and report tooling
|   |-- lab/                          Containerlab topology
|   `-- tests/                        Compliance analyzer tests
`-- .gitignore
```

## Technologies

Python, FastAPI, Uvicorn, Pydantic, PyYAML, psutil, SQLite, pytest, Containerlab, Docker, FRRouting, `vtysh`, Ansible Core, React, Vite, Axios, Git, and WSL. Netmiko is included as the planned future collector for real network devices.

## Tests

Backend tests:

```bash
cd /mnt/d/APNIC/CompliNet/complinet-dashboard/backend
PYTHONPATH=. pytest -q
```

Compliance analyzer tests:

```bash
cd /mnt/d/APNIC/CompliNet/network-compliance
PYTHONPATH=. pytest -q
```

Frontend build:

```powershell
cd D:\APNIC\CompliNet\complinet-dashboard\frontend
npm run build
```

## Documentation

See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) for the complete architecture, technologies, setup instructions, API endpoints, testing instructions, errors encountered, resolutions, security notes, and future work.
