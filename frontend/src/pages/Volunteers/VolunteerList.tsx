import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Volunteer } from '../../types';
import { Link } from 'react-router-dom';


export const VolunteerList: React.FC = () => {
  const [volunteers, setVolunteers] = useState<Volunteer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    loadVolunteers();
  }, []);

  const loadVolunteers = async () => {
    try {
      setLoading(true);
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

  // Helper function to get status
  const getStatus = (volunteer: Volunteer): string => {
    return volunteer.application_status || volunteer.status || 'unknown';
  };

  // Helper function to get hours
  const getHours = (volunteer: Volunteer): number => {
    return volunteer.total_hours ?? volunteer.hours_completed ?? 0;
  };

  // Filter volunteers based on search and status
  const filteredVolunteers = volunteers.filter(volunteer => {
    const matchesSearch = 
      volunteer.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      volunteer.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      volunteer.email.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || getStatus(volunteer) === filterStatus;
    
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const statusColors = {
      'approved': 'bg-green-100 text-green-800',
      'active': 'bg-green-100 text-green-800',
      'pending': 'bg-yellow-100 text-yellow-800',
      'incomplete': 'bg-gray-100 text-gray-800',
      'working': 'bg-blue-100 text-blue-800',
      'rejected': 'bg-red-100 text-red-800',
      'inactive': 'bg-gray-100 text-gray-800',
      'unknown': 'bg-gray-100 text-gray-800'
    };
    
    return statusColors[status as keyof typeof statusColors] || statusColors.unknown;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-xl">Loading volunteers...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Volunteers</h1>
          <p className="text-gray-600 mt-1">Manage your volunteer database</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
          + Add Volunteer
        </button>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold">{volunteers.length}</div>
          <div className="text-sm text-gray-600">Total Volunteers</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-green-600">
            {volunteers.filter(v => getStatus(v) === 'approved' || getStatus(v) === 'active').length}
          </div>
          <div className="text-sm text-gray-600">Approved</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-yellow-600">
            {volunteers.filter(v => getStatus(v) === 'pending').length}
          </div>
          <div className="text-sm text-gray-600">Pending</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-2xl font-bold text-blue-600">
            {volunteers.reduce((sum, v) => sum + getHours(v), 0)}
          </div>
          <div className="text-sm text-gray-600">Total Hours</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Status</option>
            <option value="approved">Approved</option>
            <option value="active">Active</option>
            <option value="pending">Pending</option>
            <option value="incomplete">Incomplete</option>
            <option value="working">Working</option>
            <option value="rejected">Rejected</option>
            <option value="inactive">Inactive</option>
          </select>
          <button
            onClick={loadVolunteers}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Table */}
      {filteredVolunteers.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500">
            {searchTerm || filterStatus !== 'all' 
              ? 'No volunteers found matching your filters.' 
              : 'No volunteers registered yet.'}
          </p>
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Hours
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Joined
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredVolunteers.map((volunteer) => (
                <tr key={volunteer.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        {volunteer.first_name} {volunteer.last_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        ID: {volunteer.id}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm text-gray-900">{volunteer.email}</div>
                      <div className="text-sm text-gray-500">{volunteer.phone || 'No phone'}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusBadge(getStatus(volunteer))}`}>
                      {getStatus(volunteer)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {getHours(volunteer)} hrs
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(volunteer.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
				    <Link
						to={`/volunteers/${volunteer.id}/training`}
						className="text-purple-600 hover:text-purple-900 mr-3"
					>
						Training
					</Link>
                    <button
                      className="text-indigo-600 hover:text-indigo-900 mr-3"
                      onClick={() => console.log('View', volunteer.id)}
                    >
                      View
                    </button>
                    <button
                      className="text-blue-600 hover:text-blue-900 mr-3"
                      onClick={() => console.log('Edit', volunteer.id)}
                    >
                      Edit
                    </button>
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
      )}
    </div>
  );
};