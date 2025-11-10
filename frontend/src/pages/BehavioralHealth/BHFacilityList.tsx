// frontend/src/pages/BehavioralHealth/BHFacilityList.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';

interface Facility {
  id: number;
  name: string;
  facility_type: string;
  contact_phone: string | null;
  contact_email: string | null;
  is_active: boolean;
  capabilities: string[];
}

export const BHFacilityList: React.FC = () => {
  const navigate = useNavigate();
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    loadFacilities();
  }, [filterType]);

  const loadFacilities = async () => {
    setLoading(true);
    try {
      const params = filterType !== 'all' ? { facility_type: filterType } : {};
      const data = await api.getBHFacilities(params);
      setFacilities(data || []);
    } catch (error) {
      console.error('Failed to load facilities:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Facilities</h1>
          <p className="text-gray-600 mt-1">Manage behavioral health treatment facilities</p>
        </div>
        <button className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 font-semibold">
          + Add Facility
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex gap-4 items-center">
          <label className="text-sm font-medium text-gray-700">Filter by Type:</label>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="all">All Types</option>
            <option value="hospital">Hospital</option>
            <option value="detox">Detox</option>
            <option value="residential">Residential</option>
            <option value="outpatient">Outpatient</option>
            <option value="crisis">Crisis</option>
          </select>
        </div>
      </div>

      {/* Grid */}
      {facilities.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-xl font-semibold text-gray-700 mb-2">No facilities found</p>
          <p className="text-gray-500">Add your first facility to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {facilities.map((facility) => (
            <div key={facility.id} className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
                <h3 className="text-xl font-bold text-white">{facility.name}</h3>
                <p className="text-purple-100 text-sm capitalize">{facility.facility_type}</p>
              </div>
              <div className="p-6">
                <div className="space-y-2 mb-4">
                  {facility.contact_phone && (
                    <p className="text-sm text-gray-600">📞 {facility.contact_phone}</p>
                  )}
                  {facility.contact_email && (
                    <p className="text-sm text-gray-600">📧 {facility.contact_email}</p>
                  )}
                </div>
                {facility.capabilities && facility.capabilities.length > 0 && (
                  <div className="mb-4">
                    <p className="text-xs font-semibold text-gray-500 mb-2">Capabilities:</p>
                    <div className="flex flex-wrap gap-2">
                      {facility.capabilities.map((cap, idx) => (
                        <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                          {cap}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigate(`/bh/facilities/${facility.id}/beds`)}
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                  >
                    View Beds
                  </button>
                  <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 text-sm">
                    Edit
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


// frontend/src/pages/BehavioralHealth/BHBedSearch.tsx
export const BHBedSearch: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useState({
    facility_type: '',
    bed_type: '',
    patient_age: '',
    min_available: 1
  });
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      const params = {
        ...searchParams,
        patient_age: searchParams.patient_age ? parseInt(searchParams.patient_age) : null
      };
      const data = await api.searchBHBeds(params);
      setResults(data || []);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Bed Search</h1>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Facility Type</label>
            <select
              value={searchParams.facility_type}
              onChange={(e) => setSearchParams({ ...searchParams, facility_type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
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
            <label className="block text-sm font-medium text-gray-700 mb-2">Bed Type</label>
            <select
              value={searchParams.bed_type}
              onChange={(e) => setSearchParams({ ...searchParams, bed_type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
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
            <label className="block text-sm font-medium text-gray-700 mb-2">Patient Age</label>
            <input
              type="number"
              value={searchParams.patient_age}
              onChange={(e) => setSearchParams({ ...searchParams, patient_age: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              placeholder="Optional"
            />
          </div>
        </div>

        <button
          onClick={handleSearch}
          disabled={loading}
          className="w-full px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 disabled:opacity-50"
        >
          {loading ? 'Searching...' : '🔍 Search Available Beds'}
        </button>
      </div>

      {/* Results */}
      {results.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {results.map((result, idx) => (
            <div key={idx} className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="bg-gradient-to-r from-green-500 to-green-600 px-6 py-4">
                <h3 className="text-xl font-bold text-white">{result.facility_name}</h3>
                <p className="text-green-100 text-sm capitalize">{result.facility_type}</p>
              </div>
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <div>
                    <p className="text-sm text-gray-600">Bed Type</p>
                    <p className="text-lg font-semibold text-gray-900 capitalize">{result.bed_type}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Available</p>
                    <p className="text-3xl font-bold text-green-600">{result.available_beds}</p>
                    <p className="text-xs text-gray-500">of {result.total_beds}</p>
                  </div>
                </div>
                {result.contact_phone && (
                  <p className="text-sm text-gray-600 mb-4">📞 {result.contact_phone}</p>
                )}
                <button
                  onClick={() => navigate(`/bh/referrals/new?facility=${result.facility_id}`)}
                  className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700"
                >
                  Create Referral →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


// frontend/src/pages/BehavioralHealth/BHStaleBeds.tsx
export const BHStaleBeds: React.FC = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const data = await api.getBHStaleBedAlerts(24);
      setAlerts(data || []);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Stale Bed Data Alerts</h1>
        <p className="text-gray-600 mt-1">Facilities with outdated bed availability data (&gt;24 hours old)</p>
      </div>

      {alerts.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg className="mx-auto h-16 w-16 text-green-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-xl font-semibold text-gray-700 mb-2">All bed data is current!</p>
          <p className="text-gray-500">No facilities with stale data</p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert: any) => (
            <div key={alert.facility_id} className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="bg-red-50 border-l-4 border-red-500 p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900 mb-1">{alert.facility_name}</h3>
                    <p className="text-sm text-gray-600">
                      Last updated: {new Date(alert.last_updated).toLocaleString()}
                    </p>
                    <p className="text-sm font-semibold text-red-600 mt-2">
                      ⚠️ Data is {Math.round(alert.hours_stale)} hours old
                    </p>
                  </div>
                  <div className="text-right">
                    {alert.contact_phone && (
                      <p className="text-sm text-gray-600">📞 {alert.contact_phone}</p>
                    )}
                    <button className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm">
                      Send Reminder
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


// frontend/src/pages/BehavioralHealth/BHBedManagement.tsx
export const BHBedManagement: React.FC = () => {
  const [facilities, setFacilities] = useState<any[]>([]);
  const [selectedFacility, setSelectedFacility] = useState<number | null>(null);
  const [beds, setBeds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFacilities();
  }, []);

  useEffect(() => {
    if (selectedFacility) {
      loadBeds(selectedFacility);
    }
  }, [selectedFacility]);

  const loadFacilities = async () => {
    try {
      const data = await api.getBHFacilities({ is_active: true });
      setFacilities(data || []);
      if (data && data.length > 0) {
        setSelectedFacility(data[0].id);
      }
    } catch (error) {
      console.error('Failed to load facilities:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadBeds = async (facilityId: number) => {
    try {
      const data = await api.getBHFacilityBeds(facilityId);
      setBeds(data || []);
    } catch (error) {
      console.error('Failed to load beds:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Bed Availability Management</h1>

      {/* Facility Selector */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Select Facility</label>
        <select
          value={selectedFacility || ''}
          onChange={(e) => setSelectedFacility(Number(e.target.value))}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
        >
          {facilities.map((facility) => (
            <option key={facility.id} value={facility.id}>
              {facility.name}
            </option>
          ))}
        </select>
      </div>

      {/* Bed List */}
      {beds.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-xl font-semibold text-gray-700 mb-2">No bed data for this facility</p>
          <p className="text-gray-500">Add bed availability information to get started</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {beds.map((bed: any) => (
            <div key={bed.id} className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-2 capitalize">{bed.bed_type}</h3>
              {bed.unit_name && <p className="text-sm text-gray-600 mb-4">{bed.unit_name}</p>}
              <div className="flex justify-between items-center mb-4">
                <div>
                  <p className="text-sm text-gray-600">Available</p>
                  <p className="text-3xl font-bold text-green-600">{bed.capacity_available}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-600">Total</p>
                  <p className="text-3xl font-bold text-gray-900">{bed.capacity_total}</p>
                </div>
              </div>
              <p className="text-xs text-gray-500 mb-4">
                Last updated: {new Date(bed.last_reported_at).toLocaleString()}
              </p>
              <button className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
                Update Availability
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
