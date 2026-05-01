import React, { useState } from 'react';
import { Folder, Activity, FileCheck, Plus, X } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCaseNumber, setNewCaseNumber] = useState('');
  const [sessions, setSessions] = useState([
    { id: 'CASE-2026-001', date: '2026-04-29', iterations: 3, status: 'Active' },
    { id: 'CASE-2026-002', date: '2026-04-28', iterations: 12, status: 'Exported' }
  ]);

  const handleCreateSession = (e) => {
    e.preventDefault();
    if (newCaseNumber) {
      navigate(`/session/${newCaseNumber}`);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1 className="page-title">Officer Dashboard</h1>
        <button className="btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={16} /> New Case Session
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <Folder size={20} className="stat-icon" />
          <div className="stat-content">
            <div className="stat-label">Total Sessions</div>
            <div className="stat-value">{sessions.length}</div>
          </div>
        </div>
        <div className="stat-card">
          <FileCheck size={20} className="stat-icon text-success" />
          <div className="stat-content">
            <div className="stat-label">Exported Cases</div>
            <div className="stat-value">{sessions.filter(s => s.status === 'Exported').length}</div>
          </div>
        </div>
        <div className="stat-card">
          <Activity size={20} className="stat-icon text-primary" />
          <div className="stat-content">
            <div className="stat-label">Active Sessions</div>
            <div className="stat-value">{sessions.filter(s => s.status === 'Active').length}</div>
          </div>
        </div>
      </div>

      <div className="sessions-panel">
        <h2 className="panel-title">Recent Sessions</h2>
        
        {sessions.length === 0 ? (
          <div className="empty-state">
            <p>No sessions yet — start your first case</p>
          </div>
        ) : (
          <table className="sessions-table">
            <thead>
              <tr>
                <th>Case #</th>
                <th>Date</th>
                <th>Iterations</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map(s => (
                <tr key={s.id}>
                  <td className="mono">{s.id}</td>
                  <td className="mono">{s.date}</td>
                  <td>{s.iterations}</td>
                  <td>
                    <span className={`status-badge ${s.status.toLowerCase()}`}>
                      {s.status}
                    </span>
                  </td>
                  <td>
                    <Link to={`/session/${s.id}`} className="btn-secondary action-btn">
                      {s.status === 'Active' ? 'Continue' : 'View'}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>New Case Session</h3>
              <button className="icon-btn" onClick={() => setIsModalOpen(false)}><X size={16} /></button>
            </div>
            <form onSubmit={handleCreateSession}>
              <div className="form-group">
                <label>Case Number</label>
                <input 
                  type="text" 
                  value={newCaseNumber}
                  onChange={(e) => setNewCaseNumber(e.target.value)}
                  placeholder="e.g. CASE-2026-003"
                  className="login-input"
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn-primary">Create Session</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
