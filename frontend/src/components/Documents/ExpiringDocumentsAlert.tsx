// frontend/src/components/Documents/ExpiringDocumentsAlert.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';

interface ExpiringDocument {
  volunteer_id: number;
  volunteer_name: string;
  document_type: string;
  document_title: string;
  expiration_date: string;
  days_until_expiration: number;
}

export const ExpiringDocumentsAlert: React.FC = () => {
  const [expiringDocs, setExpiringDocs] = useState<ExpiringDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadExpiringDocuments();
  }, []);

  const loadExpiringDocuments = async () => {
    try {
      setLoading(true);
      const response = await api.client.get('/v1/documents/expiring?days=30');
      setExpiringDocs(response.data);
    } catch (error) {
      console.error('Failed to load expiring documents:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="animate-pulse space-y-2">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (expiringDocs.length === 0) {
    return null; // Don't show widget if no expiring documents
  }

  const criticalDocs = expiringDocs.filter(d => d.days_until_expiration <= 7);
  const warningDocs = expiringDocs.filter(d => d.days_until_expiration > 7 && d.days_until_expiration <= 30);

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div
        onClick={() => setExpanded(!expanded)}
        className={`
          px-6 py-4 cursor-pointer transition-colors
          ${criticalDocs.length > 0
            ? 'bg-red-500 hover:bg-red-600'
            : 'bg-yellow-500 hover:bg-yellow-600'}
        `}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="text-white font-bold">
                {expiringDocs.length} Document{expiringDocs.length !== 1 ? 's' : ''} Expiring Soon
              </h3>
              <p className="text-white text-sm opacity-90">
                {criticalDocs.length > 0 && (
                  <span>{criticalDocs.length} critical (within 7 days)</span>
                )}
                {criticalDocs.length > 0 && warningDocs.length > 0 && <span>, </span>}
                {warningDocs.length > 0 && (
                  <span>{warningDocs.length} within 30 days</span>
                )}
              </p>
            </div>
          </div>
          <svg
            className={`w-5 h-5 text-white transition-transform ${expanded ? 'transform rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Expanded List */}
      {expanded && (
        <div className="divide-y divide-gray-200">
          {expiringDocs.map((doc, index) => {
            const isCritical = doc.days_until_expiration <= 7;
            const expirationDate = new Date(doc.expiration_date);

            return (
              <div key={index} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-sm font-semibold text-gray-900">
                        {doc.volunteer_name}
                      </span>
                      <span className={`
                        px-2 py-1 text-xs rounded-full font-medium
                        ${isCritical
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'}
                      `}>
                        {doc.days_until_expiration} day{doc.days_until_expiration !== 1 ? 's' : ''} left
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">
                      {doc.document_title}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      Expires: {expirationDate.toLocaleDateString()}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      // Navigate to volunteer profile or send reminder
                      console.log('Send reminder to:', doc.volunteer_id);
                    }}
                    className="ml-4 px-3 py-1 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700"
                  >
                    Send Reminder
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Footer Actions */}
      {expanded && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <button
            onClick={() => {
              // Navigate to full expiring documents report
              window.location.href = '/documents/expiring';
            }}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            View Full Report →
          </button>
        </div>
      )}
    </div>
  );
};
