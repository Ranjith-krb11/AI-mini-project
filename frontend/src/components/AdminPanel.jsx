import { useState } from 'react';
import { fetchDatabaseContents } from '../services/api';
import { FiDatabase, FiRefreshCw } from 'react-icons/fi';

export const AdminPanel = () => {
  const [data, setData] = useState([]);
  const [totalItems, setTotalItems] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const handleFetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await fetchDatabaseContents();
      setTotalItems(result.total_items);
      setData(result.data);
      setIsOpen(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="component-card admin-panel">
      <h2 className="section-title">
        <FiDatabase className="icon-inline" /> 🛠️ Admin Panel
      </h2>
      
      <button 
        className="btn secondary-btn" 
        onClick={handleFetchData}
        disabled={loading}
      >
        {loading ? <FiRefreshCw className="icon-spin" /> : 'View Database Contents'}
      </button>

      {error && <div className="alert error-alert">{error}</div>}

      {isOpen && totalItems !== null && (
        <div className="database-view">
          {totalItems === 0 ? (
            <div className="alert info-alert">The database is currently empty.</div>
          ) : (
            <>
              <div className="alert success-alert">Database contains {totalItems} chunks.</div>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Source File</th>
                      <th>Text Content</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.map((row, idx) => (
                      <tr key={idx}>
                        <td className="col-id">{row.id}</td>
                        <td className="col-source">{row.source}</td>
                        <td className="col-content">
                          <div className="content-scroll">{row.content}</div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};
