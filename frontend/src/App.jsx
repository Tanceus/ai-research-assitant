import { useState, useEffect } from 'react';
import { uploadDocument, getDocuments, deleteDocument, queryDocuments } from './api';
import './App.css';

function App() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [connectionError, setConnectionError] = useState(null);

  useEffect(() => {
    checkConnection();
    loadDocuments();
  }, []);

  const checkConnection = async () => {
    try {
      const { healthCheck } = await import('./api');
      await healthCheck();
      setConnectionError(null);
    } catch (error) {
      setConnectionError('Unable to connect to backend. Make sure the backend is running on http://localhost:8000');
      console.error('Connection error:', error);
    }
  };

  const loadDocuments = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
      setConnectionError(null);
    } catch (error) {
      console.error('Error loading documents:', error);
      if (error.message.includes('connect') || error.message.includes('fetch')) {
        setConnectionError('Cannot connect to backend. Please ensure the backend server is running on http://localhost:8000');
      }
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      alert('Please upload a PDF file');
      return;
    }

    setLoading(true);
    setUploadStatus('Uploading...');

    try {
      await uploadDocument(file);
      setUploadStatus('Upload successful!');
      await loadDocuments();
      setTimeout(() => setUploadStatus(''), 3000);
    } catch (error) {
      setUploadStatus(`Upload failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await deleteDocument(documentId);
      await loadDocuments();
      if (selectedDocument === documentId) {
        setSelectedDocument(null);
      }
    } catch (error) {
      alert(`Failed to delete document: ${error.message}`);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      alert('Please enter a query');
      return;
    }

    setLoading(true);
    try {
      const response = await queryDocuments(query, 5, selectedDocument || null);
      setResults(response);
    } catch (error) {
      alert(`Query failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(2)} MB`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Research Assistant</h1>
        <p>Upload PDFs and query them using AI-powered search</p>
      </header>

      <main className="app-main">
        <div className="container">
          {/* Connection Error Banner */}
          {connectionError && (
            <div className="error-banner">
              <strong>⚠️ Connection Error:</strong> {connectionError}
              <button onClick={checkConnection} className="retry-button">Retry</button>
            </div>
          )}
          
          {/* Document Upload Section */}
          <section className="section">
            <h2>Upload Document</h2>
            <div className="upload-area">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={loading}
                className="file-input"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="file-label">
                {loading ? 'Uploading...' : 'Choose PDF File'}
              </label>
              {uploadStatus && (
                <p className={`upload-status ${uploadStatus.includes('success') ? 'success' : 'error'}`}>
                  {uploadStatus}
                </p>
              )}
            </div>
          </section>

          {/* Documents List Section */}
          <section className="section">
            <h2>Uploaded Documents ({documents.length})</h2>
            {documents.length === 0 ? (
              <p className="empty-state">No documents uploaded yet</p>
            ) : (
              <div className="documents-grid">
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    className={`document-card ${selectedDocument === doc.id ? 'selected' : ''}`}
                    onClick={() => setSelectedDocument(doc.id === selectedDocument ? null : doc.id)}
                  >
                    <div className="document-header">
                      <h3>{doc.title || doc.filename}</h3>
                      <button
                        className="delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(doc.id);
                        }}
                      >
                        ×
                      </button>
                    </div>
                    <div className="document-info">
                      <p><strong>Author:</strong> {doc.author || 'N/A'}</p>
                      <p><strong>Pages:</strong> {doc.pages || 'N/A'}</p>
                      <p><strong>Size:</strong> {formatFileSize(doc.file_size)}</p>
                      <p><strong>Uploaded:</strong> {formatDate(doc.upload_date)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Query Section */}
          <section className="section">
            <h2>Query Documents</h2>
            <div className="query-area">
              <div className="query-input-group">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Enter your query..."
                  className="query-input"
                  onKeyPress={(e) => e.key === 'Enter' && handleQuery()}
                  disabled={loading}
                />
                <button
                  onClick={handleQuery}
                  disabled={loading || !query.trim()}
                  className="query-button"
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
              {selectedDocument && (
                <p className="filter-info">
                  Filtering results from: {documents.find(d => d.id === selectedDocument)?.filename}
                </p>
              )}
            </div>

            {/* Results Section */}
            {results && (
              <div className="results-section">
                <h3>Search Results ({results.count})</h3>
                {results.results.length === 0 ? (
                  <p className="empty-state">No results found</p>
                ) : (
                  <div className="results-list">
                    {results.results.map((result, index) => (
                      <div key={index} className="result-card">
                        <div className="result-header">
                          <span className="result-rank">#{result.rank}</span>
                          <span className="result-score">
                            Similarity: {(result.similarity_score * 100).toFixed(2)}%
                          </span>
                          {result.page_number && (
                            <span className="result-page">Page {result.page_number}</span>
                          )}
                        </div>
                        <div className="result-content">
                          {result.content}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </section>
        </div>
      </main>

      <footer className="app-footer">
        <p>AI Research Assistant - Powered by FastAPI & React</p>
      </footer>
    </div>
  );
}

export default App;

