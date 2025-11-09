// frontend/src/components/Documents/ElectronicSignatureCapture.tsx
import React, { useRef, useState, useEffect } from 'react';
import SignatureCanvas from 'react-signature-canvas';
import { api } from '../../services/api';

interface ElectronicSignatureCaptureProps {
  policyId?: number;
  documentId?: number;
  consentText: string;
  onSuccess: () => void;
  onCancel: () => void;
}

export const ElectronicSignatureCapture: React.FC<ElectronicSignatureCaptureProps> = ({
  policyId,
  documentId,
  consentText,
  onSuccess,
  onCancel
}) => {
  const signaturePadRef = useRef<SignatureCanvas>(null);
  const [signatureMethod, setSignatureMethod] = useState<'drawn' | 'typed'>('drawn');
  const [typedName, setTypedName] = useState('');
  const [acknowledged, setAcknowledged] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ipAddress, setIpAddress] = useState<string>('');

  useEffect(() => {
    // Get user's IP address for audit trail
    fetch('https://api.ipify.org?format=json')
      .then(res => res.json())
      .then(data => setIpAddress(data.ip))
      .catch(err => console.error('Failed to get IP:', err));
  }, []);

  const clearSignature = () => {
	const pad = signaturePadRef.current;
	if (pad) {
		pad.clear();
	}
	setTypedName('');
  };


  const handleSubmit = async () => {
    if (!acknowledged) {
      setError('You must acknowledge the terms to continue');
      return;
    }

    let signatureData = '';

	  if (signatureMethod === 'drawn') {
	    const pad = signaturePadRef.current;
	    if (!pad || pad.isEmpty()) {
	  	  setError('Please provide a signature');
	  	  return;
	  }
	  signatureData = pad.toDataURL();
	  } else {
      if (!typedName.trim()) {
        setError('Please type your full name');
        return;
      }
      signatureData = typedName;
    }

    try {
      setSaving(true);
      setError(null);

      await api.client.post('/v1/documents/sign', {
        policy_document_id: policyId,
        custom_document_id: documentId,
        signature_data: signatureData,
        signature_method: signatureMethod,
        consent_text: consentText,
        acknowledged_terms: true
      });

      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save signature');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Electronic Signature Required</h2>
        <p className="text-gray-600">Please review and sign the document below</p>
      </div>

      {/* Consent Text */}
      <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 mb-6 max-h-64 overflow-y-auto">
        <div className="prose prose-sm max-w-none">
          <div dangerouslySetInnerHTML={{ __html: consentText }} />
        </div>
      </div>

      {/* Signature Method Toggle */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-3">
          Signature Method
        </label>
        <div className="flex space-x-4">
          <button
            onClick={() => setSignatureMethod('drawn')}
            className={`
              flex-1 px-4 py-3 rounded-lg font-semibold transition-colors
              ${signatureMethod === 'drawn'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}
            `}
          >
            ✍️ Draw Signature
          </button>
          <button
            onClick={() => setSignatureMethod('typed')}
            className={`
              flex-1 px-4 py-3 rounded-lg font-semibold transition-colors
              ${signatureMethod === 'typed'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}
            `}
          >
            ⌨️ Type Name
          </button>
        </div>
      </div>

      {/* Signature Input */}
      <div className="mb-6">
        {signatureMethod === 'drawn' ? (
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Draw Your Signature
            </label>
            <div className="border-2 border-gray-300 rounded-lg overflow-hidden bg-white">
              <SignatureCanvas
                ref={signaturePadRef}
                canvasProps={{
                  className: 'w-full h-48 cursor-crosshair'
                }}
                backgroundColor="white"
                penColor="black"
              />
            </div>
            <button
              onClick={clearSignature}
              className="mt-2 text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              Clear Signature
            </button>
          </div>
        ) : (
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Type Your Full Name
            </label>
            <input
              type="text"
              value={typedName}
              onChange={(e) => setTypedName(e.target.value)}
              placeholder="John Doe"
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-2xl font-signature focus:outline-none focus:ring-2 focus:ring-blue-500"
              style={{ fontFamily: 'Brush Script MT, cursive' }}
            />
          </div>
        )}
      </div>

      {/* Acknowledgment Checkbox */}
      <div className="mb-6">
        <label className="flex items-start cursor-pointer">
          <input
            type="checkbox"
            checked={acknowledged}
            onChange={(e) => setAcknowledged(e.target.checked)}
            className="mt-1 w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="ml-3 text-sm text-gray-700">
            <strong>I acknowledge</strong> that I have read and understood the document above, 
            and that my electronic signature has the same legal effect as a handwritten signature.
          </span>
        </label>
      </div>

      {/* Legal Notice */}
      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-800">
              <strong>Legal Notice:</strong> Your signature, IP address ({ipAddress}), 
              and timestamp will be securely recorded for legal purposes. This signature 
              cannot be repudiated.
            </p>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3">
        <button
          onClick={onCancel}
          disabled={saving}
          className="px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          disabled={!acknowledged || saving}
          className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Saving...
            </span>
          ) : (
            '✓ Sign Document'
          )}
        </button>
      </div>
    </div>
  );
};
