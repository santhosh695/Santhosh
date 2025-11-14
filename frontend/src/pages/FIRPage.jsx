import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../hooks/useAuth';

function FIRPage() {
  const { t } = useTranslation();
  const { user, isPolice } = useAuth();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    complainant_name: '',
    complainant_phone: '',
    complainant_address: '',
    incident_date: '',
    incident_location: '',
    incident_type: '',
    sections_applied: '',
    evidence: []
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
      newErrors.title = 'FIR title is required';
    }

    if (!formData.description) {
      newErrors.description = 'Description is required';
    }

    if (!formData.complainant_name) {
      newErrors.complainant_name = 'Complainant name is required';
    }

    if (!formData.incident_date) {
      newErrors.incident_date = 'Incident date is required';
    }

    if (!formData.incident_location) {
      newErrors.incident_location = 'Incident location is required';
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
      console.log('FIR Data:', formData);
      // Show success message
      setIsLoading(false);
    } catch (error) {
      console.error('FIR creation error:', error);
      setIsLoading(false);
    }
  };

  if (!isPolice()) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Restricted</h1>
          <p className="text-gray-600">This page is only accessible to police officers.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Create First Information Report (FIR)</h1>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* FIR Details */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">FIR Details</h2>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                      FIR Title *
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
                      placeholder="Brief title of the incident"
                    />
                    {errors.title && (
                      <p className="mt-1 text-sm text-red-600">{errors.title}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="incident_type" className="block text-sm font-medium text-gray-700">
                      Incident Type
                    </label>
                    <select
                      id="incident_type"
                      name="incident_type"
                      value={formData.incident_type}
                      onChange={handleChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    >
                      <option value="">Select incident type</option>
                      <option value="theft">Theft</option>
                      <option value="assault">Assault</option>
                      <option value="fraud">Fraud</option>
                      <option value="harassment">Harassment</option>
                      <option value="property_dispute">Property Dispute</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div className="mt-4">
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                    Detailed Description *
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    rows={4}
                    value={formData.description}
                    onChange={handleChange}
                    className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm ${
                      errors.description ? 'border-red-500' : ''
                    }`}
                    placeholder="Provide detailed description of the incident"
                  />
                  {errors.description && (
                    <p className="mt-1 text-sm text-red-600">{errors.description}</p>
                  )}
                </div>
              </div>

              {/* Complainant Information */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Complainant Information</h2>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="complainant_name" className="block text-sm font-medium text-gray-700">
                      Complainant Name *
                    </label>
                    <input
                      type="text"
                      id="complainant_name"
                      name="complainant_name"
                      value={formData.complainant_name}
                      onChange={handleChange}
                      className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm ${
                        errors.complainant_name ? 'border-red-500' : ''
                      }`}
                    />
                    {errors.complainant_name && (
                      <p className="mt-1 text-sm text-red-600">{errors.complainant_name}</p>
                    )}
                  </div>

                  <div>
                    <label htmlFor="complainant_phone" className="block text-sm font-medium text-gray-700">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      id="complainant_phone"
                      name="complainant_phone"
                      value={formData.complainant_phone}
                      onChange={handleChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label htmlFor="complainant_address" className="block text-sm font-medium text-gray-700">
                    Address
                  </label>
                  <textarea
                    id="complainant_address"
                    name="complainant_address"
                    rows={2}
                    value={formData.complainant_address}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                </div>
              </div>

              {/* Incident Details */}
              <div className="border-b border-gray-200 pb-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">Incident Details</h2>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label htmlFor="incident_date" className="block text-sm font-medium text-gray-700">
                      Incident Date & Time *
                    </label>
                    <input
                      type="datetime-local"
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
                      Incident Location *
                    </label>
                    <input
                      type="text"
                      id="incident_location"
                      name="incident_location"
                      value={formData.incident_location}
                      onChange={handleChange}
                      className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm ${
                        errors.incident_location ? 'border-red-500' : ''
                      }`}
                    />
                    {errors.incident_location && (
                      <p className="mt-1 text-sm text-red-600">{errors.incident_location}</p>
                    )}
                  </div>
                </div>

                <div className="mt-4">
                  <label htmlFor="sections_applied" className="block text-sm font-medium text-gray-700">
                    IPC Sections Applied
                  </label>
                  <input
                    type="text"
                    id="sections_applied"
                    name="sections_applied"
                    value={formData.sections_applied}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                    placeholder="e.g., Section 420, 467, 468 IPC"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  {isLoading ? 'Creating FIR...' : 'Create FIR'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FIRPage;