import React, { useState } from 'react';

const AddDeviceModal = ({ isOpen, onClose, onAddDevice }) => {
  const [name, setName] = useState('');
  const [host, setHost] = useState('');
  const [deviceType, setDeviceType] = useState('cisco_ios');
  const [role, setRole] = useState('router');
  const [baseline, setBaseline] = useState('cisco_router.cfg');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name || !host) return;
    onAddDevice({
      name,
      host,
      device_type: deviceType,
      role,
      baseline,
    });
    setName('');
    setHost('');
    onClose();
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <h3 style={{ marginBottom: '16px', fontSize: '18px' }}>Add Monitored Device</h3>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Device Name / Hostname (e.g. R2, SW2)</label>
            <input
              type="text"
              className="form-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. R2"
              required
            />
          </div>

          <div className="form-group">
            <label>Management IP Address</label>
            <input
              type="text"
              className="form-input"
              value={host}
              onChange={(e) => setHost(e.target.value)}
              placeholder="192.168.100.12"
              required
            />
          </div>

          <div className="form-group">
            <label>Device Type (Netmiko driver)</label>
            <select
              className="form-input"
              value={deviceType}
              onChange={(e) => setDeviceType(e.target.value)}
            >
              <option value="cisco_ios">Cisco IOS / IOS-XE</option>
              <option value="cisco_nxos">Cisco NX-OS</option>
            </select>
          </div>

          <div className="form-group">
            <label>Role</label>
            <select
              className="form-input"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="router">Router</option>
              <option value="switch">Switch</option>
            </select>
          </div>

          <div className="form-group">
            <label>Git Approved Baseline File</label>
            <select
              className="form-input"
              value={baseline}
              onChange={(e) => setBaseline(e.target.value)}
            >
              <option value="cisco_router.cfg">cisco_router.cfg</option>
              <option value="cisco_switch.cfg">cisco_switch.cfg</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end', marginTop: '24px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save Device to Inventory
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddDeviceModal;
