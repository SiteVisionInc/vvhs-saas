import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

interface RegistrationData {
  tenant_id: number;
  first_name: string;
  middle_name?: string;
  last_name: string;
  email: string;
  phone_primary?: string;
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state: string;
  zip_code?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relationship?: string;
  skills?: string;
  languages?: string;
  availability?: string;
  occupation?: string;
  password: string;
  password_confirm: string;
}

export const PublicRegistrationWizard: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<RegistrationData>({
    tenant_id: 1,
    first_name: '',
    last_name: '',
    email: '',
    state: 'VA',
    password: '',
    password_confirm: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);

  const totalSteps = 5;

  const updateField = (field: keyof RegistrationData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (step === 1) {
      if (!formData.first_name) newErrors.first_name = 'First name is required';
      if (!formData.last_name) newErrors.last_name = 'Last name is required';
      if (!formData.email) newErrors.email = 'Email is required';
      else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Email is invalid';
    }

    if (step === 4) {
      if (!formData.password) newErrors.password = 'Password is required';
      else if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
      if (formData.password !== formData.password_confirm) {
        newErrors.password_confirm = 'Passwords do not match';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, totalSteps));
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setSubmitting(true);
    try {
      const { password_confirm, ...submitData } = formData;
      
      const response = await axios.post('/api/v1/volunteers/register', submitData);
      
      console.log('Registration successful:', response.data);
      navigate('/registration-success', { state: { email: formData.email } });
    } catch (error: any) {
      console.error('Registration error:', error);
      const message = error.response?.data?.detail || 'Registration failed. Please try again.';
      setErrors({ submit: message });
    } finally {
      setSubmitting(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <Step1BasicInfo formData={formData} updateField={updateField} errors={errors} />;
      case 2:
        return <Step2EmergencyContact formData={formData} updateField={updateField} errors={errors} />;
      case 3:
        return <Step3Skills formData={formData} updateField={updateField} errors={errors} />;
      case 4:
        return <Step4Password formData={formData} updateField={updateField} errors={errors} />;
      case 5:
        return <Step5Review formData={formData} />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Become a Volunteer
          </h1>
          <p className="text-lg text-gray-600">
            Join the Virginia Volunteer Health System
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Step {currentStep} of {totalSteps}
            </span>
            <span className="text-sm text-gray-500">
              {Math.round((currentStep / totalSteps) * 100)}% Complete
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Form Card */}
        <div className="bg-white rounded-xl shadow-2xl p-8">
          {renderStep()}

          {errors.submit && (
            <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 rounded">
              <p className="text-sm text-red-800">{errors.submit}</p>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="mt-8 flex justify-between">
            <button
              onClick={prevStep}
              disabled={currentStep === 1}
              className="px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              ← Previous
            </button>

            {currentStep < totalSteps ? (
              <button
                onClick={nextStep}
                className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
              >
                Next →
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={submitting}
                className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {submitting ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Submitting...
                  </span>
                ) : (
                  '✓ Submit Application'
                )}
              </button>
            )}
          </div>
        </div>

        {/* Help Text */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>Already have an account? <a href="/login" className="text-blue-600 hover:underline">Sign in here</a></p>
        </div>
      </div>
    </div>
  );
};

// Step Components
const Step1BasicInfo: React.FC<any> = ({ formData, updateField, errors }) => (
  <div className="space-y-6">
    <div>
      <h3 className="text-2xl font-bold text-gray-900 mb-2">Basic Information</h3>
      <p className="text-gray-600">Let's start with your contact details</p>
    </div>
    
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          First Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={formData.first_name}
          onChange={(e) => updateField('first_name', e.target.value)}
          className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.first_name ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="John"
        />
        {errors.first_name && <p className="text-sm text-red-600 mt-1">{errors.first_name}</p>}
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Middle Name
        </label>
        <input
          type="text"
          value={formData.middle_name || ''}
          onChange={(e) => updateField('middle_name', e.target.value)}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="M."
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Last Name <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          value={formData.last_name}
          onChange={(e) => updateField('last_name', e.target.value)}
          className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.last_name ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="Doe"
        />
        {errors.last_name && <p className="text-sm text-red-600 mt-1">{errors.last_name}</p>}
      </div>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Email Address <span className="text-red-500">*</span>
        </label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => updateField('email', e.target.value)}
          className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
          placeholder="john.doe@email.com"
        />
        {errors.email && <p className="text-sm text-red-600 mt-1">{errors.email}</p>}
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Phone Number
        </label>
        <input
          type="tel"
          value={formData.phone_primary || ''}
          onChange={(e) => updateField('phone_primary', e.target.value)}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="(555) 123-4567"
        />
      </div>
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Street Address
      </label>
      <input
        type="text"
        value={formData.address_line1 || ''}
        onChange={(e) => updateField('address_line1', e.target.value)}
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="123 Main Street"
      />
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Address Line 2
      </label>
      <input
        type="text"
        value={formData.address_line2 || ''}
        onChange={(e) => updateField('address_line2', e.target.value)}
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Apt, Suite, etc. (optional)"
      />
    </div>

    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          City
        </label>
        <input
          type="text"
          value={formData.city || ''}
          onChange={(e) => updateField('city', e.target.value)}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Richmond"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          State
        </label>
        <select
          value={formData.state}
          onChange={(e) => updateField('state', e.target.value)}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="VA">Virginia</option>
          <option value="MD">Maryland</option>
          <option value="DC">Washington DC</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          ZIP Code
        </label>
        <input
          type="text"
          value={formData.zip_code || ''}
          onChange={(e) => updateField('zip_code', e.target.value)}
          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="23220"
        />
      </div>
    </div>
  </div>
);

const Step2EmergencyContact: React.FC<any> = ({ formData, updateField, errors }) => (
  <div className="space-y-6">
    <div>
      <h3 className="text-2xl font-bold text-gray-900 mb-2">Emergency Contact</h3>
      <p className="text-gray-600">Who should we contact in case of emergency?</p>
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Contact Name
      </label>
      <input
        type="text"
        value={formData.emergency_contact_name || ''}
        onChange={(e) => updateField('emergency_contact_name', e.target.value)}
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Jane Doe"
      />
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Contact Phone
      </label>
      <input
        type="tel"
        value={formData.emergency_contact_phone || ''}
        onChange={(e) => updateField('emergency_contact_phone', e.target.value)}
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="(555) 987-6543"
      />
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Relationship
      </label>
      <input
        type="text"
        value={formData.emergency_contact_relationship || ''}
        onChange={(e) => updateField('emergency_contact_relationship', e.target.value)}
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Spouse, Parent, Friend, etc."
      />
    </div>
  </div>
);

const Step3Skills: React.FC<any> = ({ formData, updateField, errors }) => (
  <div className="space-y-6">
    <div>
      <h3 className="text-2xl font-bold text-gray-900 mb-2">Skills & Availability</h3>
      <p className="text-gray-600">Tell us about your skills and when you're available</p>
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Current Occupation
      </label>
      <input
        type="text"
        value={formData.occupation || ''}
        onChange={(e) => updateField('occupation', e.target.value)}
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Registered Nurse, Teacher, etc."
      />
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Skills & Certifications
      </label>
      <textarea
        value={formData.skills || ''}
        onChange={(e) => updateField('skills', e.target.value)}
        rows={4}
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="CPR, First Aid, Medical Training, Languages, etc."
      />
      <p className="text-sm text-gray-500 mt-1">
        List any relevant skills, certifications, or training you have
      </p>
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Languages Spoken
      </label>
      <input
        type="text"
        value={formData.languages || ''}
        onChange={(e) => updateField('languages', e.target.value)}
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="English, Spanish, etc."
      />
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        General Availability
      </label>
      <textarea
        value={formData.availability || ''}
        onChange={(e) => updateField('availability', e.target.value)}
        rows={3}
        className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Weekdays, Weekends, Evenings, etc."
      />
      <p className="text-sm text-gray-500 mt-1">
        When are you typically available to volunteer?
      </p>
    </div>
  </div>
);

const Step4Password: React.FC<any> = ({ formData, updateField, errors }) => (
  <div className="space-y-6">
    <div>
      <h3 className="text-2xl font-bold text-gray-900 mb-2">Create Your Account</h3>
      <p className="text-gray-600">Choose a secure password for your volunteer portal</p>
    </div>

    <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
      <p className="text-sm text-blue-800">
        <strong>Password Requirements:</strong>
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li>At least 8 characters long</li>
          <li>Include uppercase and lowercase letters</li>
          <li>Include at least one number</li>
          <li>Include at least one special character</li>
        </ul>
      </p>
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Password <span className="text-red-500">*</span>
      </label>
      <input
        type="password"
        value={formData.password}
        onChange={(e) => updateField('password', e.target.value)}
        className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.password ? 'border-red-500' : 'border-gray-300'}`}
        placeholder="Enter a secure password"
      />
      {errors.password && <p className="text-sm text-red-600 mt-1">{errors.password}</p>}
    </div>

    <div>
      <label className="block text-sm font-semibold text-gray-700 mb-2">
        Confirm Password <span className="text-red-500">*</span>
      </label>
      <input
        type="password"
        value={formData.password_confirm}
        onChange={(e) => updateField('password_confirm', e.target.value)}
        className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.password_confirm ? 'border-red-500' : 'border-gray-300'}`}
        placeholder="Re-enter your password"
      />
      {errors.password_confirm && <p className="text-sm text-red-600 mt-1">{errors.password_confirm}</p>}
    </div>
  </div>
);

