import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { Link } from 'react-router-dom';

interface DashboardStats {
  totalVolunteers: number;
  approvedVolunteers: number;
  pendingApplications: number;
  totalEvents: number;
  upcomingEvents: number;
  activeEvents: number;
}

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalVolunteers: 0,
    approvedVolunteers: 0,
    pendingApplications: 0,
    totalEvents: 0,
    upcomingEvents: 0,
    activeEvents: 0
  });
  const [loading, setLoading] = useState(true);
  const [recentEvents, setRecentEvents] = useState<any[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Fetch volunteers
      const volunteers = await api.getVolunteers();
      
      // Fetch events
      const events = await api.getEvents();
      
      // Calculate stats
      const now = new Date();
      const volunteerStats = {
        totalVolunteers: volunteers.length,
        approvedVolunteers: volunteers.filter(v => 
          v.status === 'approved' || v.application_status === 'approved'
        ).length,
        pendingApplications: volunteers.filter(v => 
          v.status === 'pending' || v.application_status === 'pending'
        ).length,
      };

      const eventStats = {
        totalEvents: events.length,
        upcomingEvents: events.filter(e => {
          const eventDate = new Date(e.event_date || e.start_date || '');
          return eventDate > now;
        }).length,
        activeEvents: events.filter(e => {
          const eventDate = new Date(e.event_date || e.start_date || '');
          return eventDate.toDateString() === now.toDateString();
        }).length,
      };

      setStats({
        ...volunteerStats,
        ...eventStats
      });
      
      // Get recent events (last 5)
      setRecentEvents(events.slice(0, 5));
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="text-xl">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Welcome back, {user?.first_name || user?.username}!</h1>
        <p className="text-gray-600 mt-2">
          Role: <span className="font-semibold capitalize">{user?.role?.replace('_', ' ')}</span> | 
          Tenant ID: <span className="font-semibold">{user?.tenant_id}</span>
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-blue-600">{stats.totalVolunteers}</div>
          <div className="text-gray-600 text-sm mt-2">Total Volunteers</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-green-600">{stats.approvedVolunteers}</div>
          <div className="text-gray-600 text-sm mt-2">Approved</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-yellow-600">{stats.pendingApplications}</div>
          <div className="text-gray-600 text-sm mt-2">Pending</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-purple-600">{stats.totalEvents}</div>
          <div className="text-gray-600 text-sm mt-2">Total Events</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-indigo-600">{stats.upcomingEvents}</div>
          <div className="text-gray-600 text-sm mt-2">Upcoming</div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-2xl font-bold text-red-600">{stats.activeEvents}</div>
          <div className="text-gray-600 text-sm mt-2">Active Today</div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link to="/volunteers" className="block w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-center">
              Manage Volunteers
            </Link>
            <Link to="/events" className="block w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-center">
              Manage Events
            </Link>
            <button className="w-full bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700">
              Create New Event
            </button>
            <button className="w-full bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
              Generate Report
            </button>
          </div>
        </div>

        {/* Recent Events */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Events</h2>
          {recentEvents.length > 0 ? (
            <div className="space-y-3">
              {recentEvents.map((event) => (
                <div key={event.id} className="border-l-4 border-blue-500 pl-3 py-2">
                  <div className="font-semibold">{event.title || event.name}</div>
                  <div className="text-sm text-gray-600">
                    {event.location} • {new Date(event.event_date || event.start_date || '').toLocaleDateString()}
                  </div>
                  <div className="text-sm text-gray-500">
                    {event.registered_volunteers || 0} / {event.max_volunteers || 0} volunteers
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No events scheduled</p>
          )}
        </div>
      </div>

      {/* System Info */}
      <div className="bg-gray-100 rounded-lg p-4">
        <h3 className="font-semibold text-gray-700 mb-2">System Information</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Version:</span> 
            <span className="font-semibold ml-2">1.0.0</span>
          </div>
          <div>
            <span className="text-gray-600">Environment:</span> 
            <span className="font-semibold ml-2">Production</span>
          </div>
          <div>
            <span className="text-gray-600">Last Login:</span> 
            <span className="font-semibold ml-2">{new Date().toLocaleString()}</span>
          </div>
          <div>
            <span className="text-gray-600">Status:</span> 
            <span className="font-semibold text-green-600 ml-2">● Online</span>
          </div>
        </div>
      </div>
    </div>
  );
};