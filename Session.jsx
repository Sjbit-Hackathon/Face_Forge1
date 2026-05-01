import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PenTool, ChevronDown, CheckCircle2, FileText, History, Search, ShieldCheck, Plus } from 'lucide-react';
import './Session.css';

const featureGroups = {
  Eyes: {
    Size: ["Small", "Medium", "Large", "Wider"],
    Shape: ["Round", "Almond", "Narrow"],
    Spacing: ["Close", "Normal", "Wide"],
    Depth: ["Deep", "Normal", "Protruding"]
  },
  Nose: {
    Width: ["Narrow", "Medium", "Broad"],
    Bridge: ["Straight", "Flat", "Curved"],
    Tip: ["Pointed", "Rounded"],
    Length: ["Short", "Medium", "Long"]
  },
  Mouth: {
    "Lip Size": ["Thin", "Medium", "Full"],
    Shape: ["Straight", "Curved", "Downturned"],
    Width: ["Narrow", "Medium", "Wide"]
  },
  Jaw: {
    Width: ["Narrow", "Medium", "Wide"],
    Jawline: ["Soft", "Defined", "Square"],
    Chin: ["Round", "Pointed", "Square"]
  }
};

const FeatureControls = ({ activeDropdown, setActiveDropdown, selections, onSelect }) => {
  return (
    <div 
      className="feature-controls-bar"
      onMouseLeave={() => setActiveDropdown(null)}
    >
      <div className="horizontal-control-pill">
        {Object.keys(featureGroups).map((group) => (
          <div 
            key={group}
            className="control-trigger-wrapper"
            onMouseEnter={() => setActiveDropdown(group)}
          >
            <button className={`control-trigger ${activeDropdown === group ? 'active' : ''}`}>
              {group} <ChevronDown size={14} className={`chevron ${activeDropdown === group ? 'rotated' : ''}`} />
            </button>
            
            {activeDropdown === group && (
              <div className="compact-dropdown-panel">
                <div className="dropdown-content">
                  {Object.entries(featureGroups[group]).map(([attrName, options]) => (
                    <div key={attrName} className="attr-row">
                      <span className="attr-label">{attrName}:</span>
                      <div className="pill-group">
                        {options.map((option) => {
                          const isActive = selections[group]?.[attrName] === option;
                          return (
                            <button
                              key={option}
                              className={`pill-btn ${isActive ? 'active' : ''}`}
                              onClick={() => {
                                onSelect(group, attrName, option);
                                setActiveDropdown(null);
                              }}
                            >
                              {option}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const Session = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // States
  const [hasSketch, setHasSketch] = useState(true); // Default true for UI mockup matching the image
  const [isGenerating, setIsGenerating] = useState(false);
  const [witnessInput, setWitnessInput] = useState('');
  const [refinementInput, setRefinementInput] = useState('');
  const [activeDropdown, setActiveDropdown] = useState(null);
  const [activeTab, setActiveTab] = useState('Versions');
  
  const [featureSelections, setFeatureSelections] = useState({
    Eyes: { Size: 'Medium', Shape: 'Almond', Spacing: 'Normal', Depth: 'Normal' }, 
    Nose: {}, Mouth: {}, Jaw: {}
  });

  const handleSelectFeature = (group, attrName, value) => {
    setFeatureSelections(prev => ({
      ...prev, [group]: { ...prev[group], [attrName]: value }
    }));
  };

  return (
    <div className="unified-session-layout">
      
      {/* LEFT COLUMN (60%) */}
      <div className="column-left">
        
        {/* Witness Statement Card */}
        <div className="card witness-card">
          <div className="card-header border-none">
            <div className="header-meta">
              <FileText size={18} className="text-accent" />
              <h3>Witness Statement</h3>
            </div>
          </div>
          <div className="card-body pt-0">
            <p className="card-subtext">Capture the officer's interview verbatim. The system extracts age, features, hair, distinguishing marks, then generates an HD composite.</p>
            <textarea 
              className="ui-textarea"
              placeholder="e.g. Male, late 30s, light olive skin, short dark brown hair receding at the temples, brown almond-shaped eyes, prominent straight nose, square jaw with light stubble, scar above the left eyebrow, neutral expression..."
              value={witnessInput}
              onChange={(e) => setWitnessInput(e.target.value)}
            />
          </div>
        </div>

        {/* Sketch Canvas Card */}
        <div className="card sketch-card">
          <div className="card-header canvas-header border-none">
            <div className="header-meta-col">
              <h3>Sketch Canvas</h3>
              <span className="meta-badge-text mono">Iteration v3 &nbsp; sha256: b0aee043604824bd...</span>
            </div>
            <button className="btn-success btn-sm">Export Report</button>
          </div>
          
          <div className="card-body canvas-body pt-0">
            <div className="canvas-viewport">
              {hasSketch ? (
                <div className="sketch-image-container">
                  <div className="hd-sketch-mock">
                    <div className="sketch-face-placeholder"></div>
                  </div>
                </div>
              ) : (
                <div className="wireframe-placeholder">AWAITING DESCRIPTION</div>
              )}
              
              <FeatureControls 
                activeDropdown={activeDropdown}
                setActiveDropdown={setActiveDropdown}
                selections={featureSelections}
                onSelect={handleSelectFeature}
              />
            </div>
          </div>
        </div>
      </div>

      {/* RIGHT COLUMN (40%) */}
      <div className="column-right">
        
        {/* AI Interrogator Card */}
        <div className="card">
          <div className="card-header border-none pb-2">
            <div className="header-meta">
              <h3>AI Interrogator</h3>
              <span className="gemini-badge">Gemini 2.0 Flash</span>
            </div>
          </div>
          <div className="card-body pt-0">
            <p className="card-subtext">Provide a witness statement to generate the initial sketch.</p>
            <button className="btn-primary full-width mt-2">
              <PenTool size={16} /> Generate Initial Sketch
            </button>
          </div>
        </div>

        {/* Iterative Refinement Card */}
        <div className="card">
          <div className="card-header border-none pb-2">
            <h3>Iterative refinement</h3>
          </div>
          <div className="card-body pt-0">
            <p className="card-subtext">Add a small correction; locked features remain fixed across iterations.</p>
            <textarea 
              className="ui-textarea sm mt-2"
              placeholder="e.g. Make the nose narrower with a slight bump on the bridge"
              value={refinementInput}
              onChange={(e) => setRefinementInput(e.target.value)}
            />
            <button className="btn-secondary full-width mt-4">
              <PenTool size={16} /> Refine sketch
            </button>
          </div>
        </div>

        {/* Version Panel Card */}
        <div className="card versions-card">
          <div className="card-header tabs-header">
            <button className={`tab-btn ${activeTab === 'Versions' ? 'active' : ''}`} onClick={() => setActiveTab('Versions')}>
              <History size={16}/> Versions
            </button>
            <button className={`tab-btn ${activeTab === 'Matches' ? 'active' : ''}`} onClick={() => setActiveTab('Matches')}>
              <Search size={16}/> Matches
            </button>
            <button className={`tab-btn ${activeTab === 'Audit' ? 'active' : ''}`} onClick={() => setActiveTab('Audit')}>
              <ShieldCheck size={16}/> Audit
            </button>
          </div>
          
          <div className="card-body bg-darker">
            {activeTab === 'Versions' && (
              <div className="thumbnail-grid">
                <div className="thumb-item"><span className="thumb-label">v1</span><div className="thumb-img t1"></div></div>
                <div className="thumb-item"><span className="thumb-label">v2</span><div className="thumb-img t2"></div></div>
                <div className="thumb-item active"><span className="thumb-label">v3</span><div className="thumb-img t3"></div></div>
                <div className="thumb-item new-iteration">
                  <Plus size={24} className="text-muted"/>
                  <span>New iteration</span>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default Session;
