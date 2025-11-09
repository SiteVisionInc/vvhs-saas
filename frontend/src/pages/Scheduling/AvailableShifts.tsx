import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';

interface AvailableShift {
  id: number;
  event_id: number;
  name: string;
  start_time: string;
  end_time: string;
  location: string;
  max_volunteers: number;
  current_volunteers: number;
  available_spots: number;
  waitlist_count: number;
  allow_self_signup: boolean;
  enable_waitlist: boolean;
  required_skills: string[];
  event_name: string;
  event_description: string;
}

export const AvailableShifts: React.FC = () => {
  const [shifts, setShifts] = useState<AvailableShift[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({
    startDate: '',
    endDate: '',
    includeFull: false
  });

  useEffect(() => {
    loadAvailableShifts();
  }, [filter]);

  const loadAvailableShifts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filter.startDate) params.append('start_date', filter.startDate);
      if (filter.endDate) params.append('end_date', filter.endDate);
      if (filter.includeFull) params.append('include_full', 'true');
      
      const response = await api.client.get(`/v1/scheduling/shifts/available?${params}`);
      setShifts(response.data);
    } catch (error) {
      console.error('Failed to load shifts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (shiftId: number) => {
    if (!window.confirm('Sign up for this shift?')) return;

    try {
      await api.client.post(`/v1/scheduling/shifts/${shiftId}/signup`, {
        shift_id: shiftId,
        notes: ''
      });
      alert('Successfully signed up!');
      loadAvailableShifts();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to sign up');
    }
  };

  const handleJoinWaitlist = async (shiftId: number) => {
    if (!window.confirm('Join the waitlist for this shift?')) return;

    try {
      await api.client.post(`/v1/scheduling/shifts/${shiftId}/waitlist`, {
        shift_id: shiftId,
        notes: '',
        auto_accept: true
      });
      alert('Added to waitlist!');
      loadAvailableShifts();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to join waitlist');
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
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
          Available Shifts
        </h1>
        <p className="text-gray-600">Browse and sign up for volunteer opportunities</p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={filter.startDate}
              onChange={(e) => setFilter({ ...filter, startDate: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              End Date
            </label>
            <input
              type="date"
              value={filter.endDate}
              onChange={(e) => setFilter({ ...filter, endDate: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex items-end">
            <label className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={filter.includeFull}
                onChange={(e) => setFilter({ ...filter, includeFull: e.target.checked })}
                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="ml-2 text-sm font-medium text-gray-700">
                Show full shifts
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Shifts Grid */}
      {shifts.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <svg
            className="mx-auto h-16 w-16 text-gray-400 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          <p className="text-xl font-semibold text-gray-700 mb-2">
            No available shifts found
          </p>
          <p className="text-gray-500">
            Try adjusting your filters or check back later
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {shifts.map((shift) => (
            <div
              key={shift.id}
              className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
            >
              {/* Shift Header */}
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4">
                <h3 className="text-xl font-bold text-white mb-1">
                  {shift.name}
                </h3>
                <p className="text-blue-100 text-sm">{shift.event_name}</p>
              </div>

              {/* Shift Details */}
              <div className="p-6">
                {/* Date/Time */}
                <div className="mb-4">
                  <div className="flex items-center text-gray-700 mb-2">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="font-semibold">{formatDateTime(shift.start_time)}</span>
                  </div>
                  <div className="flex items-center text-gray-600 text-sm ml-7">
                    to {formatDateTime(shift.end_time)}
                  </div>
                </div>

                {/* Location */}
                {shift.location && (
                  <div className="flex items-center text-gray-700 mb-4">
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span>{shift.location}</span>
                  </div>
                )}

                {/* Capacity Bar */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>
                      {shift.current_volunteers} / {shift.max_volunteers} volunteers
                    </span>
                    <span>
                      {shift.available_spots} {shift.available_spots === 1 ? 'spot' : 'spots'} left
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all duration-500 ${
                        shift.available_spots === 0
                          ? 'bg-red-500'
                          : shift.available_spots <= 2
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{
                        width: `${(shift.current_volunteers / shift.max_volunteers) * 100}%`
                      }}
                    />
                  </div>
                </div>

                {/* Required Skills */}
                {shift.required_skills && shift.required_skills.length > 0 && (
                  <div className="mb-4">
                    <p className="text-sm font-semibold text-gray-700 mb-2">
                      Required Skills:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {shift.required_skills.map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Waitlist Info */}
                {shift.waitlist_count > 0 && (
                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 mb-4">
                    <p className="text-sm text-yellow-800">
                      <strong>{shift.waitlist_count}</strong> {shift.waitlist_count === 1 ? 'person' : 'people'} on waitlist
                    </p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3">
                  {shift.available_spots > 0 ? (
                    <button
                      onClick={() => handleSignup(shift.id)}
                      className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold py-3 rounded-lg hover:from-green-600 hover:to-green-700 transition-all shadow-md hover:shadow-lg"
                    >
                      ✓ Sign Up
                    </button>
                  ) : shift.enable_waitlist ? (
                    <button
                      onClick={() => handleJoinWaitlist(shift.id)}
                      className="flex-1 bg-gradient-to-r from-yellow-500 to-yellow-600 text-white font-semibold py-3 rounded-lg hover:from-yellow-600 hover:to-yellow-700 transition-all shadow-md hover:shadow-lg"
                    >
                      Join Waitlist
                    </button>
                  ) : (
                    <button
                      disabled
                      className="flex-1 bg-gray-300 text-gray-500 font-semibold py-3 rounded-lg cursor-not-allowed"
                    >
                      Full
                    </button>
                  )}

                  <button className="px-6 py-3 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors">
                    Details
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