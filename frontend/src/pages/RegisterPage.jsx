import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = '/api';

const RegisterPage = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    interests: []
  });
  const [interests, setInterests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchInterests();
  }, []);

  const fetchInterests = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/auth/interests`);
      setInterests(response.data);
    } catch (error) {
      console.error('Error fetching interests:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleInterestToggle = (interestId) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interestId)
        ? prev.interests.filter(id => id !== interestId)
        : [...prev.interests, interestId]
    }));
  };

  const validateStep1 = () => {
    if (!formData.username.trim()) {
      setError('Username is required');
      return false;
    }
    if (!formData.email.trim()) {
      setError('Email is required');
      return false;
    }
    if (!formData.password) {
      setError('Password is required');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }
    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return false;
    }
    return true;
  };

  const handleNextStep = () => {
    setError('');
    if (step === 1 && validateStep1()) {
      setStep(2);
    }
  };

  const handlePreviousStep = () => {
    setError('');
    if (step === 2) {
      setStep(1);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (formData.interests.length === 0) {
      setError('Please select at least one interest');
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        interests: formData.interests
      });

      setSuccess('Registration successful! Redirecting...');
      
      // Store user data in localStorage
      localStorage.setItem('user', JSON.stringify(response.data));
      
      // Redirect to home page after 2 seconds
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);

    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const groupInterestsByCategory = () => {
    const grouped = {};
    interests.forEach(interest => {
      if (!grouped[interest.category]) {
        grouped[interest.category] = {};
      }
      if (!grouped[interest.category][interest.subcategory]) {
        grouped[interest.category][interest.subcategory] = [];
      }
      grouped[interest.category][interest.subcategory].push(interest);
    });
    return grouped;
  };

  const groupedInterests = groupInterestsByCategory();

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-8">Join Raddit</h1>
        
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${step >= 1 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-400'}`}>
                1
              </div>
              <span className="ml-2 font-medium">Account Details</span>
            </div>
            <div className={`flex-1 h-1 mx-4 ${step >= 2 ? 'bg-blue-600' : 'bg-gray-300'}`}></div>
            <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${step >= 2 ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-400'}`}>
                2
              </div>
              <span className="ml-2 font-medium">Choose Interests</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
            {success}
          </div>
        )}

        <form onSubmit={step === 1 ? handleNextStep : handleSubmit}>
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Choose a username"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Create a password"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password
                </label>
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Confirm your password"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                Next: Choose Interests
              </button>
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Select Your Interests</h2>
              <p className="text-gray-600 mb-6">
                Choose the topics you're interested in. We'll use this to personalize your experience.
              </p>

              <div className="mb-4">
                <span className="text-sm text-gray-600">
                  Selected: {formData.interests.length} interests
                </span>
              </div>

              <div className="space-y-6 max-h-96 overflow-y-auto">
                {Object.entries(groupedInterests).map(([category, subcategories]) => (
                  <div key={category} className="border rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">{category}</h3>
                    {Object.entries(subcategories).map(([subcategory, interests]) => (
                      <div key={subcategory} className="mb-4">
                        <h4 className="text-md font-medium text-gray-700 mb-2">{subcategory}</h4>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {interests.map(interest => (
                            <label
                              key={interest.id}
                              className="flex items-center space-x-2 p-2 rounded border hover:bg-gray-50 cursor-pointer"
                            >
                              <input
                                type="checkbox"
                                checked={formData.interests.includes(interest.id)}
                                onChange={() => handleInterestToggle(interest.id)}
                                className="rounded text-blue-600 focus:ring-blue-500"
                              />
                              <span className="text-sm text-gray-700">{interest.name}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              <div className="mt-6 flex space-x-4">
                <button
                  type="button"
                  onClick={handlePreviousStep}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={loading || formData.interests.length === 0}
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {loading ? 'Creating Account...' : 'Complete Registration'}
                </button>
              </div>
            </div>
          )}
        </form>

        <p className="mt-6 text-center text-sm text-gray-600">
          Already have an account?{' '}
          <a href="/login" className="text-blue-600 hover:text-blue-800">
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
};

export default RegisterPage;