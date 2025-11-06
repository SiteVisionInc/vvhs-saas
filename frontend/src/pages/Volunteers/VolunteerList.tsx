// frontend/src/pages/Volunteers/VolunteerList.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Volunteer } from '../../types';

export const VolunteerList: React.FC = () => {
  const [volunteers, setVolunteers] = useState<Volunteer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVolunteers();
  }, []);

  const loadVolunteers = async () => {
    try {
      const data = await api.getVolunteers();
      setVolunteers(data);
    } catch (error) {
      console.error('Failed to load volunteers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this volunteer?')) return;

    try {
      await api.deleteVolunteer(id);
      setVolunteers(volunteers.filter(v => v.id !== id));
    } catch (error) {
      console.error('Failed to delete volunteer:', error);
      alert('Failed to delete volunteer. Please try again.');
    }
  };

  // Helper function to get display status
  const getStatusDisplay = (volunteer: Volunteer): string => {
    return volunteer.status || volunteer.application_status || 'pending';
  };

  // Helper function to get hours display
  const getHoursDisplay = (volunteer: Volunteer): number => {
    return volunteer.hours_completed ?? volunteer.total_hours ?? 0;
  };

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  if (!volunteers || volunteers.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Volunteers</h1>
        </div>
        <div className="bg-white shadow-md rounded-lg p-8 text-center text-gray-500">
          No volunteers registered yet.
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Volunteers</h1>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hours</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {volunteers.map((volunteer) => (
              <tr key={volunteer.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  {volunteer.first_name} {volunteer.last_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">{volunteer.email}</td>
                <td className="px-6 py-4 whitespace-nowrap">{volunteer.phone || 'N/A'}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    getStatusDisplay(volunteer) === 'active' || getStatusDisplay(volunteer) === 'approved'
                      ? 'bg-green-100 text-green-800'
                      : getStatusDisplay(volunteer) === 'pending'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {getStatusDisplay(volunteer)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">{getHoursDisplay(volunteer)}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <button
                    onClick={() => handleDelete(volunteer.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};