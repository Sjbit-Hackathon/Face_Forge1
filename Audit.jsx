import React from 'react';
import { Download, Search, Filter, Calendar } from 'lucide-react';
import './Audit.css';

const auditData = [
  { id: 1, time: '2026-04-29 14:05:12', officer: 'Det. Sarah Chen', case: 'CASE-2026-001', iter: 'v1', action: 'SKETCH_GENERATED', sha: 'b0aee043...', details: 'Generated initial HD sketch' },
  { id: 2, time: '2026-04-29 14:03:00', officer: 'Det. Sarah Chen', case: 'CASE-2026-001', iter: '-', action: 'FEATURE_LOCK', sha: '-', details: 'Locked Eyes feature' },
  { id: 3, time: '2026-04-29 14:00:00', officer: 'Det. Sarah Chen', case: 'CASE-2026-001', iter: '-', action: 'SESSION_CREATED', sha: '-', details: 'Created new case session' },
  { id: 4, time: '2026-04-29 13:45:10', officer: 'Chief Helen Park', case: '-', iter: '-', action: 'LOGIN', sha: '-', details: 'Admin login success' },
  { id: 5, time: '2026-04-28 16:30:22', officer: 'Det. Marcus Reed', case: 'CASE-2026-002', iter: 'v12', action: 'EXPORTED', sha: '7a584742...', details: 'Exported forensic report PDF' },
  { id: 6, time: '2026-04-28 16:20:15', officer: 'Det. Marcus Reed', case: 'CASE-2026-002', iter: 'v12', action: 'SKETCH_REFINED', sha: '533b3d5b...', details: 'Refined jaw structure' },
];

const getActionBadgeColor = (action) => {
  switch (action) {
    case 'LOGIN': return 'badge-blue';
    case 'SESSION_CREATED': return 'badge-gray';
    case 'SKETCH_GENERATED': return 'badge-purple';
    case 'SKETCH_REFINED': return 'badge-teal';
    case 'FEATURE_LOCK': return 'badge-amber';
    case 'EXPORTED': return 'badge-green';
    case 'LOGOUT': return 'badge-gray';
    default: return 'badge-gray';
  }
};

const Audit = () => {
  return (
    <div className="audit-page">
      <div className="audit-header">
        <h1 className="page-title">Admin Audit Log</h1>
        <button className="btn-secondary">
          <Download size={16} /> Export Audit CSV
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-content">
            <div className="stat-label">Total Events</div>
            <div className="stat-value">124,592</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-content">
            <div className="stat-label">Sessions Today</div>
            <div className="stat-value text-primary">18</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-content">
            <div className="stat-label">Exports This Week</div>
            <div className="stat-value text-success">42</div>
          </div>
        </div>
      </div>

      <div className="audit-panel">
        <div className="toolbar">
          <div className="search-group">
            <Search size={16} className="toolbar-icon" />
            <input type="text" placeholder="Search officer or case..." className="toolbar-input" />
          </div>
          <div className="toolbar-filters">
            <button className="filter-btn"><Calendar size={16} /> Date Range</button>
            <button className="filter-btn"><Filter size={16} /> Action Type</button>
          </div>
        </div>

        <table className="audit-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Officer</th>
              <th>Case #</th>
              <th>Iter</th>
              <th>Action</th>
              <th>SHA-256</th>
              <th>Details</th>
            </tr>
          </thead>
          <tbody>
            {auditData.map((row) => (
              <tr key={row.id}>
                <td className="mono text-muted">{row.time}</td>
                <td>{row.officer}</td>
                <td className="mono">{row.case}</td>
                <td>{row.iter}</td>
                <td>
                  <span className={`action-badge ${getActionBadgeColor(row.action)}`}>
                    {row.action}
                  </span>
                </td>
                <td className="mono text-muted truncate-cell" title={row.sha}>{row.sha}</td>
                <td className="details-cell">{row.details}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="pagination">
          <span className="page-info">Showing 1-20 of 124,592</span>
          <div className="page-controls">
            <button className="btn-secondary" disabled>Previous</button>
            <button className="btn-secondary">Next</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Audit;
