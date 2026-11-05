import React, { useRef, useState } from 'react';
import { uploadDocument, deleteDocument } from '../services/api';
import { UploadCloud, FileText, CheckCircle2, Clock, Trash2, X, FileSearch } from 'lucide-react';

export default function Sidebar({ 
  documents, 
  fetchDocs, 
  selectedDocumentIds, 
  setSelectedDocumentIds, 
  searchScope, 
  setSearchScope,
  isCollapsed
}) {
  const fileInputRef = useRef();
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadClick = () => {
    if (!isUploading) fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setIsUploading(true);
      await uploadDocument(file);
      await fetchDocs();
    } catch (err) {
      alert("Error uploading document: " + err.message);
    } finally {
      setIsUploading(false);
      e.target.value = null; // reset
    }
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    try {
      await deleteDocument(id);
      setSelectedDocumentIds(prev => prev.filter(docId => docId !== id));
      await fetchDocs();
    } catch (err) {
      alert("Error deleting document");
    }
  };

  const handleToggleSelect = (id) => {
    setSelectedDocumentIds(prev => {
      if (prev.includes(id)) {
        return prev.filter(docId => docId !== id);
      } else {
        return [...prev, id];
      }
    });
  };

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-content">
        
        {/* Upload Zone */}
        <div>
          <div className="section-title">Documents</div>
          <div 
            className={`upload-zone ${isUploading ? 'disabled' : ''}`} 
            onClick={handleUploadClick}
          >
            <UploadCloud className="upload-icon" size={32} />
            <div className="upload-text">
              {isUploading ? 'Uploading...' : 'Drop PDF here or click'}
            </div>
            {!isUploading && <div className="upload-subtext">PDF files supported</div>}
          </div>
          <input 
            type="file" 
            accept=".pdf" 
            ref={fileInputRef} 
            style={{ display: 'none' }} 
            onChange={handleFileChange} 
          />
        </div>

        {/* Scope Selector */}
        {documents.length > 0 && (
          <div className="scope-selector">
            <div className="section-title">Query Scope</div>
            <label className="scope-option">
              <input 
                type="radio" 
                name="scope" 
                value="selected"
                checked={searchScope === 'selected'}
                onChange={() => setSearchScope('selected')}
              />
              <FileSearch size={16} />
              Selected ({selectedDocumentIds.length})
            </label>
            <label className="scope-option">
              <input 
                type="radio" 
                name="scope" 
                value="all"
                checked={searchScope === 'all'}
                onChange={() => setSearchScope('all')}
              />
              <FileText size={16} />
              All Documents ({documents.length})
            </label>
          </div>
        )}

        {/* Document List */}
        <div className="doc-list">
          <div className="section-title">Indexed Files</div>
          {documents.map(doc => {
            const isSelected = selectedDocumentIds.includes(doc.id);
            const isIndexed = doc.status && doc.status.toLowerCase() === 'indexed';
            
            return (
              <div 
                key={doc.id} 
                className={`doc-item ${isSelected ? 'selected' : ''}`}
                onClick={() => handleToggleSelect(doc.id)}
              >
                <div className="doc-info">
                  <div className="doc-name" title={doc.filename}>{doc.filename}</div>
                  <div className={`doc-status ${isIndexed ? 'success' : 'processing'}`}>
                    {isIndexed ? <CheckCircle2 size={12}/> : <Clock size={12}/>}
                    {doc.status || 'Processing...'}
                  </div>
                </div>
                <div className="doc-actions">
                  <button 
                    className="delete-btn" 
                    onClick={(e) => handleDelete(doc.id, e)} 
                    title="Remove Document"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            );
          })}
          {documents.length === 0 && (
            <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', textAlign: 'center', marginTop: '10px' }}>
              No documents uploaded yet.
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
