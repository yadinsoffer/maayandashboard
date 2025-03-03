'use client';

import { useState } from 'react';
import { submitKey } from '../utils/ec2-api';

interface KeyInputFormProps {
  onSuccess: () => void;
  errorMessage?: string;
}

export default function KeyInputForm({ onSuccess, errorMessage }: KeyInputFormProps) {
  const [key, setKey] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(errorMessage || null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!key.trim()) {
      setError('Please enter a valid key');
      return;
    }
    
    setIsSubmitting(true);
    setError(null);
    
    console.log('Submitting key...');
    
    try {
      const result = await submitKey(key);
      console.log('Key submission result:', result);
      
      if (result.success) {
        console.log('Key validation successful');
        onSuccess();
      } else {
        console.error('Key validation failed:', result.error);
        setError(result.message || 'Failed to validate key. Please try again.');
      }
    } catch (err) {
      console.error('Error submitting key:', err);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Dashboard Access Required</h1>
        
        <p className="mb-6 text-gray-600 text-center">
          The dashboard update process failed. Please enter your access key to continue.
        </p>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4" role="alert">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="key" className="block text-sm font-medium text-gray-700 mb-1">
              Access Key
            </label>
            <input
              type="text"
              id="key"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Enter your access key"
              disabled={isSubmitting}
            />
          </div>
          
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {isSubmitting ? 'Validating...' : 'Submit Key'}
          </button>
        </form>
      </div>
    </div>
  );
} 