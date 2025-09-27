import React from 'react';
import { Document } from '../services/api';

interface DocumentListProps {
  documents: Document[];
  onDeleteDocument?: (docId: number) => void;
  loading?: boolean;
}

const DocumentList: React.FC<DocumentListProps> = ({ 
  documents, 
  onDeleteDocument, 
  loading 
}) => {
  if (loading) {
    return (
      <div className="card">
        <h2>Processed Documents</h2>
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading documents...</p>
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="card">
        <h2>Processed Documents</h2>
        <div className="alert alert-warning">
          <p>📄 No documents have been processed yet.</p>
          <p>Upload and analyze documents to see them here.</p>
        </div>
      </div>
    );
  }

  const formatDate = (dateString?: string): string => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleString();
  };

  const getClauseCount = (clauses: Record<string, any>): number => {
    return Object.keys(clauses).length;
  };

  const handleDelete = (docId: number, filename: string) => {
    if (window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      onDeleteDocument?.(docId);
    }
  };

  return (
    <div className="card">
      <h2>Processed Documents ({documents.length})</h2>
      
      <table className="table">
        <thead>
          <tr>
            <th>Document</th>
            <th>Clauses Found</th>
            <th>Status</th>
            <th>Processed</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {documents.map((doc) => (
            <tr key={doc.id}>
              <td>
                <div>
                  <strong>📄 {doc.filename}</strong>
                  <br />
                  <small style={{ color: '#666' }}>
                    {doc.file_path}
                  </small>
                </div>
              </td>
              <td>
                <div>
                  <strong>{getClauseCount(doc.clauses)}</strong>
                  <br />
                  <small style={{ color: '#666' }}>
                    {Object.keys(doc.clauses).slice(0, 3).join(', ')}
                    {Object.keys(doc.clauses).length > 3 && '...'}
                  </small>
                </div>
              </td>
              <td>
                <span className={`status-${doc.status}`}>
                  {doc.status === 'success' ? '✅ Success' : '❌ Failed'}
                </span>
              </td>
              <td>
                <small>{formatDate(doc.created_at)}</small>
              </td>
              <td>
                <div style={{ display: 'flex', gap: '5px' }}>
                  <button
                    onClick={() => {
                      // Show document details in a modal or expand
                      const clausesText = JSON.stringify(doc.clauses, null, 2);
                      alert(`Clauses for ${doc.filename}:\n\n${clausesText}`);
                    }}
                    className="btn"
                    style={{ fontSize: '12px', padding: '5px 10px' }}
                  >
                    View Details
                  </button>
                  
                  {onDeleteDocument && doc.id && (
                    <button
                      onClick={() => handleDelete(doc.id!, doc.filename)}
                      className="btn btn-danger"
                      style={{ fontSize: '12px', padding: '5px 10px' }}
                    >
                      Delete
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Clause Types Summary */}
      <div style={{ marginTop: '20px' }}>
        <h3>📊 Clause Types Summary</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
          {(() => {
            const clauseTypes: Record<string, number> = {};
            documents.forEach(doc => {
              Object.keys(doc.clauses).forEach(clause => {
                clauseTypes[clause] = (clauseTypes[clause] || 0) + 1;
              });
            });

            return Object.entries(clauseTypes)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 6)
              .map(([clauseType, count]) => (
                <div key={clauseType} style={{ 
                  background: '#f8f9fa', 
                  padding: '10px', 
                  borderRadius: '4px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontWeight: 'bold', color: '#007bff' }}>{count}</div>
                  <div style={{ fontSize: '0.9em' }}>
                    {clauseType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </div>
                </div>
              ));
          })()}
        </div>
      </div>
    </div>
  );
};

export default DocumentList;