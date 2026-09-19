import React from 'react';

const RemediationGuide = ({ summary, requests = [], onCreateRequest, onApproveRequest, onExecuteRequest }) => {
  const failedRules = summary?.failed_rules || [];

  const requestRemediation = async (item) => {
    const playbook = window.prompt('Choose playbook: syslog, ipv6, ospf, or hostname', 'hostname');
    if (!playbook) return;
    const requestedBy = window.prompt('Your name', 'operator');
    if (!requestedBy) return;
    await onCreateRequest({
      device_name: item.device_name,
      playbook: playbook.toLowerCase(),
      requested_by: requestedBy,
      reason: `Rule ${item.rule_id}: ${item.name}`,
    });
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px' }}>Network Engineering Remediation Playbook</h2>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
          Every change requires an explicit approval before Ansible execution.
        </p>
      </div>

      <div className="card">
        {failedRules.length === 0 ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--pass-color)' }}>
            <strong>No remediations required! All devices are fully compliant with baseline standards.</strong>
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
                    <th>Action</th>
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
                    <td>
                      <button className="btn btn-secondary" onClick={() => requestRemediation(item)}>
                        Request
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        <h3 style={{ fontSize: '16px', marginBottom: '16px' }}>Remediation Requests</h3>
        {requests.length === 0 ? (
          <div style={{ color: 'var(--text-muted)' }}>No remediation requests have been submitted.</div>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr><th>Device</th><th>Playbook</th><th>Requested By</th><th>Status</th><th>Action</th></tr>
              </thead>
              <tbody>
                {requests.map((request) => (
                  <tr key={request.id}>
                    <td>{request.device_name}</td>
                    <td><code>{request.playbook}</code></td>
                    <td>{request.requested_by}</td>
                    <td><span className="badge">{request.status}</span></td>
                    <td>
                      {request.status === 'pending' && (
                        <button
                          className="btn btn-secondary"
                          onClick={() => {
                            const approvedBy = window.prompt('Approved by', 'operator');
                            if (approvedBy) onApproveRequest(request.id, approvedBy);
                          }}
                        >
                          Approve
                        </button>
                      )}
                      {request.status === 'approved' && (
                        <button className="btn btn-primary" onClick={() => onExecuteRequest(request.id)}>
                          Execute
                        </button>
                      )}
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