const Step5Review: React.FC<any> = ({ formData }) => (
  <div className="space-y-6">
    <div>
      <h3 className="text-2xl font-bold text-gray-900 mb-2">Review Your Information</h3>
      <p className="text-gray-600">Please review your information before submitting</p>
    </div>

    <div className="bg-gray-50 rounded-lg p-6 space-y-4">
      <div>
        <h4 className="font-semibold text-gray-700 mb-2">Personal Information</h4>
        <div className="text-sm text-gray-600 space-y-1">
          <p><strong>Name:</strong> {formData.first_name} {formData.middle_name} {formData.last_name}</p>
          <p><strong>Email:</strong> {formData.email}</p>
          {formData.phone_primary && <p><strong>Phone:</strong> {formData.phone_primary}</p>}
          {formData.address_line1 && (
            <p><strong>Address:</strong> {formData.address_line1}, {formData.city}, {formData.state} {formData.zip_code}</p>
          )}
        </div>
      </div>

      {(formData.emergency_contact_name || formData.emergency_contact_phone) && (
        <div>
          <h4 className="font-semibold text-gray-700 mb-2">Emergency Contact</h4>
          <div className="text-sm text-gray-600 space-y-1">
            {formData.emergency_contact_name && <p><strong>Name:</strong> {formData.emergency_contact_name}</p>}
            {formData.emergency_contact_phone && <p><strong>Phone:</strong> {formData.emergency_contact_phone}</p>}
            {formData.emergency_contact_relationship && <p><strong>Relationship:</strong> {formData.emergency_contact_relationship}</p>}
          </div>
        </div>
      )}

      <div>
        <h4 className="font-semibold text-gray-700 mb-2">Skills & Availability</h4>
        <div className="text-sm text-gray-600 space-y-1">
          {formData.occupation && <p><strong>Occupation:</strong> {formData.occupation}</p>}
          {formData.skills && <p><strong>Skills:</strong> {formData.skills}</p>}
          {formData.languages && <p><strong>Languages:</strong> {formData.languages}</p>}
          {formData.availability && <p><strong>Availability:</strong> {formData.availability}</p>}
        </div>
      </div>
    </div>

    <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4">
      <p className="text-sm text-yellow-800">
        <strong>⚠️ Note:</strong> After submitting, your application will be reviewed by a coordinator. You'll receive an email notification once your application has been approved.
      </p>
    </div>
  </div>
);