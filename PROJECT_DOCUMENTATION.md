# CompliNet Project Documentation

## 1. Project Overview

CompliNet is a network compliance and configuration-drift platform for FRRouting (FRR) devices running in Containerlab, with support for real devices through Netmiko.

The platform:

- Collects live device configurations.
- Evaluates configurations against YAML compliance rules.
- Compares collected configurations with Git-managed baselines.
- Produces explainable findings with expected values, actual values, reasons, severity, and remediation guidance.
- Displays compliance data in a React dashboard.
- Monitors the controller host health.
- Supports human-approved Ansible remediation.
- Recollects and verifies configuration after remediation.
- Records operational events in SQLite.

The current lab contains two FRR routers:

- `R1` in `clab-complinet-r1`
- `R2` in `clab-complinet-r2`

## 2. Architecture

```text
Containerlab / Real Network Devices
              |
              v
  Source-based collectors
  Containerlab or Netmiko
              |
              v
     Collected configurations
              |
       +------+------+
       |             |
       v             v
 Git baselines   YAML rules
       |             |
       +------+------+
              v
      Compliance analyzer
              |
       +------+------+----------------+
       |             |                |
       v             v                v
   FastAPI       SQLite audit      HTML reports
       |
       v
 React/Vite dashboard
       |
       v
 Approved Ansible remediation
       |
       v
 Recollect and verify
```

## 3. Technologies Used

### Backend and analysis

- Python 3.11 or newer. Python 3.14 works with the current dependency versions.
- FastAPI for the REST API.
- Uvicorn for the application server.
- Pydantic 2 for request validation.
- PyYAML for inventory and rule files.
- SQLAlchemy is retained as a project dependency for future persistence work.
- psutil for CPU, memory, disk, uptime, and Docker health reporting.
- SQLite for the audit event ledger.
- pytest and pytest-asyncio for tests.

### Network automation

- Containerlab for the FRR lab topology.
- Docker for running and accessing the FRR containers.
- FRRouting (FRR) and `vtysh` for device configuration and collection.
- Netmiko is included as a future-use collector path for real-device collection; the current validated environment uses Containerlab and FRR.
- Ansible Core for approved remediation playbooks.

### Frontend

- React 18.
- Vite for development and production builds.
- Axios for API requests.
- CSS for the dashboard interface.

### Development environment

- Git and GitHub.
- WSL, with the backend running in the same WSL distribution as the Containerlab Docker daemon.
- The project fork is `https://github.com/ha6vas2/CompliNet.git`.

## 4. Repository Structure

```text
CompliNet/
|-- README.md                         Project overview and quick start
|-- PROJECT_DOCUMENTATION.md          Detailed architecture, setup, and troubleshooting
|-- complinet-dashboard/
|   |-- ansible/
|   |   |-- inventory.yml              Lab remediation inventory
|   |   `-- playbooks/                 Approved remediation playbooks
|   |-- backend/
|   |   |-- app/
|   |   |   |-- api/routers/            FastAPI route modules
|   |   |   |-- schemas/                API request schemas
|   |   |   |-- services/               Compliance, health, audit, remediation services
|   |   |   `-- main.py                 FastAPI application entry point
|   |   `-- requirements.txt
|   |-- frontend/
|   |   |-- src/App.jsx                Dashboard application
|   |   |-- src/components/             Dashboard components
|   |   |-- src/services/api.js         API client functions
|   |   `-- package.json
|   `-- dist/                          Built frontend output
|-- network-compliance/
|   |-- baselines/                     Approved FRR configurations
|   |-- collected/                     Runtime configurations, ignored by Git
|   |-- compliance/rules.yaml           Compliance policy definitions
|   |-- inventory/devices.yaml          Device inventory
|   |-- collectors/                    Containerlab and Netmiko collectors
|   |-- scripts/                       Collection, analysis, and report code
|   |-- reports/                       Generated reports, ignored by Git
|   |-- lab/                            Containerlab topology and FRR files
|   `-- tests/                          Analyzer regression tests
`-- .gitignore
```

## 5. Installation and Setup

### 5.1 Requirements

Install or enable:

- Docker Desktop with WSL integration.
- WSL distribution named `Containerlab` or another Linux distribution that runs the Containerlab Docker daemon.
- Containerlab.
- Python 3.11+.
- Node.js and npm.
- Git.

The backend and Containerlab must use the same Docker daemon. Running the backend in a different WSL distribution can result in an empty Docker environment even when the lab is running.

### 5.2 Backend environment

Run these commands in the WSL distribution that owns the running Containerlab containers:

```bash
cd /mnt/d/APNIC/CompliNet/complinet-dashboard/backend

python3 -m venv /tmp/complinet-backend-venv
source /tmp/complinet-backend-venv/bin/activate
python -m pip install -r requirements.txt

export PYTHONPATH=.
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For a persistent environment, create the virtual environment outside the repository or use the backend `.venv` only when it was created with the same Python version as the WSL distribution running the service.

API documentation is available at:

- `http://localhost:8000/docs`
- `http://localhost:8000/openapi.json`

### 5.3 Frontend

In PowerShell or a terminal with Node.js:

```powershell
cd D:\APNIC\CompliNet\complinet-dashboard\frontend
npm install
npm run dev
```

Open the URL shown by Vite, normally `http://localhost:5173`.

To build the production dashboard:

```powershell
npm run build
```

### 5.4 Start the Containerlab topology

From the same WSL distribution that runs the Containerlab Docker daemon:

```bash
cd /mnt/d/APNIC/CompliNet/network-compliance
containerlab deploy -t lab/complinet.clab.yml
```

Verify the lab:

