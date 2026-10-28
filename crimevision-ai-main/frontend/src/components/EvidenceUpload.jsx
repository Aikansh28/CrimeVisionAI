import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadEvidence } from '../services/api';

function EvidenceUpload({ caseId, onUploadComplete }) {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'success' | 'error' | null
  const [statusMessage, setStatusMessage] = useState('');

  // Handle file drop
  const onDrop = useCallback(
    async (acceptedFiles) => {
      if (acceptedFiles.length === 0) return;

      setUploading(true);
      setUploadStatus(null);

      try {
        // Upload each file one at a time
        for (const file of acceptedFiles) {
          const formData = new FormData();
          formData.append('file', file);
          await uploadEvidence(caseId, formData);
        }

        setUploadStatus('success');
        setStatusMessage(`${acceptedFiles.length} file(s) uploaded successfully`);

        // Notify parent to refresh evidence list
        if (onUploadComplete) {
          onUploadComplete();
        }

        // Clear success message after 3 seconds
        setTimeout(() => {
          setUploadStatus(null);
          setStatusMessage('');
        }, 3000);
      } catch (err) {
        setUploadStatus('error');
        setStatusMessage(err.response?.data?.detail || 'Upload failed. Please try again.');
      } finally {
        setUploading(false);
      }
    },
    [caseId, onUploadComplete]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'audio/mpeg': ['.mp3'],
      'audio/wav': ['.wav'],
    },
    disabled: uploading,
  });

  return (
    <div className="mb-6">
      {/* Drop zone area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-500 bg-opacity-10'
            : uploading
            ? 'border-gray-600 bg-gray-800 cursor-not-allowed'
            : 'border-gray-600 hover:border-blue-500 hover:bg-gray-800'
        }`}
      >
        <input {...getInputProps()} />

        {uploading ? (
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-3 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-300">Uploading evidence...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <Upload className="w-10 h-10 text-gray-400" />
            {isDragActive ? (
              <p className="text-blue-400 font-medium">Drop files here...</p>
            ) : (
              <>
                <p className="text-gray-300">
                  Drag & drop evidence files here, or{' '}
                  <span className="text-blue-400 underline">click to browse</span>
                </p>
                <p className="text-xs text-gray-500">
                  Supported: JPEG, PNG (images) • MP3, WAV (audio)
                </p>
              </>
            )}
          </div>
        )}
      </div>

      {/* Upload status message */}
      {uploadStatus && (
        <div
          className={`mt-3 flex items-center gap-2 px-4 py-2 rounded-lg text-sm ${
            uploadStatus === 'success'
              ? 'bg-green-500 bg-opacity-20 text-green-400'
              : 'bg-red-500 bg-opacity-20 text-red-400'
          }`}
        >
          {uploadStatus === 'success' ? (
            <CheckCircle className="w-4 h-4" />
          ) : (
            <AlertCircle className="w-4 h-4" />
          )}
          {statusMessage}
        </div>
      )}
    </div>
  );
}

export default EvidenceUpload;
