import React from 'react';

const ComplianceDashboard = ({ summary, onRunAudit, onSelectTab }) => {
  if (!summary) return <div>Loading compliance metrics...</div>;

  const {
    total_devices = 0,
    compliant_devices = 0,
    non_compliant_devices = 0,
    average_score = 100,
    severity_counts = {},
    failed_rules = [],
  } = summary;

  return (
    <div>
      {/* Metric Cards */}
      <div className="metrics-grid">
        <div className="card">
          <div className="card-title">Network Health Score</div>
          <div
            className="card-value"
            style={{
              color:
                average_score >= 90
                  ? 'var(--pass-color)'
                  : average_score >= 70
                  ? 'var(--warn-color)'
                  : 'var(--fail-color)',
            }}
          >
            {average_score} <span style={{ fontSize: '18px', color: 'var(--text-muted)' }}>/ 100</span>
          </div>
          <div className="card-subtext">Git Baseline Alignment</div>
        </div>

        <div className="card">
          <div className="card-title">Audit Scope</div>
          <div className="card-value">{total_devices}</div>
          <div className="card-subtext">Active Monitored Devices</div>
        </div>

        <div className="card">
          <div className="card-title">Compliant Devices</div>
          <div className="card-value" style={{ color: 'var(--pass-color)' }}>
            {compliant_devices}
          </div>
          <div className="card-subtext">Zero Drift / Fully Passing</div>
        </div>

        <div className="card">
          <div className="card-title">Drift / Non-Compliant</div>
          <div className="card-value" style={{ color: 'var(--fail-color)' }}>
            {non_compliant_devices}
          </div>
          <div className="card-subtext">Requires Engineering Review</div>
        </div>
      </div>

      {/* Severity Breakdown */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Rule Violation Severity Breakdown</h3>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, padding: '16px', background: 'var(--bg-dark)', borderRadius: '8px' }}>
            <span className="badge badge-critical">Critical</span>
            <div style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '8px' }}>
              {severity_counts.critical || 0}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Telnet / Urgent Security Risk
            </div>
          </div>

          <div style={{ flex: 1, padding: '16px', background: 'var(--bg-dark)', borderRadius: '8px' }}>
            <span className="badge badge-high">High</span>
            <div style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '8px' }}>
              {severity_counts.high || 0}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              SSH / AAA / VTP Risk
            </div>
          </div>

          <div style={{ flex: 1, padding: '16px', background: 'var(--bg-dark)', borderRadius: '8px' }}>
            <span className="badge badge-medium">Medium</span>
            <div style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '8px' }}>
              {severity_counts.medium || 0}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              NTP / STP Mode
            </div>
          </div>

          <div style={{ flex: 1, padding: '16px', background: 'var(--bg-dark)', borderRadius: '8px' }}>
            <span className="badge badge-low">Low / Warning</span>
            <div style={{ fontSize: '24px', fontWeight: 'bold', marginTop: '8px' }}>
              {(severity_counts.low || 0) + (severity_counts.warning || 0)}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Logging Buffer Size
            </div>
          </div>
        </div>
      </div>

      {/* Actionable Rule Violations Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '16px' }}>Active Configuration Violations & Remediations</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Static analysis results against Git baselines
            </p>
          </div>
          <button className="btn btn-secondary" onClick={() => onSelectTab('remediation')}>
            View Full Remediation Guide
          </button>
        </div>

        {failed_rules.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--pass-color)' }}>
            🎉 <strong>All network devices are 100% compliant with approved Git baselines!</strong>
          </div>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Device</th>
                  <th>Rule ID</th>
                  <th>Rule Name</th>
                  <th>Status</th>
                  <th>Severity</th>
                  <th>Suggested Remediation</th>
                </tr>
              </thead>
              <tbody>
                {failed_rules.map((item, idx) => (
                  <tr key={idx}>
                    <td><strong>{item.device_name}</strong></td>
                    <td><code>{item.rule_id}</code></td>
                    <td>{item.name}</td>
                    <td>
                      <span className={`badge ${item.status === 'FAIL' ? 'badge-fail' : 'badge-warn'}`}>
                        {item.status}
                      </span>
                    </td>
                    <td>
                      <span className={`badge badge-${item.severity?.toLowerCase()}`}>
                        {item.severity}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'monospace', color: '#cbd5e1' }}>
                      {item.remediation}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComplianceDashboard;