import React from 'react';

const RemediationGuide = ({ summary }) => {
  const failedRules = summary?.failed_rules || [];

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px' }}>Network Engineering Remediation Playbook</h2>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
          Suggested configuration fixes for non-compliant devices (remediation suggestions only; no auto-pushes)
        </p>
      </div>

      <div className="card">
        {failedRules.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--pass-color)' }}>
            🎉 <strong>No remediations required! All devices are fully compliant with baseline standards.</strong>
          </div>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Target Device</th>
                  <th>Rule ID</th>
                  <th>Severity</th>
                  <th>Status</th>
                  <th>Recommended Remediation Commands</th>
                </tr>
              </thead>
              <tbody>
                {failedRules.map((item, idx) => (
                  <tr key={idx}>
                    <td><strong>{item.device_name}</strong></td>
                    <td><code>{item.rule_id}</code></td>
                    <td>
                      <span className={`badge badge-${item.severity?.toLowerCase()}`}>
                        {item.severity}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${item.status === 'FAIL' ? 'badge-fail' : 'badge-warn'}`}>
                        {item.status}
                      </span>
                    </td>
                    <td>
                      <div
                        style={{
                          background: '#0d1117',
                          padding: '8px 12px',
                          borderRadius: '6px',
                          fontFamily: 'monospace',
                          color: '#38bdf8',
                        }}
                      >
                        # Remediation for {item.name}:
                        <br />
                        {item.remediation}
                      </div>
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

export default RemediationGuide;
