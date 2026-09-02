import { useState } from 'react';
import { uploadPdf } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { FiUploadCloud, FiCheckCircle } from 'react-icons/fi';

const MAX_SIZE_BYTES = 15 * 1024 * 1024; // 15MB

export const FileUpload = ({ onUploadSuccess }) => {
  const { token, isAuthenticated } = useAuth();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      
      // Client-side quick checks
      if (!selected.name.toLowerCase().endsWith('.pdf')) {
        setError('Only PDF documents (.pdf) are supported.');
        setFile(null);
        return;
      }

      if (selected.size === 0) {
        setError('The selected file is empty (0 bytes).');
        setFile(null);
        return;
      }

      if (selected.size > MAX_SIZE_BYTES) {
        setError('File exceeds the 15MB limit.');
        setFile(null);
        return;
      }

      setFile(selected);
      setMessage('');
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    if (!isAuthenticated) {
      setError('Please sign in or create an account to upload study materials.');
      return;
    }
    
    setLoading(true);
    setMessage('');
    setError('');
    
    try {
      const data = await uploadPdf(file, token);
      setMessage(data.message);
      setFile(null); // Clear file after success
      if (onUploadSuccess) {
        onUploadSuccess(data);
      }
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="component-card">
      <h2 className="section-title">1. Upload Study Material</h2>
      <p className="section-subtitle">PDF syllabus, slides, or lecture notes (Max 15MB)</p>
      
      <div className="file-upload-container">
        <label className="file-upload-label">
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileChange} 
            style={{ display: 'none' }} 
          />
          <div className="upload-box">
            {file ? (
              <div className="file-selected">
                <FiCheckCircle className="icon success-icon" />
                <span>{file.name}</span>
              </div>
            ) : (
              <div className="file-prompt">
                <FiUploadCloud className="icon" />
                <span>Click or drag PDF to upload</span>
              </div>
            )}
          </div>
        </label>
        
        <button 
          className="btn primary-btn" 
          onClick={handleUpload} 
          disabled={!file || loading}
        >
          {loading ? 'Processing Document...' : 'Process Document'}
        </button>
      </div>

      {message && <div className="alert success-alert">✅ {message}</div>}
      {error && <div className="alert error-alert">⚠️ {error}</div>}
    </div>
  );
};