```bash
docker ps
docker exec clab-complinet-r1 vtysh -c "show running-config"
docker exec clab-complinet-r2 vtysh -c "show running-config"
```

## 6. Using the Application

### 6.1 Run a compliance audit

The dashboard does not run audits automatically. Press **Run Compliance Audit** to:

1. Collect each enabled device configuration.
2. Evaluate compliance rules.
3. Compare collected configurations with baselines.
4. Update the dashboard summary.
5. Record compliance events when findings are detected.

The equivalent API call is:

```bash
curl -X POST http://localhost:8000/api/compliance/run
```

### 6.2 Health monitoring

```text
GET /api/system/health
```

The response includes controller status, CPU usage, memory usage, disk usage, uptime, and Docker/container status.

### 6.3 Remediation workflow

Every remediation requires human approval:

1. Create a request.
2. Approve the request.
3. Execute the request.
4. Recollect configuration.
5. Verify compliance.
6. Review the audit events.

Example API flow:

```powershell
$request = Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/remediation/requests `
  -ContentType 'application/json' `
  -Body '{"device_name":"R1","playbook":"hostname","requested_by":"operator","reason":"Restore approved hostname"}'

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/remediation/requests/$($request.id)/approve" `
  -ContentType 'application/json' `
  -Body '{"approved_by":"network-admin"}'

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/remediation/requests/$($request.id)/execute"
```

Supported playbooks:

- `hostname`
- `syslog`
- `ipv6`
- `ospf`

Audit events can be queried with:

```text
GET /api/audit/events
```

## 7. API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/system/health` | Controller and Docker health |
| `GET /api/compliance/summary` | Compliance summary |
| `GET /api/compliance/devices` | Device compliance results |
| `GET /api/compliance/devices/{device_name}` | One device result |
| `GET /api/compliance/rules` | Configured compliance rules |
| `POST /api/compliance/run` | Manual collection and audit |
| `GET /api/audit/events` | Audit timeline |
| `GET /api/remediation/requests` | Remediation requests |
| `POST /api/remediation/requests` | Create a request |
| `POST /api/remediation/requests/{id}/approve` | Approve a request |
| `POST /api/remediation/requests/{id}/execute` | Execute and verify a request |

## 8. Testing

### Backend tests

Run from the backend directory in the active backend environment:

```bash
cd /mnt/d/APNIC/CompliNet/complinet-dashboard/backend
PYTHONPATH=. pytest -q
```

The focused operations suite currently contains two tests covering health metrics and approval enforcement.

### Compliance engine tests

```bash
cd /mnt/d/APNIC/CompliNet/network-compliance
PYTHONPATH=. pytest -q
```

The analyzer regression suite currently contains 14 tests.

### Frontend validation

```powershell
cd D:\APNIC\CompliNet\complinet-dashboard\frontend
npm run build
npm audit --audit-level=high
```

## 9. Problems Encountered and Resolutions

### Python was unavailable in PowerShell

The Windows PowerShell environment did not have a usable `python` or `pytest` command. Testing was moved to WSL, where Python and project virtual environments were available.

### FastAPI failed to import

The original backend requirements pinned FastAPI 0.95 and Pydantic 1.10, which are incompatible with Python 3.14. The requirements were updated to current FastAPI, Uvicorn, Pydantic 2, pytest, and pytest-asyncio ranges.

### WSL could not access Docker

The Docker socket was owned by `root:root` and the WSL user was not in the Docker group. The socket was changed to `root:docker`, the user was added to the `docker` group, and access was verified with `docker ps`.

### Backend and Containerlab used different Docker daemons

Ubuntu WSL could access Docker but could not see the Containerlab containers. The backend was moved to the dedicated `Containerlab` WSL distribution, which owns the daemon containing `clab-complinet-r1` and `clab-complinet-r2`.

### Ansible could not be found

The remediation service originally called `ansible-playbook` by name. It now resolves the executable beside the active Python interpreter, making virtual-environment execution reliable.

### Ansible rejected the locale

The Containerlab distribution did not provide a usable default locale for Ansible. The remediation subprocess now sets `LANG=C.UTF-8` and `LC_ALL=C.UTF-8`.

### Stale frontend bundles still showed `LIVE · 10s`

The source had been updated, but old generated bundles in `dist/assets` still contained the live indicator. The dashboard was rebuilt and stale bundles were removed.

### Automatic audits were misleading

The frontend originally ran a compliance audit every 10 seconds. This caused collection attempts without an explicit user action and made Docker errors appear repeatedly. Automatic polling was removed; audits now run only when the user presses **Run Compliance Audit**.

## 10. Security and Operational Notes

- Do not use `chmod 666 /var/run/docker.sock`.
- Docker socket access grants broad control over the host; limit membership in the Docker group.
- Do not commit passwords, private keys, or `.env` files.
- The current Ansible lab inventory targets local Docker containers. Real-device inventory and credentials must be configured separately.
- Test remediation in the lab before using production devices.
- Remediation requests are currently held in memory; audit events persist in SQLite.
- Generated collected configs and reports are ignored by Git.

## 11. Current Status and Future Work

Implemented:

- FRR/Containerlab collection.
- Explainable compliance findings.
- Manual compliance audits.
- Host health monitoring.
- SQLite audit events.
- Approval-gated Ansible remediation.
- Post-remediation verification.

Recommended next improvements:

- Activate and validate the Netmiko collector against real devices.
- Persist remediation requests in SQLite.
- Add authentication and role-based approval permissions.
- Add structured Ansible inventory for real devices.
- Add frontend audit timeline visualization.
- Add automated API integration tests.
- Add CI checks for backend tests, frontend builds, YAML, and Ansible syntax.
