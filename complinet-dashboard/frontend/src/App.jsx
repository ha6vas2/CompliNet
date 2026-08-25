import React, { useEffect, useState } from 'react';
import ComplianceDashboard from './components/ComplianceDashboard';
import DeviceList from './components/DeviceList';
import ComplianceRules from './components/ComplianceRules';
import RemediationGuide from './components/RemediationGuide';
import AddDeviceModal from './components/AddDeviceModal';
import { fetchSummary, fetchDevices, fetchRules, triggerAuditRun, createDevice } from './services/api';
import './styles.css';

const App = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [summary, setSummary] = useState(null);
  const [devices, setDevices] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningAudit, setRunningAudit] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [error, setError] = useState(null);

  const loadAllData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [summaryData, deviceData, ruleData] = await Promise.all([
        fetchSummary(),
        fetchDevices(),
        fetchRules(),
      ]);
      setSummary(summaryData);
      setDevices(deviceData);
      setRules(ruleData);
    } catch (err) {
      console.error('Failed to load compliance data:', err);
      setError('Unable to connect to CompliNet FastAPI backend. Make sure the backend server is running on http://localhost:8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAllData();
  }, []);

  const handleRunAudit = async () => {
    try {
      setRunningAudit(true);
      const newSummary = await triggerAuditRun();
      setSummary(newSummary);
      const newDevices = await fetchDevices();
      setDevices(newDevices);
    } catch (err) {
      console.error('Audit run failed:', err);
      alert('Audit run failed: ' + err.message);
    } finally {
      setRunningAudit(false);
    }
  };

  const handleGNS3Sync = async () => {
    try {
      setRunningAudit(true);
      const res = await syncGNS3();
      if (res.status === 'success') {
        alert(`Successfully discovered and imported ${res.count} active node(s) from GNS3!`);
        await loadAllData();
      } else {
        alert(`GNS3 Sync Notice: ${res.message}`);
      }
    } catch (err) {
      alert('GNS3 sync error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setRunningAudit(false);
    }
  };

  const handleAddDevice = async (deviceData) => {
    try {
      await createDevice(deviceData);
      await loadAllData();
    } catch (err) {
      console.error('Failed to add device:', err);
      alert('Failed to add device: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="app-container">
      {/* Top Glassmorphism Navigation Bar */}
      <header className="header">
        <div className="logo-area">
          <span className="logo-icon">🔍</span>
          <div>
            <div className="logo-title">CompliNet</div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Network Drift & Static Compliance Analysis System
            </div>
          </div>
        </div>

        <div className="header-actions">
          <button className="btn btn-secondary" onClick={handleGNS3Sync} disabled={runningAudit}>
            🌐 Sync GNS3 Topology
          </button>
          <button className="btn btn-secondary" onClick={() => setIsAddModalOpen(true)}>
            + Add Device IP
          </button>
          <button className="btn btn-primary" onClick={handleRunAudit} disabled={runningAudit}>
            {runningAudit ? '⚡ Running Collection & Analysis...' : '⚡ Run Compliance Audit'}
          </button>
        </div>
      </header>


      {/* View Tabs */}
      <nav className="tab-bar">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Executive Summary
        </button>
        <button
          className={`tab-btn ${activeTab === 'devices' ? 'active' : ''}`}
          onClick={() => setActiveTab('devices')}
        >
          🖥️ Devices & Drift Diffs ({devices.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'rules' ? 'active' : ''}`}
          onClick={() => setActiveTab('rules')}
        >
          🔍 Compliance Matrix ({rules.length} Rules)
        </button>
        <button
          className={`tab-btn ${activeTab === 'remediation' ? 'active' : ''}`}
          onClick={() => setActiveTab('remediation')}
        >
          🛠️ Remediation Playbook ({summary?.failed_rules?.length || 0})
        </button>
      </nav>

      {/* Main View Area */}
      <main className="main-content">
        {error && (
          <div
            style={{
              padding: '16px',
              backgroundColor: 'var(--fail-bg)',
              color: 'var(--fail-color)',
              borderRadius: '8px',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              marginBottom: '24px',
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {loading && !summary ? (
          <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading CompliNet Dashboard...
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <ComplianceDashboard
                summary={summary}
                onRunAudit={handleRunAudit}
                onSelectTab={(tab) => setActiveTab(tab)}
              />
            )}

            {activeTab === 'devices' && (
              <DeviceList
                devices={devices}
                onOpenAddDevice={() => setIsAddModalOpen(true)}
              />
            )}

            {activeTab === 'rules' && <ComplianceRules rules={rules} />}

            {activeTab === 'remediation' && <RemediationGuide summary={summary} />}
          </>
        )}
      </main>

      <AddDeviceModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onAddDevice={handleAddDevice}
      />
    </div>
  );
};

export default App;