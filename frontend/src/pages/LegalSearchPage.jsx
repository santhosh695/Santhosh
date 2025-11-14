import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../hooks/useAuth';

function LegalSearchPage() {
  const { t } = useTranslation();
  const { user, isPolice } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('acts');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAct, setSelectedAct] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!searchQuery.trim()) return;

    setIsLoading(true);

    try {
      // Mock search results - in real implementation, this would call API
      const mockResults = [
        {
          id: 1,
          title: 'Indian Penal Code, 1860 - Section 420',
          type: 'section',
          act: 'Indian Penal Code',
          section: '420',
          description: 'Cheating and dishonestly inducing delivery of property',
          punishment: 'Imprisonment up to 7 years and fine'
        },
        {
          id: 2,
          title: 'Code of Criminal Procedure, 1973 - Section 154',
          type: 'section',
          act: 'CrPC',
          section: '154',
          description: 'Information in cognizable cases',
          punishment: 'Police must register FIR in cognizable offenses'
        },
        {
          id: 3,
          title: 'Indian Evidence Act, 1872 - Section 3',
          type: 'section',
          act: 'Indian Evidence Act',
          section: '3',
          description: 'Interpretation clause - Evidence includes oral and documentary evidence',
          punishment: 'N/A'
        }
      ];

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      setSearchResults(mockResults.filter(result =>
        result.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        result.description.toLowerCase().includes(searchQuery.toLowerCase())
      ));
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleActSelect = (act) => {
    setSelectedAct(act);
  };

  const closeActDetails = () => {
    setSelectedAct(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Legal Research & Search
          </h1>
          <p className="text-gray-600">
            Search Indian legal acts, sections, and case laws
          </p>
        </div>

        {/* Search Section */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="p-6">
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <label htmlFor="search_query" className="block text-sm font-medium text-gray-700 mb-2">
                    Search Legal Database
                  </label>
                  <input
                    type="text"
                    id="search_query"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search acts, sections, or keywords..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label htmlFor="search_type" className="block text-sm font-medium text-gray-700 mb-2">
                    Search Type
                  </label>
                  <select
                    id="search_type"
                    value={searchType}
                    onChange={(e) => setSearchType(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="acts">All Acts</option>
                    <option value="ipc">Indian Penal Code</option>
                    <option value="crpc">Code of Criminal Procedure</option>
                    <option value="cpc">Code of Civil Procedure</option>
                    <option value="evidence">Indian Evidence Act</option>
                  </select>
                </div>

                <div className="flex items-end">
                  <button
                    type="submit"
                    disabled={isLoading || !searchQuery.trim()}
                    className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
                  >
                    {isLoading ? 'Searching...' : 'Search'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        {/* Quick Access Acts */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Indian Penal Code</h3>
            <p className="text-gray-600 text-sm mb-3">Criminal offenses and punishments in India</p>
            <button
              onClick={() => handleSearch({ preventDefault: () => {}, target: { elements: { search_query: { value: 'IPC' } } } })}
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              Browse IPC →
            </button>
          </div>

          <div className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Code of Criminal Procedure</h3>
            <p className="text-gray-600 text-sm mb-3">Procedures for criminal trials and investigations</p>
            <button
              onClick={() => handleSearch({ preventDefault: () => {}, target: { elements: { search_query: { value: 'CrPC' } } } })}
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              Browse CrPC →
            </button>
          </div>

          <div className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Indian Evidence Act</h3>
            <p className="text-gray-600 text-sm mb-3">Rules of evidence in Indian courts</p>
            <button
              onClick={() => handleSearch({ preventDefault: () => {}, target: { elements: { search_query: { value: 'Evidence Act' } } } })}
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              Browse Evidence Act →
            </button>
          </div>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Search Results ({searchResults.length})
              </h2>
            </div>
            <div className="divide-y divide-gray-200">
              {searchResults.map((result) => (
                <div key={result.id} className="p-6 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        {result.title}
                      </h3>
                      <p className="text-gray-600 mb-3">{result.description}</p>
                      {result.punishment && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                          <p className="text-sm text-yellow-800">
                            <span className="font-semibold">Punishment:</span> {result.punishment}
                          </p>
                        </div>
                      )}
                    </div>
                    <div className="ml-4 flex space-x-2">
                      <button
                        onClick={() => handleActSelect(result)}
                        className="px-3 py-1 text-sm bg-primary-100 text-primary-700 rounded-md hover:bg-primary-200"
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Results */}
        {searchQuery && searchResults.length === 0 && !isLoading && (
          <div className="bg-white shadow rounded-lg p-12 text-center">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M12 12h.01M12 12h.01M12 12h.01M12 12h.01M12 12h.01M12 12h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
            <p className="text-gray-600">
              Try searching with different keywords or browse acts directly
            </p>
          </div>
        )}

        {/* Act Details Modal */}
        {selectedAct && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-bold text-gray-900">{selectedAct.title}</h3>
                <button
                  onClick={closeActDetails}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">Description</h4>
                  <p className="text-gray-600">{selectedAct.description}</p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">Act</h4>
                  <p className="text-gray-600">{selectedAct.act}</p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">Section</h4>
                  <p className="text-gray-600">{selectedAct.section}</p>
                </div>

                {selectedAct.punishment && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Punishment</h4>
                    <p className="text-gray-600">{selectedAct.punishment}</p>
                  </div>
                )}
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  onClick={closeActDetails}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default LegalSearchPage;