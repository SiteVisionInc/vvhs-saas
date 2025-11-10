// frontend/src/pages/BehavioralHealth/BHDashboard.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
//import { PatientIntakeForm } from '../../components/BehavioralHealth/PatientIntakeForm';
//import { BedSearchInterface } from '../../components/BehavioralHealth/BedSearchInterface';
//import { FacilityReferralQueue } from '../../components/BehavioralHealth/FacilityReferralQueue';
//import { ScreeningInstruments } from '../../components/BehavioralHealth/ScreeningInstruments';
import { ScreeningInstruments, FacilityReferralQueue, BedSearchInterface, PatientIntakeForm } from '../../components/BehavioralHealth/bh_frontend_component';

export const BHDashboard: React.FC = () => {
  const [stats, setStats] = useState({
    total_patients: 0,
    total_referrals: 0,
    pending_referrals: 0,
    active_placements: 0,
    available_beds: 0
  });
  const [activeView, setActiveView] = useState<'dashboard' | 'intake' | 'bed-search' | 'referrals'>('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      // Load BH statistics
      const [patientsRes, referralsRes, bedsRes] = await Promise.all([
        api.client.get('/v1/bh/patients'),
        api.client.get('/v1/bh/referrals'),
        api.client.get('/v1/bh/facilities/search', { params: { min_available: 1 } })
      ]);

      setStats({
        total_patients: patientsRes.data.length || 0,
        total_referrals: referralsRes.data.length || 0,
        pending_referrals: referralsRes.data.filter((r: any) => r.status === 'submitted').length || 0,
        active_placements: referralsRes.data.filter((r: any) => r.status === 'placed').length || 0,
        available_beds: bedsRes.data.reduce((sum: number, facility: any) => sum + facility.available_beds, 0)
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
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          🏥 Behavioral Health Module
        </h1>
        <p className="text-gray-600 text-lg">
          Clinical workflow system for patient referrals and placements
        </p>
      </div>

      {activeView === 'dashboard' && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-blue-100 text-sm mb-1">Total Patients</p>
                  <p className="text-4xl font-bold">{stats.total_patients}</p>
                </div>
                <div className="bg-blue-400 bg-opacity-30 rounded-full p-3">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-100 text-sm mb-1">Available Beds</p>
                  <p className="text-4xl font-bold">{stats.available_beds}</p>
                </div>
                <div className="bg-green-400 bg-opacity-30 rounded-full p-3">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-yellow-100 text-sm mb-1">Pending Referrals</p>
                  <p className="text-4xl font-bold">{stats.pending_referrals}</p>
                </div>
                <div className="bg-yellow-400 bg-opacity-30 rounded-full p-3">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-purple-100 text-sm mb-1">Active Placements</p>
                  <p className="text-4xl font-bold">{stats.active_placements}</p>
                </div>
                <div className="bg-purple-400 bg-opacity-30 rounded-full p-3">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-indigo-100 text-sm mb-1">Total Referrals</p>
                  <p className="text-4xl font-bold">{stats.total_referrals}</p>
                </div>
                <div className="bg-indigo-400 bg-opacity-30 rounded-full p-3">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-8 text-white mb-8">
            <h2 className="text-2xl font-bold mb-6">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <button
                onClick={() => setActiveView('intake')}
                className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all"
              >
                <h3 className="font-semibold mb-1">📋 New Patient Intake</h3>
                <p className="text-sm text-blue-100">Register new patient</p>
              </button>

              <button
                onClick={() => setActiveView('bed-search')}
                className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all"
              >
                <h3 className="font-semibold mb-1">🔍 Search Beds</h3>
                <p className="text-sm text-blue-100">Find available placement</p>
              </button>

              <button
                onClick={() => setActiveView('referrals')}
                className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all"
              >
                <h3 className="font-semibold mb-1">📥 Referral Queue</h3>
                <p className="text-sm text-blue-100">Review pending referrals</p>
              </button>

              <button
                className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all"
              >
                <h3 className="font-semibold mb-1">📊 Reports</h3>
                <p className="text-sm text-blue-100">View analytics</p>
              </button>
            </div>
          </div>

          {/* Workflow Diagram */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Clinical Workflow</h2>
            <div className="flex items-center justify-between">
              <div className="text-center">
                <div className="w-20 h-20 mx-auto bg-blue-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-3xl">📋</span>
                </div>
                <p className="text-sm font-semibold">Intake</p>
              </div>
              <div className="text-gray-400 text-2xl">→</div>
              <div className="text-center">
                <div className="w-20 h-20 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-3xl">🔍</span>
                </div>
                <p className="text-sm font-semibold">Screening</p>
              </div>
              <div className="text-gray-400 text-2xl">→</div>
              <div className="text-center">
                <div className="w-20 h-20 mx-auto bg-yellow-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-3xl">🏥</span>
                </div>
                <p className="text-sm font-semibold">Bed Search</p>
              </div>
              <div className="text-gray-400 text-2xl">→</div>
              <div className="text-center">
                <div className="w-20 h-20 mx-auto bg-purple-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-3xl">📄</span>
                </div>
                <p className="text-sm font-semibold">Referral</p>
              </div>
              <div className="text-gray-400 text-2xl">→</div>
              <div className="text-center">
                <div className="w-20 h-20 mx-auto bg-indigo-100 rounded-full flex items-center justify-center mb-2">
                  <span className="text-3xl">✓</span>
                </div>
                <p className="text-sm font-semibold">Placement</p>
              </div>
            </div>
          </div>
        </>
      )}

      {activeView === 'intake' && (
        <PatientIntakeForm
          onSuccess={(patientId) => {
            alert(`Patient created with ID: ${patientId}`);
            setActiveView('dashboard');
            loadStats();
          }}
          onCancel={() => setActiveView('dashboard')}
        />
      )}

      {activeView === 'bed-search' && (
        <BedSearchInterface
          onSelectFacility={(facilityId, bedType) => {
            alert(`Selected facility ${facilityId} with bed type ${bedType}`);
            // TODO: Navigate to referral creation
          }}
        />
      )}

      {activeView === 'referrals' && (
        <div>
          <button
            onClick={() => setActiveView('dashboard')}
            className="mb-4 text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Back to Dashboard
          </button>
          <FacilityReferralQueue />
        </div>
      )}
    </div>
  );
};
