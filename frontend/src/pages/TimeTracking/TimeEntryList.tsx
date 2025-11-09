// frontend/src/pages/TimeTracking/TimeEntryList.tsx - FIXED with debugging
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { useAuth } from '../../context/AuthContext';

interface TimeEntry {
  id: number;
  volunteer_id: number;
  volunteer_name: string;
  event_name: string | null;
  check_in_time: string;
  check_out_time: string | null;
  hours_decimal: number | null;
  entry_method: string;
  status: string;
  volunteer_notes: string | null;
  coordinator_notes: string | null;
}

export const TimeEntryList: React.FC = () => {
  const { user } = useAuth();
  const [entries, setEntries] = useState<TimeEntry[]>([]);
  const [pendingOnly, setPendingOnly] = useState(true);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEntries, setSelectedEntries] = useState<Set<number>>(new Set());

  useEffect(() => {
    loadEntries();
  }, [pendingOnly]);

  const loadEntries = async () => {
    try {
      console.log('🔍 Loading time entries... pendingOnly:', pendingOnly);
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      if (pendingOnly) params.append('status', 'pending');
      
      const url = `/v1/time-tracking/entries?${params}`;
      console.log('📡 API URL:', url);
      
      const response = await api.client.get(url);
      console.log('✅ API Response:', response.data);
      console.log('📊 Entries count:', response.data?.length || 0);
      
      if (Array.isArray(response.data)) {
        setEntries(response.data);
        console.log('✓ Set entries state with', response.data.length, 'items');
      } else {
        console.error('❌ Response is not an array:', response.data);
        setError('Invalid response format from server');
        setEntries([]);
      }
    } catch (error: any) {
      console.error('❌ Failed to load time entries:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      setError(error.response?.data?.detail || 'Failed to load time entries');
      setEntries([]);
    } finally {
      setLoading(false);
      console.log('🏁 Loading complete. Final entries:', entries.length);
    }
  };

  const handleApprove = async (entryId: number) => {
    try {
      await api.client.patch(`/v1/time-tracking/entries/${entryId}/approve`, {
        status: 'approved',
        coordinator_notes: null
      });
      alert('Entry approved successfully!');
      loadEntries();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to approve entry');
    }
  };

  const handleReject = async (entryId: number) => {
    const reason = window.prompt('Reason for rejection (optional):');
    
    try {
      await api.client.patch(`/v1/time-tracking/entries/${entryId}/approve`, {
        status: 'rejected',
        rejection_reason: reason || 'No reason provided'
      });
      alert('Entry rejected');
      loadEntries();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to reject entry');
    }
  };

  const handleBulkApprove = async () => {
    if (selectedEntries.size === 0) {
      alert('No entries selected');
      return;
    }

    if (!window.confirm(`Approve ${selectedEntries.size} entries?`)) return;

    try {
      await api.client.post('/v1/time-tracking/entries/bulk-approve', {
        entry_ids: Array.from(selectedEntries),
        action: 'approve'
      });
      alert(`Approved ${selectedEntries.size} entries!`);
      setSelectedEntries(new Set());
      loadEntries();
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to bulk approve');
    }
  };

  const toggleSelection = (id: number) => {
    const newSelected = new Set(selectedEntries);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedEntries(newSelected);
  };

  const toggleAll = () => {
    if (selectedEntries.size === entries.length) {
      setSelectedEntries(new Set());
    } else {
      setSelectedEntries(new Set(entries.map(e => e.id)));
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  console.log('🎨 Rendering TimeEntryList with', entries.length, 'entries');

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading time entries...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Time Entries</h1>
          <p className="text-gray-600 mt-1">Review and approve volunteer hours</p>
        </div>
        
        {selectedEntries.size > 0 && (
          <button
            onClick={handleBulkApprove}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-semibold"
          >
            ✓ Approve {selectedEntries.size} Selected
          </button>
        )}
      </div>

      {/* Debug Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
        <h3 className="font-semibold text-blue-900 mb-2">Debug Info:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Entries loaded: {entries.length}</li>
          <li>• Pending only filter: {pendingOnly ? 'ON' : 'OFF'}</li>
          <li>• Loading state: {loading ? 'true' : 'false'}</li>
          <li>• Error: {error || 'none'}</li>
          <li>• User: {user?.first_name} {user?.last_name} (tenant: {user?.tenant_id})</li>
        </ul>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <p className="text-red-800 font-semibold">Error:</p>
          <p className="text-red-700">{error}</p>
          <button 
            onClick={loadEntries}
            className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="flex items-center justify-between">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={pendingOnly}
              onChange={(e) => {
                console.log('Toggle pending only:', e.target.checked);
                setPendingOnly(e.target.checked);
              }}
              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="ml-2 text-sm font-medium text-gray-700">
              Show pending only
            </span>
          </label>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              {entries.length} {entries.length === 1 ? 'entry' : 'entries'}
            </span>
            <button
              onClick={loadEntries}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm font-medium"
            >
              🔄 Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      {entries.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p className="text-xl font-semibold text-gray-700 mb-2">
            No time entries found
          </p>
          <p className="text-gray-500">
            {pendingOnly 
              ? 'There are no pending time entries to approve.' 
              : 'No time entries have been created yet.'}
          </p>
          <button
            onClick={() => setPendingOnly(!pendingOnly)}
            className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {pendingOnly ? 'Show All Entries' : 'Show Pending Only'}
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left">
                  <input
                    type="checkbox"
                    checked={entries.length > 0 && selectedEntries.size === entries.length}
                    onChange={toggleAll}
                    className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Volunteer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Event
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Check In
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Check Out
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hours
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Method
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {entries.map((entry) => (
                <tr key={entry.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    {entry.status === 'pending' && (
                      <input
                        type="checkbox"
                        checked={selectedEntries.has(entry.id)}
                        onChange={() => toggleSelection(entry.id)}
                        className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{entry.volunteer_name}</div>
                    <div className="text-xs text-gray-500">ID: {entry.volunteer_id}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {entry.event_name || <span className="text-gray-400">General Hours</span>}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {formatDateTime(entry.check_in_time)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {entry.check_out_time ? formatDateTime(entry.check_out_time) : <span className="text-gray-400">-</span>}
                  </td>
                  <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                    {entry.hours_decimal?.toFixed(2) || '0.00'}
                  </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                      {entry.entry_method}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(entry.status)}`}>
                      {entry.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    {entry.status === 'pending' ? (
                      <>
                        <button
                          onClick={() => handleApprove(entry.id)}
                          className="text-green-600 hover:text-green-900 font-medium text-sm"
                        >
                          ✓ Approve
                        </button>
                        <button
                          onClick={() => handleReject(entry.id)}
                          className="text-red-600 hover:text-red-900 font-medium text-sm"
                        >
                          ✗ Reject
                        </button>
                      </>
                    ) : (
                      <span className="text-gray-400 text-sm">No actions</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};