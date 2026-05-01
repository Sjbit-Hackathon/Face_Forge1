import React from 'react';
import { ChevronLeft, Download, PenTool, CheckCircle, RotateCcw, Clock, Target, ShieldCheck } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { FeatureLocks } from '../components/FeatureLocks';
import './CaseDetail.css';

const CaseDetail = () => {
  const { id } = useParams();

  return (
    <div className="case-detail">
      <div className="case-header">
        <div className="case-header-left">
          <Link to="/dashboard" className="back-link"><ChevronLeft size={16} /> Cases</Link>
          <h2 className="case-id-title">{id || 'CASE-20260429-4257'}</h2>
          <span className="status-badge exported">exported</span>
          <span className="case-meta">v3 · Lead Detective Sarah Chen (Badge B-4271)</span>
        </div>
        <div className="case-header-right">
          <button className="btn-secondary"><Download size={16} /> Export forensic PDF</button>
          <button className="btn-text">Close case</button>
        </div>
      </div>

      <div className="case-grid">
        <div className="grid-left">
          <div className="panel witness-panel">
            <h3 className="panel-title-with-icon"><PenTool size={18} className="text-red" /> Witness statement</h3>
            <p className="panel-desc">
              Capture the officer's interview verbatim. The system extracts age, features, hair, distinguishing marks, then generates an HD composite.
            </p>
            <textarea 
              className="statement-input"
              defaultValue="e.g. Male, late 30s, light olive skin, short dark brown hair receding at the temples, brown almond-shaped eyes, prominent straight nose, square jaw with light stubble, scar above the left eyebrow, neutral expression..."
            />
          </div>

          <FeatureLocks />

          <div className="panel sketch-panel">
            <h3 className="panel-title">Sketch canvas</h3>
            <p className="panel-desc">Iteration v3 <span className="mono-text">sha256: b0aee043604824bd...</span></p>
            <div className="sketch-image-placeholder">
              {/* Image would go here. using a generic background for demo */}
              <div className="dummy-image">SKETCH IMAGE</div>
            </div>
          </div>
        </div>

        <div className="grid-right">
          <div className="panel refinement-panel">
            <h3 className="panel-title">Iterative refinement</h3>
            <p className="panel-desc">Add a small correction; locked features remain fixed across iterations.</p>
            <textarea 
              className="refinement-input"
              defaultValue="e.g. Make the nose narrower with a slight bump on the bridge"
            />
            <button className="btn-secondary full-width mt-16"><PenTool size={16} /> Refine sketch</button>
          </div>

          <div className="panel versions-panel">
            <div className="tabs">
              <button className="tab active"><RotateCcw size={14} /> Versions</button>
              <button className="tab"><Target size={14} /> Matches</button>
              <button className="tab"><ShieldCheck size={14} /> Audit</button>
            </div>
            
            <div className="thumbnails-grid">
              <div className="thumbnail">
                <span className="version-badge">v1</span>
                <div className="dummy-thumb">v1 Image</div>
              </div>
              <div className="thumbnail">
                <span className="version-badge">v2</span>
                <div className="dummy-thumb">v2 Image</div>
              </div>
              <div className="thumbnail active">
                <span className="version-badge">v3</span>
                <div className="dummy-thumb">v3 Image</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaseDetail;
