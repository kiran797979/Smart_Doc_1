import React from 'react';
import { Contradiction } from '../services/api';

interface ContradictionListProps {
  contradictions: Contradiction[];
  loading?: boolean;
}

const ContradictionList: React.FC<ContradictionListProps> = ({ contradictions, loading }) => {
  if (loading) {
    return (
      <div className="card">
        <h2>Contradictions Found</h2>
        <div className="loading">
          <div className="spinner"></div>
          <p>Analyzing documents for contradictions...</p>
        </div>
      </div>
    );
  }

  if (contradictions.length === 0) {
    return (
      <div className="card">
        <h2>Contradictions Found</h2>
        <div className="alert alert-success">
          <h3>✅ No contradictions detected!</h3>
          <p>All analyzed documents appear to be consistent with each other.</p>
        </div>
      </div>
    );
  }

  const getSeverityClass = (severity: string): string => {
    return `severity-${severity.toLowerCase()}`;
  };

  const getSeverityIcon = (severity: string): string => {
    switch (severity.toLowerCase()) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '🔶';
      case 'low': return '🔹';
      default: return '📝';
    }
  };

  // Group contradictions by severity
  const groupedContradictions = contradictions.reduce((acc, contradiction) => {
    const severity = contradiction.severity.toLowerCase();
    if (!acc[severity]) {
      acc[severity] = [];
    }
    acc[severity].push(contradiction);
    return acc;
  }, {} as Record<string, Contradiction[]>);

  const severityOrder = ['critical', 'high', 'medium', 'low'];

  return (
    <div className="card">
      <h2>Contradictions Found ({contradictions.length})</h2>
      
      {/* Summary */}
      <div className="alert alert-warning">
        <h3>⚠️ Document Contradictions Detected</h3>
        <p>Found {contradictions.length} contradiction(s) across your documents. Review and resolve these inconsistencies.</p>
      </div>

      {/* Contradictions by severity */}
      {severityOrder.map(severity => {
        const items = groupedContradictions[severity];
        if (!items || items.length === 0) return null;

        return (
          <div key={severity} style={{ marginTop: '20px' }}>
            <h3>
              {getSeverityIcon(severity)} {severity.charAt(0).toUpperCase() + severity.slice(1)} Priority ({items.length})
            </h3>
            
            <table className="table">
              <thead>
                <tr>
                  <th>Clause Type</th>
                  <th>Documents</th>
                  <th>Values</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {items.map((contradiction) => (
                  <tr key={contradiction.id}>
                    <td>
                      <strong className={getSeverityClass(contradiction.severity)}>
                        {contradiction.clause_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </strong>
                    </td>
                    <td>
                      {contradiction.documents.map((doc, index) => (
                        <div key={index} style={{ marginBottom: '5px' }}>
                          📄 <strong>{doc.filename}</strong>
                        </div>
                      ))}
                    </td>
                    <td>
                      {contradiction.documents.map((doc, index) => (
                        <div key={index} style={{ marginBottom: '5px' }}>
                          <code>{doc.value}</code>
                        </div>
                      ))}
                    </td>
                    <td>
                      <details>
                        <summary style={{ cursor: 'pointer' }}>View Details</summary>
                        <div style={{ marginTop: '10px', fontSize: '0.9em' }}>
                          <p><strong>Summary:</strong> {contradiction.summary}</p>
                          {contradiction.details && (
                            <div>
                              <strong>Analysis:</strong>
                              <pre style={{ 
                                background: '#f8f9fa', 
                                padding: '10px', 
                                borderRadius: '4px',
                                fontSize: '0.8em',
                                overflow: 'auto'
                              }}>
                                {JSON.stringify(contradiction.details, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      </details>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      })}

      {/* Recommendations */}
      <div style={{ marginTop: '30px' }}>
        <h3>💡 Recommendations</h3>
        <div className="alert alert-warning">
          <ul style={{ margin: 0, paddingLeft: '20px' }}>
            {groupedContradictions.critical && (
              <li>🚨 <strong>Critical:</strong> Address critical contradictions immediately as they may affect legal validity</li>
            )}
            {groupedContradictions.high && (
              <li>⚠️ <strong>High Priority:</strong> Review high-priority contradictions that may cause confusion or disputes</li>
            )}
            {contradictions.some(c => c.clause_type === 'notice_period') && (
              <li>📅 Standardize notice period requirements across all documents</li>
            )}
            {contradictions.some(c => c.clause_type === 'working_hours') && (
              <li>⏰ Align working hours specifications in all relevant documents</li>
            )}
            {contradictions.some(c => c.clause_type === 'salary') && (
              <li>💰 Verify and correct salary information discrepancies</li>
            )}
            <li>📋 Consider creating a master document template to ensure consistency</li>
            <li>🔍 Regularly audit documents for consistency when making updates</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ContradictionList;