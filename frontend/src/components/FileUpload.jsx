import { useState } from 'react';
import { uploadPdf } from '../services/api';
import { FiUploadCloud, FiCheckCircle } from 'react-icons/fi';

export const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setMessage('');
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setLoading(true);
    setMessage('');
    setError('');
    
    try {
      const data = await uploadPdf(file);
      setMessage(data.message);
      setFile(null); // Clear file after success
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="component-card">
      <h2 className="section-title">1. Upload Study Material</h2>
      <p className="section-subtitle">Upload a PDF syllabus or notes</p>
      
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

      {message && <div className="alert success-alert">{message}</div>}
      {error && <div className="alert error-alert">{error}</div>}
    </div>
  );
};
