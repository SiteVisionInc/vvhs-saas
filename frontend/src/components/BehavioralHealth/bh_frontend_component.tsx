// ==================== BEHAVIORAL HEALTH FRONTEND COMPONENTS ====================
// Complete UI implementation for Module 2.2 workflows

// ==================== A. INTAKE → SCREENING → CONSENT ====================

// 1. PatientIntakeForm.tsx
import { api } from '../../services/api';
import React, { useState, useEffect } from 'react';


interface PatientIntakeFormProps {
  onSuccess: (patientId: number) => void;
  onCancel: () => void;
}

interface SearchParams {
  facility_type: string;
  bed_type: string;
  region_id: number | null;
  min_available: number;
  patient_age: number | null;
  patient_gender: string;
  capabilities: string[];
}


export const PatientIntakeForm: React.FC<PatientIntakeFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    mrn: '',
    first_name: '',
    last_name: '',
    dob: '',
    gender: '',
    phones: [{ type: 'mobile', number: '', preferred: true }],
    addresses: [{ type: 'home', line1: '', city: '', state: 'VA', zip: '' }],
    guardians: [],
    emergency_contacts: [{ name: '', phone: '', relationship: '' }],
    notes: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const response = await api.client.post('/v1/bh/patients', formData);
      onSuccess(response.data.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create patient');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold text-gray-900 mb-6">Patient Intake Form</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Demographics Section */}
        <div className="border-b border-gray-200 pb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Demographics</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Medical Record Number (MRN)
              </label>
              <input
                type="text"
                value={formData.mrn}
                onChange={(e) => setFormData({ ...formData, mrn: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="Optional"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                First Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.first_name}
                onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Last Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.last_name}
                onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date of Birth
              </label>
              <input
                type="date"
                value={formData.dob}
                onChange={(e) => setFormData({ ...formData, dob: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Gender
              </label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select...</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="X">Non-binary</option>
                <option value="U">Unknown</option>
              </select>
            </div>
          </div>
        </div>

        {/* Contact Information */}
        <div className="border-b border-gray-200 pb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Contact Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                value={formData.phones[0].number}
                onChange={(e) => {
                  const newPhones = [...formData.phones];
                  newPhones[0].number = e.target.value;
                  setFormData({ ...formData, phones: newPhones });
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="(555) 123-4567"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Address Line 1
              </label>
              <input
                type="text"
                value={formData.addresses[0].line1}
                onChange={(e) => {
                  const newAddresses = [...formData.addresses];
                  newAddresses[0].line1 = e.target.value;
                  setFormData({ ...formData, addresses: newAddresses });
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                City
              </label>
              <input
                type="text"
                value={formData.addresses[0].city}
                onChange={(e) => {
                  const newAddresses = [...formData.addresses];
                  newAddresses[0].city = e.target.value;
                  setFormData({ ...formData, addresses: newAddresses });
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ZIP Code
              </label>
              <input
                type="text"
                value={formData.addresses[0].zip}
                onChange={(e) => {
                  const newAddresses = [...formData.addresses];
                  newAddresses[0].zip = e.target.value;
                  setFormData({ ...formData, addresses: newAddresses });
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Emergency Contact */}
        <div className="border-b border-gray-200 pb-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Emergency Contact</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contact Name
              </label>
              <input
                type="text"
                value={formData.emergency_contacts[0].name}
                onChange={(e) => {
                  const newContacts = [...formData.emergency_contacts];
                  newContacts[0].name = e.target.value;
                  setFormData({ ...formData, emergency_contacts: newContacts });
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contact Phone
              </label>
              <input
                type="tel"
                value={formData.emergency_contacts[0].phone}
                onChange={(e) => {
                  const newContacts = [...formData.emergency_contacts];
                  newContacts[0].phone = e.target.value;
                  setFormData({ ...formData, emergency_contacts: newContacts });
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Relationship
              </label>
              <input
                type="text"
                value={formData.emergency_contacts[0].relationship}
                onChange={(e) => {
                  const newContacts = [...formData.emergency_contacts];
                  newContacts[0].relationship = e.target.value;
                  setFormData({ ...formData, emergency_contacts: newContacts });
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Clinical Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Clinical Notes
          </label>
          <textarea
            rows={4}
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Initial assessment, presenting concerns, etc."
          />
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            disabled={submitting}
            className="px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? 'Creating...' : 'Create Patient'}
          </button>
        </div>
      </form>
    </div>
  );
};


// 2. ScreeningInstruments.tsx
interface ScreeningInstrumentsProps {
  patientId: number;
  onComplete: () => void;
}

export const ScreeningInstruments: React.FC<ScreeningInstrumentsProps> = ({ patientId, onComplete }) => {
  const [selectedInstrument, setSelectedInstrument] = useState<'C-SSRS' | 'ASAM' | 'PHQ-9' | null>(null);
  const [responses, setResponses] = useState<any>({});
  const [submitting, setSubmitting] = useState(false);

	const instruments = {
	'C-SSRS': {
		name: 'Columbia-Suicide Severity Rating Scale',
		questions: [
		{ id: 'wish_dead', text: 'Have you wished you were dead or wished you could go to sleep and not wake up?' },
		{ id: 'suicidal_thoughts', text: 'Have you actually had any thoughts of killing yourself?' },
		{ id: 'thoughts_method', text: 'Have you been thinking about how you might do this?' },
		{ id: 'intent', text: 'Have you had these thoughts and had some intention of acting on them?' },
		{ id: 'plan', text: 'Have you started to work out or worked out the details of how to kill yourself?' }
		]
	},
	'PHQ-9': {
		name: 'Patient Health Questionnaire-9',
		questions: [
		{ id: 'q1', text: 'Little interest or pleasure in doing things' },
		{ id: 'q2', text: 'Feeling down, depressed, or hopeless' },
		// ...
		],
		options: [
		{ value: 0, label: 'Not at all' },
		{ value: 1, label: 'Several days' },
		{ value: 2, label: 'More than half the days' },
		{ value: 3, label: 'Nearly every day' }
		]
	},
	'ASAM': {
		name: 'American Society of Addiction Medicine (ASAM) Screening',
		questions: [
		{ id: 'use_frequency', text: 'How often do you use substances?' },
		{ id: 'craving', text: 'Do you feel strong cravings to use substances?' }
		]
	}
	};


  const handleSubmit = async () => {
    if (!selectedInstrument) return;

    setSubmitting(true);
    try {
      // Calculate score
      let score = 0;
      if (selectedInstrument === 'PHQ-9') {
        score = Object.values(responses).reduce((sum: number, val: any) => sum + parseInt(val || 0), 0);
      } else if (selectedInstrument === 'C-SSRS') {
        // C-SSRS scoring: count positive responses
        score = Object.values(responses).filter(v => v === 'yes').length;
      }

      await api.client.post('/v1/bh/patients/screenings', {
        patient_id: patientId,
        instrument_type: selectedInstrument,
        score,
        details_json: responses,
        clinician_id: 1, // TODO: Get from current user
        screening_date: new Date().toISOString()
      });

      onComplete();
    } catch (error) {
      alert('Failed to save screening');
    } finally {
      setSubmitting(false);
    }
  };

  if (!selectedInstrument) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">Clinical Screening</h2>
        <p className="text-gray-600 mb-8">Select a screening instrument to administer:</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Object.entries(instruments).map(([key, instrument]) => (
            <button
              key={key}
              onClick={() => setSelectedInstrument(key as any)}
              className="border-2 border-gray-300 rounded-xl p-6 hover:border-blue-500 hover:bg-blue-50 transition-all text-left"
            >
              <h3 className="text-xl font-bold text-gray-900 mb-2">{key}</h3>
              <p className="text-sm text-gray-600">{instrument.name}</p>
            </button>
          ))}
        </div>
      </div>
    );
  }

  const instrument = instruments[selectedInstrument];

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">{selectedInstrument}</h2>
          <p className="text-gray-600">{instrument.name}</p>
        </div>
        <button
          onClick={() => setSelectedInstrument(null)}
          className="text-gray-500 hover:text-gray-700"
        >
          ← Back
        </button>
      </div>

      <div className="space-y-6">
        {instrument.questions.map((question: { id: string; text: string }, index: number) => (
          <div key={question.id} className="border-b border-gray-200 pb-6">
            <p className="text-lg font-medium text-gray-900 mb-4">
              {index + 1}. {question.text}
            </p>

            {selectedInstrument === 'PHQ-9' && (
              <div className="flex space-x-4">
                {instruments['PHQ-9'].options.map(option => (
                  <label key={option.value} className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name={question.id}
                      value={option.value}
                      checked={responses[question.id] === String(option.value)}
                      onChange={(e) => setResponses({ ...responses, [question.id]: e.target.value })}
                      className="w-5 h-5 text-blue-600"
                    />
                    <span className="ml-2 text-sm text-gray-700">{option.label}</span>
                  </label>
                ))}
              </div>
            )}

            {selectedInstrument === 'C-SSRS' && (
              <div className="flex space-x-6">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name={question.id}
                    value="yes"
                    checked={responses[question.id] === 'yes'}
                    onChange={(e) => setResponses({ ...responses, [question.id]: e.target.value })}
                    className="w-5 h-5 text-blue-600"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">Yes</span>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    name={question.id}
                    value="no"
                    checked={responses[question.id] === 'no'}
                    onChange={(e) => setResponses({ ...responses, [question.id]: e.target.value })}
                    className="w-5 h-5 text-blue-600"
                  />
                  <span className="ml-2 text-sm font-medium text-gray-700">No</span>
                </label>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-end space-x-3 mt-8">
        <button
          onClick={() => setSelectedInstrument(null)}
          disabled={submitting}
          className="px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          disabled={submitting || Object.keys(responses).length !== instrument.questions.length}
          className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          {submitting ? 'Saving...' : 'Complete Screening'}
        </button>
      </div>
    </div>
  );
};


// ==================== B. BED SEARCH → PLACEMENT ====================

// 3. BedSearchInterface.tsx
interface BedSearchInterfaceProps {
  onSelectFacility: (facilityId: number, bedType: string) => void;
}

export const BedSearchInterface: React.FC<BedSearchInterfaceProps> = ({ onSelectFacility }) => {
  const [searchParams, setSearchParams] = useState<SearchParams>({
	facility_type: '',
	bed_type: '',
	region_id: null,
	min_available: 1,
	patient_age: null,
	patient_gender: '',
	capabilities: []
  });
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'map'>('list');

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await api.client.post('/v1/bh/facilities/search', searchParams);
      setResults(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Filters */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Search Available Beds</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Facility Type
            </label>
            <select
              value={searchParams.facility_type}
              onChange={(e) => setSearchParams({ ...searchParams, facility_type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Types</option>
              <option value="hospital">Hospital</option>
              <option value="detox">Detox</option>
              <option value="residential">Residential</option>
              <option value="outpatient">Outpatient</option>
              <option value="crisis">Crisis</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bed Type
            </label>
            <select
              value={searchParams.bed_type}
              onChange={(e) => setSearchParams({ ...searchParams, bed_type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Types</option>
              <option value="general">General</option>
              <option value="adolescent">Adolescent</option>
              <option value="geriatric">Geriatric</option>
              <option value="SUD">SUD</option>
              <option value="detox">Detox</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Patient Age (optional)
            </label>
            <input
              type="number"
              value={searchParams.patient_age || ''}
              onChange={(e) => setSearchParams({ ...searchParams, patient_age: e.target.value ? parseInt(e.target.value) : null })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
              placeholder="Age"
            />
          </div>
        </div>

        <div className="flex justify-between items-center">
          <div className="flex space-x-2">
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 rounded-lg font-medium ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
            >
              📋 List View
            </button>
            <button
              onClick={() => setViewMode('map')}
              className={`px-4 py-2 rounded-lg font-medium ${viewMode === 'map' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700'}`}
            >
              🗺️ Map View
            </button>
          </div>

          <button
            onClick={handleSearch}
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? 'Searching...' : '🔍 Search Beds'}
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {results.map((result) => (
          <div key={`${result.facility_id}-${result.bed_type}`} className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4">
              <h3 className="text-xl font-bold text-white">{result.facility_name}</h3>
              <p className="text-green-100 text-sm">{result.facility_type}</p>
            </div>

            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-sm text-gray-600">Bed Type</p>
                  <p className="text-lg font-semibold text-gray-900">{result.bed_type}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">Available Beds</p>
                  <p className="text-3xl font-bold text-green-600">{result.available_beds}</p>
                  <p className="text-xs text-gray-500">of {result.total_beds}</p>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                {result.contact_phone && (
                  <p className="text-sm text-gray-600">
                    📞 {result.contact_phone}
                  </p>
                )}
                {result.distance_miles && (
                  <p className="text-sm text-gray-600">
                    📍 {result.distance_miles} miles away
                  </p>
                )}
                <p className="text-sm text-gray-500">
                  Last updated: {new Date(result.last_updated).toLocaleString()}
                </p>
              </div>

              {result.is_stale && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mb-4">
                  <p className="text-sm text-yellow-800"> Data may be stale ({'>'}24 hours old)</p>
                </div>
              )}

              <button
                onClick={() => onSelectFacility(result.facility_id, result.bed_type)}
                className="w-full px-4 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700"
              >
                Create Referral →
              </button>
            </div>
          </div>
        ))}
      </div>

      {results.length === 0 && !loading && (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <p className="text-gray-500 text-lg">
            No beds available matching your criteria. Try adjusting your filters.
          </p>
        </div>
      )}
    </div>
  );
};


// 4. ReferralCreationWizard.tsx - OMITTED FOR BREVITY (similar pattern to PublicRegistrationWizard)

// 5. FacilityReferralQueue.tsx
export const FacilityReferralQueue: React.FC = () => {
  const [referrals, setReferrals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('submitted');

  useEffect(() => {
    loadReferrals();
  }, [filter]);

  const loadReferrals = async () => {
    setLoading(true);
    try {
      const response = await api.client.get(`/v1/bh/referrals?status=${filter}`);
      setReferrals(response.data);
    } catch (error) {
      console.error('Failed to load referrals:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (referralId: number) => {
    const admissionDate = window.prompt('Enter admission date (YYYY-MM-DD):');
    if (!admissionDate) return;

    try {
      await api.client.post(`/v1/bh/referrals/${referralId}/accept`, {
        bed_type: 'general', // TODO: Get from referral
        admission_date: admissionDate,
        transport_details: {},
        notes: ''
      });

      alert('Referral accepted!');
      loadReferrals();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to accept referral');
    }
  };

  const handleDecline = async (referralId: number) => {
    const reason = window.prompt('Reason for declining:');
    if (!reason) return;

    try {
      await api.client.post(`/v1/bh/referrals/${referralId}/decline`, {
        reason_code: reason,
        reason_notes: ''
      });

      alert('Referral declined');
      loadReferrals();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to decline referral');
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold text-gray-900">Referral Queue</h2>
        
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg"
        >
          <option value="submitted">Submitted</option>
          <option value="accepted">Accepted</option>
          <option value="declined">Declined</option>
          <option value="all">All</option>
        </select>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {referrals.map((referral) => (
          <div key={referral.id} className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900">
                  Referral #{referral.id}
                </h3>
                <p className="text-gray-600">
                  Patient ID: {referral.patient_id}
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                referral.priority === 'emergency' ? 'bg-red-100 text-red-800' :
                referral.priority === 'urgent' ? 'bg-orange-100 text-orange-800' :
                'bg-blue-100 text-blue-800'
              }`}>
                {referral.priority}
              </span>
            </div>

            <div className="space-y-2 mb-4">
              <p className="text-sm text-gray-600">
                <strong>Referral Date:</strong> {new Date(referral.referral_date).toLocaleString()}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Status:</strong> {referral.status}
              </p>
              {referral.notes && (
                <p className="text-sm text-gray-600">
                  <strong>Notes:</strong> {referral.notes}
                </p>
              )}
            </div>

            {referral.status === 'submitted' && (
              <div className="flex space-x-3">
                <button
                  onClick={() => handleAccept(referral.id)}
                  className="flex-1 px-4 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700"
                >
                  ✓ Accept
                </button>
                <button
                  onClick={() => handleDecline(referral.id)}
                  className="flex-1 px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700"
                >
                  ✗ Decline
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// ==================== C. DISCHARGE → FOLLOW-UP ====================
// ==================== D. DAILY BED REPORTING ====================
// Additional components TBD