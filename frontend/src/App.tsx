import React, { useState, useEffect } from 'react';
import FileUpload from './components/FileUpload';
import ContradictionList from './components/ContradictionList';
import DocumentList from './components/DocumentList';
import { 
  apiService, 
  AnalysisResult, 
  UploadResponse, 
  Document, 
  Contradiction 
} from './services/api';
import './App.css';

interface AppState {
  documents: Document[];
  contradictions: Contradiction[];
  loading: boolean;
  analyzing: boolean;
  error: string | null;
  activeTab: 'upload' | 'results' | 'documents';
  uploadResponse: UploadResponse | null;
}

const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    documents: [],
    contradictions: [],
    loading: false,
    analyzing: false,
    error: null,
    activeTab: 'upload',
    uploadResponse: null
  });

  // Load existing results on component mount
  useEffect(() => {
    loadExistingResults();
  }, []);

  const loadExistingResults = async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const results = await apiService.getContradictionResults();
      setState(prev => ({
        ...prev,
        documents: results.documents,
        contradictions: results.contradictions,
        loading: false
      }));
    } catch (error) {
      console.error('Failed to load existing results:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to load existing results',
        loading: false
      }));
    }
  };

  const handleUploadComplete = (response: UploadResponse) => {
    setState(prev => ({
      ...prev,
      uploadResponse: response,
      error: response.failed_uploads > 0 ? 
        `${response.failed_uploads} file(s) failed to upload` : null
    }));

    // Show success message
    if (response.successful_uploads > 0) {
      alert(`Successfully uploaded ${response.successful_uploads} file(s)!`);
    }
  };

  const handleUploadStart = () => {
    setState(prev => ({
      ...prev,
      uploadResponse: null,
      error: null
    }));
  };

  const handleAnalyzeDocuments = async () => {
    setState(prev => ({ ...prev, analyzing: true, error: null }));

    try {
      const results: AnalysisResult = await apiService.analyzeDocuments();
      
      setState(prev => ({
        ...prev,
        documents: results.documents,
        contradictions: results.contradictions,
        analyzing: false,
        activeTab: 'results'
      }));

      // Show analysis summary
      const message = results.summary.total_contradictions > 0 
        ? `Analysis complete! Found ${results.summary.total_contradictions} contradiction(s) across ${results.summary.total_documents} document(s).`
        : `Analysis complete! No contradictions found across ${results.summary.total_documents} document(s). All documents appear consistent! ✅`;
      
      alert(message);

    } catch (error) {
      console.error('Analysis failed:', error);
      setState(prev => ({
        ...prev,
        error: 'Analysis failed. Please try again.',
        analyzing: false
      }));
    }
  };

  const handleDeleteDocument = async (docId: number) => {
    try {
      await apiService.deleteDocument(docId);
      
      // Reload results after deletion
      await loadExistingResults();
      
      alert('Document deleted successfully');
    } catch (error) {
      console.error('Failed to delete document:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to delete document'
      }));
    }
  };

  const handleClearAllData = async () => {
    if (window.confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
      try {
        await apiService.clearAllData();
        setState({
          documents: [],
          contradictions: [],
          loading: false,
          analyzing: false,
          error: null,
          activeTab: 'upload',
          uploadResponse: null
        });
        alert('All data cleared successfully');
      } catch (error) {
        console.error('Failed to clear data:', error);
        setState(prev => ({
          ...prev,
          error: 'Failed to clear data'
        }));
      }
    }
  };

  const setActiveTab = (tab: 'upload' | 'results' | 'documents') => {
    setState(prev => ({ ...prev, activeTab: tab }));
  };

  return (
    <div className="App">
      <header style={{ 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '20px 0',
        marginBottom: '20px'
      }}>
        <div className="container">
          <h1>🔍 Smart Doc Checker</h1>
          <p>Detect contradictions across multiple documents automatically</p>
        </div>
      </header>

      <div className="container">
        {/* Error Alert */}
        {state.error && (
          <div className="alert alert-error">
            <strong>Error:</strong> {state.error}
            <button 
              onClick={() => setState(prev => ({ ...prev, error: null }))}
              style={{ float: 'right', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${state.activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            📤 Upload & Analyze
          </button>
          <button 
            className={`nav-tab ${state.activeTab === 'results' ? 'active' : ''}`}
            onClick={() => setActiveTab('results')}
          >
            ⚠️ Contradictions ({state.contradictions.length})
          </button>
          <button 
            className={`nav-tab ${state.activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            📂 Documents ({state.documents.length})
          </button>
        </div>

        {/* Tab Content */}
        {state.activeTab === 'upload' && (
          <>
            <FileUpload 
              onUploadComplete={handleUploadComplete}
              onUploadStart={handleUploadStart}
            />

            {state.uploadResponse && (
              <div className="card">
                <h3>Upload Results</h3>
                <div className="stats-grid">
                  <div className="stat-card" style={{ background: '#28a745' }}>
                    <span className="stat-number">{state.uploadResponse.successful_uploads}</span>
                    <span className="stat-label">Successful</span>
                  </div>
                  <div className="stat-card" style={{ background: '#dc3545' }}>
                    <span className="stat-number">{state.uploadResponse.failed_uploads}</span>
                    <span className="stat-label">Failed</span>
                  </div>
                </div>

                {state.uploadResponse.successful_uploads > 0 && (
                  <div style={{ marginTop: '20px' }}>
                    <button 
                      onClick={handleAnalyzeDocuments}
                      disabled={state.analyzing}
                      className="btn btn-success"
                      style={{ fontSize: '16px', padding: '12px 24px' }}
                    >
                      {state.analyzing ? '🔍 Analyzing...' : '🧠 Analyze Documents for Contradictions'}
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Analysis Status */}
            {state.analyzing && (
              <div className="card">
                <div className="loading">
                  <div className="spinner"></div>
                  <h3>Analyzing Documents...</h3>
                  <p>🔍 Extracting text from documents</p>
                  <p>🧠 Parsing clauses using NLP</p>
                  <p>⚖️ Detecting contradictions</p>
                  <p>Please wait, this may take a moment...</p>
                </div>
              </div>
            )}
          </>
        )}

        {state.activeTab === 'results' && (
          <ContradictionList 
            contradictions={state.contradictions}
            loading={state.loading}
          />
        )}

        {state.activeTab === 'documents' && (
          <DocumentList 
            documents={state.documents}
            onDeleteDocument={handleDeleteDocument}
            loading={state.loading}
          />
        )}

        {/* Statistics Card */}
        {(state.documents.length > 0 || state.contradictions.length > 0) && (
          <div className="card">
            <h3>📊 Summary Statistics</h3>
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-number">{state.documents.length}</span>
                <span className="stat-label">Documents Processed</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">{state.contradictions.length}</span>
                <span className="stat-label">Contradictions Found</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {state.contradictions.filter(c => c.severity === 'critical' || c.severity === 'high').length}
                </span>
                <span className="stat-label">High Priority Issues</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">
                  {Array.from(new Set(state.contradictions.map(c => c.clause_type))).length}
                </span>
                <span className="stat-label">Clause Types Affected</span>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="card">
          <h3>🛠️ Actions</h3>
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button 
              onClick={loadExistingResults}
              disabled={state.loading}
              className="btn"
            >
              🔄 Refresh Results
            </button>
            
            <button 
              onClick={handleAnalyzeDocuments}
              disabled={state.analyzing}
              className="btn btn-success"
            >
              {state.analyzing ? '🔍 Analyzing...' : '🧠 Re-analyze All Documents'}
            </button>
            
            <button 
              onClick={handleClearAllData}
              className="btn btn-danger"
            >
              🗑️ Clear All Data
            </button>
          </div>
        </div>

        {/* Footer */}
        <footer style={{ 
          textAlign: 'center', 
          padding: '20px', 
          marginTop: '40px', 
          borderTop: '1px solid #ddd',
          color: '#666'
        }}>
          <p>Smart Doc Checker MVP - Powered by NLP and AI</p>
          <p>Built with React, FastAPI, spaCy, and SQLite</p>
        </footer>
      </div>
    </div>
  );
};

export default App;