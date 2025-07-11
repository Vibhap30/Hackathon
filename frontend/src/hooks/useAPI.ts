import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface UseAPIReturn {
  get: <T>(url: string) => Promise<T>;
  post: <T>(url: string, data?: any) => Promise<T>;
  put: <T>(url: string, data?: any) => Promise<T>;
  delete: <T>(url: string) => Promise<T>;
  loading: boolean;
  error: string | null;
}

export const useAPI = (): UseAPIReturn => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuth();

  const apiCall = async <T>(
    url: string, 
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    data?: any
  ): Promise<T> => {
    setLoading(true);
    setError(null);

    try {
      const baseUrl = 'http://localhost:8000'; // import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const fullUrl = `${baseUrl}${url.startsWith('/') ? url : `/${url}`}`;
      
      const config: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` })
        },
        ...(data && method !== 'GET' && { body: JSON.stringify(data) })
      };

      const response = await fetch(fullUrl, config);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const get = <T>(url: string): Promise<T> => apiCall<T>(url, 'GET');
  const post = <T>(url: string, data?: any): Promise<T> => apiCall<T>(url, 'POST', data);
  const put = <T>(url: string, data?: any): Promise<T> => apiCall<T>(url, 'PUT', data);
  const delete_ = <T>(url: string): Promise<T> => apiCall<T>(url, 'DELETE');

  return {
    get,
    post,
    put,
    delete: delete_,
    loading,
    error
  };
};
