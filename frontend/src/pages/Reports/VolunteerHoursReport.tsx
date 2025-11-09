// frontend/src/pages/Reports/VolunteerHoursReport.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';

interface HoursData {
  volunteer_id: number;
  volunteer_name: string;
  total_hours: number;
  approved_hours: number;
  pending_hours: number;
  events_attended: number;
}

export const VolunteerHoursReport: React.FC = () => {
  const [data, setData] = useState<HoursData[]>([]);
  const [loading, setLoading] = useState(true);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await api.client.get(`/v1/reporting/reports/volunteer-hours?${params}`);
      setData(response.data);
    } catch (error) {
      console.error('Failed to load report:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const response = await api.client.get('/v1/reporting/reports/volunteer-hours', {
        responseType: 'blob',
        headers: { Accept: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'volunteer-hours.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Failed to export report');
    }
  };

  const totalHours = data.reduce((sum, row) => sum + row.total_hours, 0);

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Volunteer Hours Report</h1>
          <p className="text-gray-600">Individual and collective hours</p>
        </div>
        <button
          onClick={handleExport}
          className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700"
        >
          📥 Export to Excel
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={loadReport}
              className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Volunteers</p>
          <p className="text-2xl font-bold text-gray-900">{data.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Hours</p>
          <p className="text-2xl font-bold text-blue-600">{totalHours.toFixed(1)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Average Hours</p>
          <p className="text-2xl font-bold text-green-600">
            {data.length > 0 ? (totalHours / data.length).toFixed(1) : '0'}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <p className="text-sm text-gray-600">Total Events</p>
          <p className="text-2xl font-bold text-purple-600">
            {data.reduce((sum, row) => sum + row.events_attended, 0)}
          </p>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Volunteer</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Total Hours</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Approved</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Pending</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Events</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((row) => (
              <tr key={row.volunteer_id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{row.volunteer_name}</td>
                <td className="px-6 py-4 text-sm text-right font-semibold">{row.total_hours.toFixed(1)}</td>
                <td className="px-6 py-4 text-sm text-right text-green-600">{row.approved_hours.toFixed(1)}</td>
                <td className="px-6 py-4 text-sm text-right text-yellow-600">{row.pending_hours.toFixed(1)}</td>
                <td className="px-6 py-4 text-sm text-right text-gray-600">{row.events_attended}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
