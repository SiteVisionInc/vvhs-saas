// frontend/src/components/Documents/PolicyDocumentLibrary.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { ElectronicSignatureCapture } from './ElectronicSignatureCapture';

interface PolicyDocument {
  id: number;
  title: string;
  description: string;
  document_type: string;
  version: string;
  requires_signature: boolean;
  effective_date: string;
  expiration_date: string | null;
  is_active: boolean;
  is_expired: boolean;
  file_url: string;
}

interface SignatureStatus {
  policy_id: number;
  signed: boolean;
  signed_at: string | null;
}

export const PolicyDocumentLibrary: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyDocument[]>([]);
  const [signatureStatuses, setSignatureStatuses] = useState<Record<number, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [signingPolicyId, setSigningPolicyId] = useState<number | null>(null);
  const [selectedPolicy, setSelectedPolicy] = useState<PolicyDocument | null>(null);

  useEffect(() => {
    loadPolicies();
  }, []);

  const loadPolicies = async () => {
    try {
      setLoading(true);
      const response = await api.client.get('/v1/documents/policies');
      setPolicies(response.data);

      // Load signature statuses
      // In production, this would be a separate API call
      const statuses: Record<number, boolean> = {};
      response.data.forEach((policy: PolicyDocument) => {
        // Mock: set some as signed
        statuses[policy.id] = Math.random() > 0.5;
      });
      setSignatureStatuses(statuses);
    } catch (error) {
      console.error('Failed to load policies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewPolicy = (policy: PolicyDocument) => {
    setSelectedPolicy(policy);
  };

  const handleSignPolicy = (policy: PolicyDocument) => {
    setSigningPolicyId(policy.id);
    setSelectedPolicy(policy);
  };

  const handleSignatureSuccess = () => {
    setSigningPolicyId(null);
    setSelectedPolicy(null);
    loadPolicies();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (signingPolicyId && selectedPolicy) {
    return (
      <ElectronicSignatureCapture
        policyId={signingPolicyId}
        consentText={selectedPolicy.description || 'Please review and sign this policy document.'}
        onSuccess={handleSignatureSuccess}
        onCancel={() => {
          setSigningPolicyId(null);
          setSelectedPolicy(null);
        }}
      />
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Policy Documents</h1>
        <p className="text-gray-600">Review and acknowledge organizational policies</p>
      </div>

      {/* Documents requiring signature */}
      {policies.filter(p => p.requires_signature && !signatureStatuses[p.id]).length > 0 && (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-800">
                <strong>Action Required:</strong> You have{' '}
                {policies.filter(p => p.requires_signature && !signatureStatuses[p.id]).length}{' '}
                policy document(s) that require your signature.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Policy Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {policies.map((policy) => {
          const isSigned = signatureStatuses[policy.id];
          const requiresSignature = policy.requires_signature;

          return (
            <div
              key={policy.id}
              className={`
                bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow
                ${!isSigned && requiresSignature ? 'border-2 border-yellow-400' : ''}
              `}
            >
              {/* Header */}
              <div className={`
                px-6 py-4
                ${!isSigned && requiresSignature
                  ? 'bg-yellow-50'
                  : 'bg-gradient-to-r from-blue-500 to-blue-600'}
              `}>
                <h3 className={`
                  text-lg font-bold
                  ${!isSigned && requiresSignature ? 'text-gray-900' : 'text-white'}
                `}>
                  {policy.title}
                </h3>
                <p className={`
                  text-sm
                  ${!isSigned && requiresSignature ? 'text-gray-600' : 'text-blue-100'}
                `}>
                  Version {policy.version}
                </p>
              </div>

              {/* Body */}
              <div className="px-6 py-4">
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {policy.description}
                </p>

                {/* Status Badges */}
                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="px-3 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                    {policy.document_type}
                  </span>
                  {isSigned ? (
                    <span className="px-3 py-1 text-xs rounded-full bg-green-100 text-green-800">
                      ✓ Signed
                    </span>
                  ) : requiresSignature ? (
                    <span className="px-3 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                      ⚠ Signature Required
                    </span>
                  ) : (
                    <span className="px-3 py-1 text-xs rounded-full bg-gray-100 text-gray-800">
                      No signature required
                    </span>
                  )}
                </div>

                {/* Dates */}
                <div className="text-xs text-gray-500 space-y-1 mb-4">
                  <p>Effective: {new Date(policy.effective_date).toLocaleDateString()}</p>
                  {policy.expiration_date && (
                    <p>Expires: {new Date(policy.expiration_date).toLocaleDateString()}</p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleViewPolicy(policy)}
                    className="flex-1 px-4 py-2 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50"
                  >
                    View
                  </button>
                  {requiresSignature && !isSigned && (
                    <button
                      onClick={() => handleSignPolicy(policy)}
                      className="flex-1 px-4 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700"
                    >
                      Sign Now
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {policies.length === 0 && (
        <div className="text-center py-12">
          <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Policy Documents</h3>
          <p className="text-gray-500">There are no policy documents available at this time.</p>
        </div>
      )}
    </div>
  );
};
