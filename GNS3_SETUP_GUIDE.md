# 🚀 CompliNet Live GNS3 Integration Guide

This guide walks you through connecting **CompliNet** directly to live virtual routers and switches running inside **GNS3**.

---

## 🛠️ Step 1: Prepare Your GNS3 Topology

1. Open **GNS3** and create or open your network topology (e.g. 1 Cisco IOS Router `R1` and 1 Cisco Switch `SW1`).
2. Ensure the **GNS3 Local Server** API is running (default: `http://127.0.0.1:3080`).

```text
Host PC (CompliNet Engine)
    │  http://127.0.0.1:3080 (GNS3 API)
    ├───► Auto-discovers Nodes & Console Ports
    │
    └───► Netmiko SSH / Telnet (127.0.0.1:5001 / 127.0.0.1:5002)
          │
          ├───► [ GNS3 Router R1 ]
          └───► [ GNS3 Switch SW1 ]
```

---

## 🔑 Step 2: Bootstrap Cisco Devices in GNS3

Copy and paste the appropriate bootstrap configuration into the GNS3 console for your virtual devices:

### Cisco IOS Router Bootstrap (SSH Mode)
```cisco
enable
configure terminal
hostname R1
ip domain-name complinet.local

username admin privilege 15 secret cisco
enable secret cisco

crypto key generate rsa modulus 1024

interface FastEthernet0/0
 ip address 192.168.100.11 255.255.255.0
 no shutdown

line vty 0 4
 transport input ssh
 login local
exit
write memory
```

### Cisco IOS Switch Bootstrap (Rapid PVST / VTP Transparent)
```cisco
enable
configure terminal
hostname SW1
ip domain-name complinet.local

username admin privilege 15 secret cisco
enable secret cisco

vtp mode transparent
spanning-tree mode rapid-pvst

interface VLAN 1
 ip address 192.168.100.21 255.255.255.0
 no shutdown

line vty 0 4
 transport input ssh
 login local
exit
write memory
```

---

## 🔄 Step 3: Sync Inventory from GNS3

CompliNet can automatically query the GNS3 REST API to discover your topology nodes and console ports!

Run the GNS3 sync script from the `network-compliance` folder:

```powershell
# Auto-discover active nodes in GNS3
$env:PYTHONPATH="."; C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe scripts/gns3_sync.py
```

Or trigger it directly from the **CompliNet Dashboard** at `http://localhost:3000` by clicking **"Sync GNS3 Topology"**.

---

## ⚡ Step 4: Run Live Configuration Collection

Once GNS3 nodes are running and bootstrapped:

```powershell
# Collect live running configs & perform static compliance checks against Git baselines
$env:COMPLINET_MOCK="0"; $env:PYTHONPATH="."; C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe scripts/main.py
```

CompliNet will connect to the live GNS3 devices, extract `show running-config`, evaluate rules, compute health scores, and render the reports in the web dashboard!
