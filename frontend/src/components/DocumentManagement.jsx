import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { fetchUserDocuments, deleteDocument } from '../services/api';

export const DocumentManagement = ({ onDocumentsChanged, refreshTrigger }) => {
  const { token, isAuthenticated } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const loadDocuments = useCallback(async () => {
    if (!isAuthenticated) {
      setDocuments([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchUserDocuments(token);
      setDocuments(data.documents || []);
    } catch (err) {
      setError(err.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, token]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments, refreshTrigger]);

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"? All its vector data will be removed.`)) {
      return;
    }

    setDeletingId(docId);
    try {
      await deleteDocument(docId, token);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      if (onDocumentsChanged) {
        onDocumentsChanged();
      }
    } catch (err) {
      alert(`Error deleting document: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="doc-mgmt-container card">
        <div className="doc-mgmt-header">
          <h3>📁 My Study Documents</h3>
        </div>
        <div className="doc-empty-state">
          <p>Please sign in to view and manage your uploaded documents.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="doc-mgmt-container card">
      <div className="doc-mgmt-header">
        <div className="doc-header-title">
          <h3>📁 My Study Documents</h3>
          <span className="doc-count-badge">{documents.length}</span>
        </div>
        <button
          className="refresh-btn"
          onClick={loadDocuments}
          disabled={loading}
          title="Refresh documents list"
        >
          {loading ? '⟳...' : '⟳'}
        </button>
      </div>

      {error && <div className="doc-error-alert">⚠️ {error}</div>}

      {loading && documents.length === 0 ? (
        <div className="doc-loading">Loading documents...</div>
      ) : documents.length === 0 ? (
        <div className="doc-empty-state">
          <p>No documents uploaded yet.</p>
          <span>Upload a syllabus or study notes PDF to begin revision.</span>
        </div>
      ) : (
        <div className="doc-list">
          {documents.map((doc) => (
            <div key={doc.id} className="doc-item">
              <div className="doc-icon">📄</div>
              <div className="doc-details">
                <div className="doc-name" title={doc.original_filename}>
                  {doc.original_filename}
                </div>
                <div className="doc-meta">
                  <span className="doc-size">{formatFileSize(doc.file_size)}</span>
                  <span className="doc-chunks">{doc.chunk_count} chunks</span>
                  <span className="doc-date">{formatDate(doc.created_at)}</span>
                </div>
              </div>
              <div className="doc-actions">
                <span className={`doc-status-pill status-${doc.status}`}>
                  {doc.status}
                </span>
                <button
                  className="doc-delete-btn"
                  onClick={() => handleDelete(doc.id, doc.original_filename)}
                  disabled={deletingId === doc.id}
                  title="Delete document and remove vector chunks"
                >
                  {deletingId === doc.id ? '...' : '🗑️'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
