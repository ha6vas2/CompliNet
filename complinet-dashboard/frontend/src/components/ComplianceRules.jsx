import React, { useState } from 'react';

const ComplianceRules = ({ rules }) => {
  const [filterType, setFilterType] = useState('all');

  const filteredRules = rules.filter((r) => {
    if (filterType === 'all') return true;
    return r.type === filterType;
  });

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '20px' }}>YAML Compliance Rule Matrix</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Static analysis rules evaluated against device running configs
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {['all', 'required', 'forbidden', 'exact-match', 'warning'].map((type) => (
            <button
              key={type}
              className={`btn ${filterType === type ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '12px', padding: '6px 12px' }}
              onClick={() => setFilterType(type)}
            >
              {type.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Rule ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Rule Type</th>
                <th>Target Pattern / Config</th>
                <th>Severity</th>
                <th>Remediation Suggestion</th>
              </tr>
            </thead>
            <tbody>
              {filteredRules.map((rule) => (
                <tr key={rule.id}>
                  <td><code>{rule.id}</code></td>
                  <td><strong>{rule.name}</strong></td>
                  <td style={{ color: 'var(--text-muted)' }}>{rule.description}</td>
                  <td>
                    <span className="badge badge-low">{rule.type}</span>
                  </td>
                  <td><code>{rule.config}</code></td>
                  <td>
                    <span className={`badge badge-${rule.severity?.toLowerCase()}`}>
                      {rule.severity}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'monospace', color: '#cbd5e1' }}>{rule.remediation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ComplianceRules;
