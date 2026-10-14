/** API client for backend communication */
// Use relative URL in production/Docker, absolute for local dev
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.DEV ? 'http://localhost:8000' : '');

// Better error handling for fetch
async function fetchWithErrorHandling(url, options = {}) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      // Try to get error message from response
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch (e) {
        // If response is not JSON, use status text
      }
      throw new Error(errorMessage);
    }
    return response;
  } catch (error) {
    if (error.message.includes('fetch')) {
      throw new Error(`Unable to connect to backend. Make sure the backend is running on ${API_BASE_URL || 'http://localhost:8000'}`);
    }
    throw error;
  }
}

/**
 * Upload a PDF document
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetchWithErrorHandling(`${API_BASE_URL}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  return response.json();
}

/**
 * Get all documents
 */
export async function getDocuments() {
  const response = await fetchWithErrorHandling(`${API_BASE_URL}/api/documents`);
  return response.json();
}

/**
 * Get a specific document
 */
export async function getDocument(documentId) {
  const response = await fetchWithErrorHandling(`${API_BASE_URL}/api/documents/${documentId}`);
  return response.json();
}

/**
 * Delete a document
 */
export async function deleteDocument(documentId) {
  const response = await fetchWithErrorHandling(`${API_BASE_URL}/api/documents/${documentId}`, {
    method: 'DELETE',
  });

  return response.json();
}

/**
 * Query documents
 */
export async function queryDocuments(query, topK = 5, documentId = null) {
  const params = new URLSearchParams({
    query,
    top_k: topK.toString(),
  });

  if (documentId) {
    params.append('document_id', documentId.toString());
  }

  const response = await fetchWithErrorHandling(`${API_BASE_URL}/api/query?${params.toString()}`);
  return response.json();
}

/**
 * Health check
 */
export async function healthCheck() {
  try {
    const response = await fetchWithErrorHandling(`${API_BASE_URL}/api/health`);
    return response.json();
  } catch (error) {
    throw new Error(`Backend health check failed: ${error.message}`);
  }
}

