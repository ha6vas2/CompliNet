import React, { useState } from 'react';

const DeviceList = ({ devices, onOpenAddDevice }) => {
  const [expandedDevice, setExpandedDevice] = useState(null);

  const toggleDiff = (deviceName) => {
    setExpandedDevice(expandedDevice === deviceName ? null : deviceName);
  };

  const renderDiffLines = (diffText) => {
    if (!diffText || diffText.trim() === '') {
      return (
        <div style={{ color: 'var(--pass-color)', fontStyle: 'italic' }}>
          ✓ No configuration drift detected. Running config exactly matches the Git baseline!
        </div>
      );
    }

    return diffText.split('\n').map((line, index) => {
      let className = '';
      if (line.startsWith('+') && !line.startsWith('+++')) {
        className = 'diff-add';
      } else if (line.startsWith('-') && !line.startsWith('---')) {
        className = 'diff-del';
      } else if (line.startsWith('@@') || line.startsWith('---') || line.startsWith('+++')) {
        className = 'diff-hdr';
      }
      return (
        <span key={index} className={className}>
          {line}
          {'\n'}
        </span>
      );
    });
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '20px' }}>Monitored Device Inventory & Drift Analysis</h2>
          <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Snapshot comparisons against Git baselines
          </p>
        </div>
        <button className="btn btn-primary" onClick={onOpenAddDevice}>
          + Add Device
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {devices.map((device) => {
          const isExpanded = expandedDevice === device.device_name;
          return (
            <div key={device.device_name} className="card">
              <div
                style={{
                  display: 'flex',
                  justify: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '12px',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <h3 style={{ fontSize: '18px' }}>{device.device_name}</h3>
                    <span className={`badge ${device.compliant ? 'badge-pass' : 'badge-fail'}`}>
                      {device.compliant ? 'Compliant' : 'Non-Compliant'}
                    </span>
                    <span className="badge badge-low">{device.role}</span>
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '6px' }}>
                    IP: <code>{device.host}</code> | Type: <code>{device.device_type}</code> | Git Baseline: <code>{device.baseline}</code>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Score</div>
                    <div
                      style={{
                        fontSize: '22px',
                        fontWeight: 'bold',
                        color: device.score >= 80 ? 'var(--pass-color)' : 'var(--fail-color)',
                      }}
                    >
                      {device.score} / 100
                    </div>
                  </div>

                  <button className="btn btn-secondary" onClick={() => toggleDiff(device.device_name)}>
                    {isExpanded ? 'Hide Git Diff' : 'View Config Drift Diff'}
                  </button>
                </div>
              </div>

              {/* Rule Evaluation Summary */}
              <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--panel-border)' }}>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '8px' }}>
                  Rule Check Breakdown:
                </div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {device.results?.map((res, i) => (
                    <span
                      key={i}
                      className={`badge ${
                        res.status === 'PASS'
                          ? 'badge-pass'
                          : res.status === 'WARN'
                          ? 'badge-warn'
                          : 'badge-fail'
                      }`}
                      title={`${res.name}: ${res.remediation}`}
                    >
                      {res.rule_id}: {res.status}
                    </span>
                  ))}
                </div>
              </div>

              {/* Expandable Unified Diff Viewer */}
              {isExpanded && (
                <div style={{ marginTop: '16px' }}>
                  <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                    Unified Git Line Diff (Baseline: <code>{device.baseline}</code> vs Snapshot):
                  </div>
                  <pre className="diff-viewer">{renderDiffLines(device.diff)}</pre>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default DeviceList;