import React from 'react';
import { useAuth } from '../hooks/useAuth';

function DashboardPage() {
  const { user, isPolice } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <h1 className="text-3xl font-bold text-gray-900">
            {isPolice() ? 'Police Dashboard' : 'Citizen Dashboard'}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Welcome back, {user?.name}
          </p>
        </div>

        {/* Quick Actions */}
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900">
                  {isPolice() ? 'Create FIR' : 'Write Complaint'}
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  {isPolice()
                    ? 'Create a new First Information Report'
                    : 'Write and format a legal complaint'
                  }
                </p>
                <div className="mt-4">
                  <a
                    href={isPolice() ? '/fir' : '/complaint'}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    {isPolice() ? 'Create FIR' : 'Write Complaint'}
                  </a>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900">
                  Legal Research
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  Search Indian legal acts and sections
                </p>
                <div className="mt-4">
                  <a
                    href="/legal-search"
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-secondary-600 hover:bg-secondary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary-500"
                  >
                    Search Legal Acts
                  </a>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900">
                  {isPolice() ? 'Recent FIRs' : 'Recent Complaints'}
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  {isPolice()
                    ? 'View your recent FIR submissions'
                    : 'View your recent complaint submissions'
                  }
                </p>
                <div className="mt-4">
                  <a
                    href={isPolice() ? '/fir' : '/complaint'}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                  >
                    View {isPolice() ? 'FIRs' : 'Complaints'}
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white overflow-hidden shadow sm:rounded-md">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Recent Activity
              </h3>
            </div>
            <div className="border-t border-gray-200">
              <div className="px-4 py-3 sm:px-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      No recent activity
                    </p>
                    <p className="text-sm text-gray-500">
                      {isPolice()
                        ? 'Start creating FIRs or searching legal acts'
                        : 'Start writing complaints or searching legal information'
                      }
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;