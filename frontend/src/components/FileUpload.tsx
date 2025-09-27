import React, { useState, useRef } from 'react';
import { UploadResponse, apiService } from '../services/api';

interface FileUploadProps {
  onUploadComplete: (response: UploadResponse) => void;
  onUploadStart: () => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete, onUploadStart }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setSelectedFiles(files);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setSelectedFiles(files);
    }
  };

  const handleUpload = async () => {
    if (!selectedFiles || selectedFiles.length === 0) {
      alert('Please select files to upload');
      return;
    }

    setIsUploading(true);
    onUploadStart();

    try {
      const response = await apiService.uploadDocuments(selectedFiles);
      onUploadComplete(response);
      setSelectedFiles(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="card">
      <h2>Upload Documents</h2>
      <p>Upload PDF, DOCX, or TXT files to analyze for contradictions.</p>
      
      <div
        className={`upload-area ${isDragging ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileDialog}
      >
        <div>
          <p>📁 Drag and drop files here or click to browse</p>
          <p>Supported formats: PDF, DOCX, DOC, TXT</p>
        </div>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.docx,.doc,.txt"
        onChange={handleFileSelect}
        className="file-input"
      />

      {selectedFiles && selectedFiles.length > 0 && (
        <div className="file-list">
          <h3>Selected Files ({selectedFiles.length})</h3>
          {Array.from(selectedFiles).map((file, index) => (
            <div key={index} className="file-item">
              <div>
                <strong>{file.name}</strong>
                <br />
                <small>{formatFileSize(file.size)} • {file.type}</small>
              </div>
              <div className="status-success">Ready</div>
            </div>
          ))}
          
          <button
            onClick={handleUpload}
            disabled={isUploading}
            className="btn btn-success"
            style={{ marginTop: '10px' }}
          >
            {isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} File(s)`}
          </button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;