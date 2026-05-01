import React from 'react';
import { InlineSelector } from './InlineSelector';
import './FeatureLocks.css';

const featureGroups = {
  Eyes: {
    Size: ["Small", "Medium", "Large", "Wider"],
    Shape: ["Round", "Almond", "Narrow"],
    Spacing: ["Close", "Normal", "Wide"],
    Depth: ["Deep", "Normal", "Protruding"]
  },
  Nose: {
    Size: ["Small", "Medium", "Large"],
    Shape: ["Straight", "Hooked", "Button", "Broad"],
    Bridge: ["High", "Low", "Bump"]
  },
  Mouth: {
    Fullness: ["Thin", "Average", "Full"],
    Width: ["Narrow", "Average", "Wide"],
    Shape: ["Bow", "Flat", "Downturned"]
  },
  Jaw: {
    Shape: ["Square", "Round", "Pointy", "Oval"],
    Prominence: ["Weak", "Average", "Strong"],
    Width: ["Narrow", "Wide"]
  }
};

export const FeatureLocks = () => {
  const handleSelectionChange = (data) => {
    console.log('Selection changed:', data);
  };

  return (
    <div className="feature-locks-panel">
      <div className="panel-header">
        <h3 className="panel-title">FEATURE LOCKS</h3>
      </div>
      
      <div className="selectors-grid">
        {Object.entries(featureGroups).map(([group, attributes]) => (
          <div className="selector-wrapper" key={group}>
            <InlineSelector 
              group={group} 
              attributes={attributes} 
              onChange={handleSelectionChange} 
            />
          </div>
        ))}
      </div>
      
      <p className="panel-footer-text">
        Locked features will be preserved verbatim in the next iteration.
      </p>
    </div>
  );
};
