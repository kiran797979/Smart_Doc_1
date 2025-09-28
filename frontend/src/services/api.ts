import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://smart-doc-1-3.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
});

// Types
export interface Document {
  id?: number;
  filename: string;
  file_path: string;
  clauses: Record<string, any>;
  status: string;
  created_at?: string;
}

export interface Contradiction {
  id: number;
  clause_type: string;
  severity: string;
  summary: string;
  documents: Array<{
    filename: string;
    doc_id?: number;
    value: string;
  }>;
  details?: Record<string, any>;
  created_at?: string;
}

export interface AnalysisResult {
  documents: Document[];
  contradictions: Contradiction[];
  summary: {
    total_documents: number;
    total_contradictions: number;
    processing_status: string;
  };
}

export interface UploadedFile {
  filename: string;
  saved_as: string;
  file_path: string;
  file_size: number;
  status: string;
}

export interface UploadResponse {
  message: string;
  successful_uploads: number;
  failed_uploads: number;
  files: UploadedFile[];
  errors: Array<{
    filename: string;
    error: string;
  }>;
}

// API Service Class
class ApiService {
  async uploadDocuments(files: FileList): Promise<UploadResponse> {
    try {
      console.log(`📤 Uploading ${files.length} files...`);
      Array.from(files).forEach(file => {
        console.log(`📄 File: ${file.name} (${file.size} bytes, ${file.type})`);
      });

      const formData = new FormData();
      Array.from(files).forEach(file => {
        formData.append('files', file);
      });

      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout for uploads
      });
      
      console.log('✅ Upload successful:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Upload failed:', error);
      
      if (error.code === 'ECONNABORTED') {
        throw new Error('Upload timed out. Please try uploading fewer or smaller files.');
      }
      
      if (error.response) {
        console.error('📋 Upload error details:', {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data
        });
        
        const errorMessage = error.response.data?.detail || 
                           error.response.data?.message || 
                           `Upload failed (${error.response.status})`;
        throw new Error(errorMessage);
      }
      
      if (error.request) {
        throw new Error('Network error: Unable to connect to the server. Please check if the backend is running.');
      }
      
      throw new Error(`Upload failed: ${error.message}`);
    }
  }

  async analyzeDocuments(filePaths?: string[]): Promise<AnalysisResult> {
    try {
      console.log('🔍 Starting document analysis...');
      console.log('📁 File paths to analyze:', filePaths);
      
      const requestBody = filePaths ? { file_paths: filePaths } : {};
      console.log('📤 Request body:', requestBody);
      
      const response = await api.post('/analyze', requestBody, {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 30000, // 30 second timeout
      });
      
      console.log('✅ Analysis completed successfully');
      console.log('📊 Response data:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('❌ Analysis failed:', error);
      
      if (error.code === 'ECONNABORTED') {
        throw new Error('Analysis timed out. Please try again with fewer documents.');
      }
      
      if (error.response) {
        console.error('📋 Error details:', {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data
        });
        
        const errorMessage = error.response.data?.detail || 
                           error.response.data?.message || 
                           `Server error (${error.response.status})`;
        throw new Error(`Analysis failed: ${errorMessage}`);
      }
      
      if (error.request) {
        console.error('🌐 Network error - no response received');
        throw new Error('Network error: Unable to connect to the server. Please check if the backend is running.');
      }
      
      throw new Error(`Analysis failed: ${error.message}`);
    }
  }

  async getContradictionResults(): Promise<{
    documents: Document[];
    contradictions: Contradiction[];
    summary: {
      total_documents: number;
      total_contradictions: number;
    };
  }> {
    const response = await api.get('/check');
    return response.data;
  }

  async listDocuments(): Promise<{
    documents: Document[];
    total_count: number;
  }> {
    const response = await api.get('/documents');
    return response.data;
  }

  async getDocumentResults(docId: number): Promise<{
    document: Document;
    related_contradictions: Contradiction[];
    contradiction_count: number;
  }> {
    const response = await api.get(`/results/${docId}`);
    return response.data;
  }

  async deleteDocument(docId: number): Promise<{ message: string }> {
    const response = await api.delete(`/documents/${docId}`);
    return response.data;
  }

  async getStatistics(): Promise<{
    database_stats: {
      total_documents: number;
      total_contradictions: number;
      common_contradiction_types: Array<{
        clause_type: string;
        count: number;
      }>;
    };
    upload_directory_stats: {
      total_files: number;
      pdf_files: number;
      docx_files: number;
      txt_files: number;
    };
  }> {
    const response = await api.get('/statistics');
    return response.data;
  }

  async listUploadedFiles(): Promise<{
    files: Array<{
      filename: string;
      file_path: string;
      file_size: number;
      file_extension: string;
      last_modified: number;
      is_supported: boolean;
    }>;
    total_count: number;
  }> {
    const response = await api.get('/uploads');
    return response.data;
  }

  async clearAllData(): Promise<{ message: string }> {
    const response = await api.post('/clear-data');
    return response.data;
  }

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get('/health');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;