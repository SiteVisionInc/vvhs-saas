// frontend/src/pages/Reports/ReportsHub.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

export const ReportsHub: React.FC = () => {
  const navigate = useNavigate();

  const reportCategories = [
    {
      title: 'Volunteer Reports',
      icon: '👥',
      color: 'blue',
      reports: [
        { name: 'Volunteer Hours', path: '/reports/volunteer-hours', description: 'Individual and collective hours' },
        { name: 'Volunteer List', path: '/reports/volunteer-list', description: 'Complete volunteer roster' },
        { name: 'Training Compliance', path: '/reports/compliance', description: 'Training completion status' },
        { name: 'Volunteer Activity', path: '/reports/volunteer-activity', description: 'Engagement and participation' }
      ]
    },
    {
      title: 'Event Reports',
      icon: '📅',
      color: 'green',
      reports: [
        { name: 'Event Summary', path: '/reports/event-summary', description: 'Event attendance and outcomes' },
        { name: 'Impact Data', path: '/reports/impact', description: 'Services delivered and metrics' },
        { name: 'Event Calendar', path: '/reports/event-calendar', description: 'Upcoming and past events' }
      ]
    },
    {
      title: 'Administrative Reports',
      icon: '📊',
      color: 'purple',
      reports: [
        { name: 'Unit Metrics', path: '/reports/unit-metrics', description: 'Unit-level performance' },
        { name: 'Retention Analysis', path: '/reports/retention', description: 'Volunteer retention rates' },
        { name: 'Compliance Dashboard', path: '/reports/compliance-dashboard', description: 'Overall compliance status' }
      ]
    },
    {
      title: 'Custom Reports',
      icon: '🔧',
      color: 'orange',
      reports: [
        { name: 'Report Builder', path: '/reports/builder', description: 'Create custom reports' },
        { name: 'Saved Reports', path: '/reports/saved', description: 'Your saved report templates' },
        { name: 'Scheduled Reports', path: '/reports/scheduled', description: 'Automated report delivery' }
      ]
    }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">📊 Reports & Analytics</h1>
        <p className="text-gray-600 text-lg">
          Generate insights and track performance across your volunteer program
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total Reports Run</p>
              <p className="text-3xl font-bold text-blue-600">127</p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Saved Reports</p>
              <p className="text-3xl font-bold text-green-600">12</p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Scheduled Reports</p>
              <p className="text-3xl font-bold text-purple-600">5</p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Last Export</p>
              <p className="text-sm font-bold text-orange-600">2 hours ago</p>
            </div>
            <div className="bg-orange-100 rounded-full p-3">
              <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Report Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {reportCategories.map((category) => (
          <div key={category.title} className="bg-white rounded-xl shadow-lg overflow-hidden">
            {/* Category Header */}
            <div className={`bg-${category.color}-500 px-6 py-4`}>
              <h2 className="text-2xl font-bold text-white flex items-center">
                <span className="mr-3 text-3xl">{category.icon}</span>
                {category.title}
              </h2>
            </div>

            {/* Report List */}
            <div className="p-6 space-y-3">
              {category.reports.map((report) => (
                <button
                  key={report.name}
                  onClick={() => navigate(report.path)}
                  className="w-full text-left bg-gray-50 hover:bg-gray-100 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-1">
                        {report.name}
                      </h3>
                      <p className="text-sm text-gray-600">{report.description}</p>
                    </div>
                    <svg className="w-6 h-6 text-gray-400 ml-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="mt-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-8 text-white">
        <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/reports/builder')}
            className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all"
          >
            <h3 className="font-semibold mb-1">🔧 Build Custom Report</h3>
            <p className="text-sm text-blue-100">Create a report with custom filters</p>
          </button>

          <button
            onClick={() => navigate('/reports/volunteer-hours')}
            className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all"
          >
            <h3 className="font-semibold mb-1">⏱️ Quick Hours Report</h3>
            <p className="text-sm text-blue-100">View volunteer hours for this month</p>
          </button>

          <button
            onClick={() => navigate('/reports/saved')}
            className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg p-4 text-left transition-all"
          >
            <h3 className="font-semibold mb-1">📁 My Saved Reports</h3>
            <p className="text-sm text-blue-100">Access your report templates</p>
          </button>
        </div>
      </div>
    </div>
  );
};