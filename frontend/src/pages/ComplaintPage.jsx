import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../hooks/useAuth';

function ComplaintPage() {
  const { t } = useTranslation();
  const { user, isPolice } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    complaint_type: '',
    respondent_name: '',
    respondent_address: '',
    incident_date: '',
    incident_location: '',
    relief_sought: '',
    supporting_documents: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.title) {
      newErrors.title = 'Complaint title is required';
    }

    if (!formData.description) {
      newErrors.description = 'Complaint description is required';
    }

    if (!formData.complaint_type) {
      newErrors.complaint_type = 'Complaint type is required';
    }

    if (!formData.incident_date) {
      newErrors.incident_date = 'Incident date is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // API call would go here
      console.log('Complaint Data:', formData);
      // Show success message
      setIsLoading(false);
    } catch (error) {
      console.error('Complaint creation error:', error);
      setIsLoading(false);
    }
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    setFormData(prev => ({
      ...prev,
      supporting_documents: [...prev.supporting_documents, ...files]
    }));
  };

  const removeDocument = (index) => {
    setFormData(prev => ({
      ...prev,
      supporting_documents: prev.supporting_documents.filter((_, i) => i !== index)
    }));
  };

  if (isPolice()) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Restricted</h1>
          <p className="text-gray-600">This page is only accessible to citizens.</p>
          <button
            onClick={() => window.history.back()}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Write Legal Complaint</h1>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Complaint Details */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Complaint Details</h2>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                      Complaint Title *
                    </label>
                    <input
                      type="text"
                      id="title"
                      name="title"
                      value={formData.title}
                      onChange={handleChange}
                      className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm ${
                        errors.title ? 'border-red-500' : ''
                      }`}
                      placeholder="Brief title of your complaint"
                    />
                    {errors.title && (
                      <p className="mt-1 text-sm text-red-600">{errors.title}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="complaint_type" className="block text-sm font-medium text-gray-700">
                      Complaint Type *
                    </label>
                    <select
                      id="complaint_type"
                      name="complaint_type"
                      value={formData.complaint_type}
                      onChange={handleChange}
                      className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm ${
                        errors.complaint_type ? 'border-red-500' : ''
                      }`}
                    >
                      <option value="">Select complaint type</option>
                      <option value="civil_dispute">Civil Dispute</option>
                      <option value="property_dispute">Property Dispute</option>
                      <option value="consumer_complaint">Consumer Complaint</option>
                      <option value="employment_dispute">Employment Dispute</option>
                      <option value="family_matter">Family Matter</option>
                      <option value="landlord_tenant">Landlord/Tenant Issue</option>
                      <option value="contract_dispute">Contract Dispute</option>
                      <option value="other">Other</option>
                    </select>
                    {errors.complaint_type && (
                      <p className="mt-1 text-sm text-red-600">{errors.complaint_type}</p>
                    )}
                  </div>
                </div>

                <div className="mt-4">
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                    Detailed Description *
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    rows={6}
                    value={formData.description}
                    onChange={handleChange}
                    className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm ${
                      errors.description ? 'border-red-500' : ''
                    }`}
                    placeholder="Provide detailed description of your complaint, including relevant facts and circumstances"
                  />
                  {errors.description && (
                    <p className="mt-1 text-sm text-red-600">{errors.description}</p>
                  )}
                </div>
              </div>

              {/* Respondent Information */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Respondent Information</h2>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="respondent_name" className="block text-sm font-medium text-gray-700">
                      Respondent Name
                    </label>
                    <input
                      type="text"
                      id="respondent_name"
                      name="respondent_name"
                      value={formData.respondent_name}
                      onChange={handleChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                      placeholder="Name of person or organization you're complaining against"
                    />
                  </div>

                  <div>
                    <label htmlFor="respondent_address" className="block text-sm font-medium text-gray-700">
                      Respondent Address
                    </label>
                    <input
                      type="text"
                      id="respondent_address"
                      name="respondent_address"
                      value={formData.respondent_address}
                      onChange={handleChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                      placeholder="Address of respondent"
                    />
                  </div>
                </div>
              </div>

              {/* Incident Details */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Incident Details</h2>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="incident_date" className="block text-sm font-medium text-gray-700">
                      Incident Date *
                    </label>
                    <input
                      type="date"
                      id="incident_date"
                      name="incident_date"
                      value={formData.incident_date}
                      onChange={handleChange}
                      className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm ${
                        errors.incident_date ? 'border-red-500' : ''
                      }`}
                    />
                    {errors.incident_date && (
                      <p className="mt-1 text-sm text-red-600">{errors.incident_date}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="incident_location" className="block text-sm font-medium text-gray-700">
                      Incident Location
                    </label>
                    <input
                      type="text"
                      id="incident_location"
                      name="incident_location"
                      value={formData.incident_location}
                      onChange={handleChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                      placeholder="Where the incident occurred"
                    />
                  </div>
                </div>
              </div>

              {/* Relief Sought */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Relief Sought</h2>

                <div>
                  <label htmlFor="relief_sought" className="block text-sm font-medium text-gray-700">
                    What relief are you seeking?
                  </label>
                  <textarea
                    id="relief_sought"
                    name="relief_sought"
                    rows={3}
                    value={formData.relief_sought}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    placeholder="Describe what remedy or compensation you are seeking"
                  />
                </div>
              </div>

              {/* Supporting Documents */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Supporting Documents</h2>

                <div className="mt-2">
                  <label htmlFor="file_upload" className="block text-sm font-medium text-gray-700">
                    Upload supporting documents
                  </label>
                  <input
                    type="file"
                    id="file_upload"
                    multiple
                    onChange={handleFileUpload}
                    className="mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Upload any relevant documents, receipts, contracts, photos, etc.
                  </p>
                </div>

                {formData.supporting_documents.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Uploaded Documents:</h4>
                    <ul className="space-y-2">
                      {formData.supporting_documents.map((doc, index) => (
                        <li key={index} className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded">
                          <span className="text-sm text-gray-700">{doc.name}</span>
                          <button
                            type="button"
                            onClick={() => removeDocument(index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            Remove
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* AI Assistance Note */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">
                      AI-Powered Legal Formatting
                    </h3>
                    <p className="mt-1 text-sm text-blue-700">
                      Your complaint will be automatically formatted according to legal standards. Our AI will help structure it professionally for better legal standing.
                    </p>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Save as Draft
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {isLoading ? 'Generating Complaint...' : 'Generate Complaint'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ComplaintPage;