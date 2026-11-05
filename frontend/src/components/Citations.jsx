import React from 'react';
import { X, ExternalLink } from 'lucide-react';

export default function Citations({ activeCitations, setActiveCitations }) {
  if (!activeCitations || activeCitations.length === 0) {
    return (
      <div className="citations-panel hidden">
        {/* We hide it via CSS class to allow for smooth transitions or flex changes, 
            but in this case, we could just return null. Returning the hidden panel keeps the DOM structure. */}
      </div>
    );
  }

  return (
    <div className="citations-panel">
      <div className="citations-header">
        <h3>Source Evidence</h3>
        <button 
          className="icon-btn"
          onClick={() => setActiveCitations(null)}
          title="Close sources panel"
        >
          <X size={18} />
        </button>
      </div>
      
      <div className="citations-content">
        {activeCitations.map((cit, idx) => (
          <div key={idx} className="citation-card" id={`citation-${idx + 1}`}>
            <div className="citation-card-header">
              <div className="citation-doc-name">{cit.document_name}</div>
              <div className="citation-badge">Page {cit.page_number}</div>
            </div>
            
            <div className="citation-card-body">
              <div className="citation-text">
                {cit.content}
              </div>
              
              {cit.base64_image && (
                <img 
                  className="citation-image"
                  src={`data:image/png;base64,${cit.base64_image}`} 
                  alt={`Source snippet from ${cit.document_name}`} 
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
