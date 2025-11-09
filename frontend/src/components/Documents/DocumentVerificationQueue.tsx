// frontend/src/components/Documents/DocumentVerificationQueue.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';

interface PendingDocument {
  id: number;
  volunteer_id: number;
  volunteer_name: string;
  document_type: string;
  title: string;
  file_url: string;
  file_type: string;
  file_size_bytes: number;
  uploaded_at: string;
  verification_status: string;
}

export const DocumentVerificationQueue: React.FC = () => {
  const [documents, setDocuments] = useState<PendingDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState<PendingDocument | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  useEffect(() => {
    loadPendingDocuments();
  }, []);

  const loadPendingDocuments = async () => {
    try {
      setLoading(true);
      // This would need to be implemented as an API endpoint
      // For now, mock data
      const mockDocs: PendingDocument[] = [
        {
          id: 1,
          volunteer_id: 1,
          volunteer_name: 'Alice Anderson',
          document_type: 'photo_id',
          title: 'drivers_license.jpg',
          file_url: 'https://example.com/doc1.jpg',
          file_type: 'image/jpeg',
          file_size_bytes: 1024000,
          uploaded_at: new Date().toISOString(),
          verification_status: 'pending'
        }
      ];
      setDocuments(mockDocs);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async (documentId: number, status: 'approved' | 'rejected') => {
    try {
      setVerifying(true);

      await api.client.patch(`/v1/documents/documents/${documentId}/verify`, {
        verification_status: status,
        rejection_reason: status === 'rejected' ? rejectReason : null
      });

      setDocuments(documents.filter(d => d.id !== documentId));
      setSelectedDocument(null);
      setRejectReason('');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to verify document');
    } finally {
      setVerifying(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Verification Queue</h1>
        <p className="text-gray-600">
          Review and verify volunteer documents ({documents.length} pending)
        </p>
      </div>

      {/* Document List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-xl font-bold text-white mb-1">
                    {doc.volunteer_name}
                  </h3>
                  <p className="text-purple-100 text-sm">
                    {doc.document_type.replace('_', ' ')}
                  </p>
                </div>
                <span className="px-3 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                  Pending Review
                </span>
              </div>
            </div>

            {/* Body */}
            <div className="px-6 py-4">
              {/* Document Info */}
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-1">
                  <strong>File:</strong> {doc.title}
                </p>
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Size:</strong> {(doc.file_size_bytes / 1024 / 1024).toFixed(2)} MB
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Uploaded:</strong> {new Date(doc.uploaded_at).toLocaleString()}
                </p>
              </div>

              {/* Preview */}
              {doc.file_type.startsWith('image/') && (
                <div className="mb-4">
                  <img
                    src={doc.file_url}
                    alt={doc.title}
                    className="w-full h-48 object-cover rounded-lg border-2 border-gray-200"
                  />
                </div>
              )}

              {/* Quick Actions */}
              <div className="flex space-x-3">
                <button
                  onClick={() => setSelectedDocument(doc)}
                  className="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50"
                >
                  📄 View Full
                </button>
                <button
                  onClick={() => handleVerify(doc.id, 'approved')}
                  disabled={verifying}
                  className="flex-1 px-4 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  ✓ Approve
                </button>
                <button
                  onClick={() => {
                    setSelectedDocument(doc);
                    // Show reject modal
                  }}
                  disabled={verifying}
                  className="flex-1 px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 disabled:opacity-50"
                >
                  ✗ Reject
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {documents.length === 0 && (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <svg className="mx-auto h-16 w-16 text-green-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 className="text-xl font-bold text-gray-900 mb-2">All Caught Up!</h3>
          <p className="text-gray-600">There are no documents pending verification.</p>
        </div>
      )}

      {/* Reject Modal */}
      {selectedDocument && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Reject Document</h3>
            <p className="text-gray-600 mb-4">
              Please provide a reason for rejecting this document. This will be sent to the volunteer.
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="Reason for rejection (e.g., document is blurry, expired, incomplete)"
            />
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => {
                  setSelectedDocument(null);
                  setRejectReason('');
                }}
                className="px-6 py-2 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleVerify(selectedDocument.id, 'rejected')}
                disabled={!rejectReason.trim() || verifying}
                className="px-6 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                Reject Document
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
