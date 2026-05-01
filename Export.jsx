import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Download, FileText, Search, ChevronDown, ChevronRight, ShieldCheck } from 'lucide-react';
import './Export.css';

const Export = () => {
  const { id } = useParams();
  const [isAuditOpen, setIsAuditOpen] = useState(false);
  const [showMatches, setShowMatches] = useState(false);

  return (
    <div className="export-page">
      <div className="export-header">
        <div className="header-left">
          <h1 className="page-title">Forensic Report</h1>
          <span className="case-badge mono">{id}</span>
        </div>
        <div className="export-actions">
          <button className="btn-secondary" onClick={() => setShowMatches(true)}>
            <Search size={16} /> Check for Matches
          </button>
          <button className="btn-success">
            <Download size={16} /> Download HD PNG
          </button>
          <button className="btn-primary">
            <FileText size={16} /> Download PDF
          </button>
        </div>
      </div>

      <div className="export-content">
        <div className="export-visual">
          <div className="watermarked-image">
            <div className="watermark">
              FACEFORGE FORENSIC SUITE — INVESTIGATIVE USE ONLY — NOT FOR PUBLIC RELEASE
            </div>
            <div className="hd-sketch-placeholder">
              FINAL HD SKETCH (4096px)
            </div>
          </div>
        </div>

        <div className="export-sidebar">
          <div className="metadata-block">
            <h3>Evidence Metadata</h3>
            <div className="meta-row">
              <span className="meta-label">Case #</span>
              <span className="meta-value mono">{id}</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Officer</span>
              <span className="meta-value">Det. Sarah Chen</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Badge</span>
              <span className="meta-value">B-4271</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Date</span>
              <span className="meta-value mono">{new Date().toISOString().split('T')[0]}</span>
            </div>
            <div className="meta-row">
              <span className="meta-label">Iterations</span>
              <span className="meta-value">3</span>
            </div>
            <div className="meta-row hash-row">
              <span className="meta-label">SHA-256</span>
              <span className="meta-value mono truncate">b0aee043604824bd7a584742533b3d5b002bb525eb22119...</span>
            </div>
          </div>

          <div className="audit-panel-collapsible">
            <button 
              className="audit-toggle"
              onClick={() => setIsAuditOpen(!isAuditOpen)}
            >
              <div className="toggle-left">
                <ShieldCheck size={16} />
                <span>Audit Trail</span>
              </div>
              {isAuditOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
            
            {isAuditOpen && (
              <div className="audit-content">
                <div className="audit-item">
                  <span className="audit-time mono">14:05:12</span>
                  <span className="audit-action">SKETCH_GENERATED</span>
                </div>
                <div className="audit-item">
                  <span className="audit-time mono">14:03:00</span>
                  <span className="audit-action">FEATURE_LOCK (Eyes)</span>
                </div>
                <div className="audit-item">
                  <span className="audit-time mono">14:00:00</span>
                  <span className="audit-action">SESSION_CREATED</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {showMatches && (
        <div className="modal-overlay" onClick={() => setShowMatches(false)}>
          <div className="modal-content matches-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Database Matches</h3>
            </div>
            <div className="matches-body">
              <p>Scanning facial recognition databases...</p>
              <div className="progress-bar"><div className="progress-fill animated-fill"></div></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Export;
