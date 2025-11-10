// frontend/src/pages/BehavioralHealth/BehavioralHealthDashboard.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../services/api';

interface BHStats {
  total_patients: number;
  total_referrals: number;
  pending_referrals: number;
  active_placements: number;
  available_beds: number;
  stale_facilities: number;
}

export const BehavioralHealthDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<BHStats>({
    total_patients: 0,
    total_referrals: 0,
    pending_referrals: 0,
    active_placements: 0,
    available_beds: 0,
    stale_facilities: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      // These would be real API calls
      // For now using mock data
      setStats({
        total_patients: 127,
        total_referrals: 45,
        pending_referrals: 12,
        active_placements: 33,
        available_beds: 87,
        stale_facilities: 3
      });
    } catch (error) {
      console.error('Failed to load BH stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🧠 Behavioral Health Module
          </h1>
          <p className="text-gray-600 text-lg">
            Clinical workflow management for behavioral health patient referrals and placements
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Total Patients */}
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm font-medium mb-1">Total Patients</p>
                <p className="text-4xl font-bold">{stats.total_patients}</p>
              </div>
              <div className="bg-purple-400 bg-opacity-30 rounded-full p-4">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Pending Referrals */}
          <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-100 text-sm font-medium mb-1">Pending Referrals</p>
                <p className="text-4xl font-bold">{stats.pending_referrals}</p>
              </div>
              <div className="bg-yellow-400 bg-opacity-30 rounded-full p-4">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Active Placements */}
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm font-medium mb-1">Active Placements</p>
                <p className="text-4xl font-bold">{stats.active_placements}</p>
              </div>
              <div className="bg-green-400 bg-opacity-30 rounded-full p-4">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Available Beds */}
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm font-medium mb-1">Available Beds</p>
                <p className="text-4xl font-bold">{stats.available_beds}</p>
              </div>
              <div className="bg-blue-400 bg-opacity-30 rounded-full p-4">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
              </div>
            </div>
          </div>

          {/* Total Referrals */}
          <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-indigo-100 text-sm font-medium mb-1">Total Referrals</p>
                <p className="text-4xl font-bold">{stats.total_referrals}</p>
              </div>
              <div className="bg-indigo-400 bg-opacity-30 rounded-full p-4">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Stale Facilities */}
          <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-6 text-white transform hover:scale-105 transition-transform duration-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-red-100 text-sm font-medium mb-1">Stale Bed Data</p>
                <p className="text-4xl font-bold">{stats.stale_facilities}</p>
              </div>
              <div className="bg-red-400 bg-opacity-30 rounded-full p-4">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Clinical Workflow */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
              <h2 className="text-2xl font-bold text-white flex items-center">
                <span className="mr-3">🏥</span>
                Clinical Workflow
              </h2>
            </div>
            <div className="p-6 space-y-3">
              <button
                onClick={() => navigate('/bh/patients')}
                className="w-full text-left bg-gray-50 hover:bg-gray-100 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      Patients
                    </h3>
                    <p className="text-sm text-gray-600">Manage patient records and screenings</p>
                  </div>
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              <button
                onClick={() => navigate('/bh/referrals')}
                className="w-full text-left bg-gray-50 hover:bg-gray-100 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      Referrals
                    </h3>
                    <p className="text-sm text-gray-600">Create and manage patient referrals</p>
                  </div>
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              <button
                onClick={() => navigate('/bh/bed-search')}
                className="w-full text-left bg-gray-50 hover:bg-gray-100 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      🔍 Bed Search
                    </h3>
                    <p className="text-sm text-gray-600">Find available facility beds</p>
                  </div>
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>
            </div>
          </div>

          {/* Facility Management */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
              <h2 className="text-2xl font-bold text-white flex items-center">
                <span className="mr-3">🏢</span>
                Facility Management
              </h2>
            </div>
            <div className="p-6 space-y-3">
              <button
                onClick={() => navigate('/bh/facilities')}
                className="w-full text-left bg-gray-50 hover:bg-gray-100 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      Facilities
                    </h3>
                    <p className="text-sm text-gray-600">Manage treatment facilities</p>
                  </div>
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              <button
                onClick={() => navigate('/bh/beds')}
                className="w-full text-left bg-gray-50 hover:bg-gray-100 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      Bed Availability
                    </h3>
                    <p className="text-sm text-gray-600">Update bed capacity snapshots</p>
                  </div>
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>

              <button
                onClick={() => navigate('/bh/stale-beds')}
                className="w-full text-left bg-gray-50 hover:bg-gray-100 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      ⚠️ Stale Data Alerts
                    </h3>
                    <p className="text-sm text-gray-600">Review facilities with outdated data</p>
                  </div>
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Info Banner */}
        <div className="bg-blue-50 border-l-4 border-blue-500 p-6 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-lg font-medium text-blue-900 mb-2">
                About the Behavioral Health Module
              </h3>
              <p className="text-sm text-blue-800">
                This comprehensive clinical workflow system manages the complete lifecycle of behavioral health patient care:
                from intake and screening, through referral and placement, to discharge and follow-up. 
                It includes real-time bed availability tracking, facility management, and outcome measurement.
              </p>
              <ul className="mt-3 text-sm text-blue-800 space-y-1 list-disc list-inside">
                <li><strong>Patient Management:</strong> Track demographics, consent, and risk levels</li>
                <li><strong>Clinical Screening:</strong> C-SSRS, ASAM, PHQ-9, and custom assessments</li>
                <li><strong>Referral Workflow:</strong> Submit, track, and manage patient referrals</li>
                <li><strong>Bed Search:</strong> Real-time availability across facilities</li>
                <li><strong>Follow-Up:</strong> 30/60/90-day outcome tracking</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
