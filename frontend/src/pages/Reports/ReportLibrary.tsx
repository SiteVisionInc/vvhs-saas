// frontend/src/pages/Reports/ReportLibrary.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';

interface SavedReport {
  id: number;
  name: string;
  description: string;
  report_type: string;
  last_generated_at: string | null;
  created_at: string;
}

export const ReportLibrary: React.FC = () => {
  const [reports, setReports] = useState<SavedReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReports();
  }, []);

  const loadReports = async () => {
    try {
      const response = await api.client.get('/v1/reporting/reports');
      setReports(response.data);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteReport = async (reportId: number) => {
    try {
      const response = await api.client.post(`/v1/reporting/reports/${reportId}/execute`, {
        export_format: 'excel'
      });
      
      alert('Report generated successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to execute report');
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Report Library</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((report) => (
          <div key={report.id} className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              {report.name}
            </h3>
            <p className="text-gray-600 mb-4">{report.description}</p>
            
            <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
                {report.report_type}
              </span>
              {report.last_generated_at && (
                <span>
                  Last run: {new Date(report.last_generated_at).toLocaleDateString()}
                </span>
              )}
            </div>

            <button
              onClick={() => handleExecuteReport(report.id)}
              className="w-full px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700"
            >
              Run Report
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
