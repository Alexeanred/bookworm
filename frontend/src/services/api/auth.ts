import { API_BASE_URL, handleResponse } from './index';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  admin: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Store token in localStorage
const TOKEN_KEY = 'bookworm_token';
const USER_KEY = 'bookworm_user';

/**
 * Login user with email and password
 */
export async function login(email: string, password: string): Promise<AuthResponse> {
  const formData = new FormData();
  formData.append('username', email); // OAuth2 uses 'username' field
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    body: formData,
    credentials: 'include', // Important for cookies
  });

  const data = await handleResponse<AuthResponse>(response);
  
  // Store token and user data
  localStorage.setItem(TOKEN_KEY, data.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(data.user));
  
  return data;
}

/**
 * Logout user
 */
export async function logout(): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    });
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Clear local storage regardless of API success
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

/**
 * Get current user information
 */
export async function getCurrentUser(): Promise<User | null> {
  // First check if we have user in localStorage
  const storedUser = localStorage.getItem(USER_KEY);
  if (storedUser) {
    return JSON.parse(storedUser);
  }
  
  // If not, try to get from API
  const token = getToken();
  if (!token) return null;
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      credentials: 'include'
    });
    
    const user = await handleResponse<User>(response);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    return user;
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
  }
}

/**
 * Get stored token
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

/**
 * Get user's full name
 */
export function getUserFullName(): string {
  const storedUser = localStorage.getItem(USER_KEY);
  if (!storedUser) return '';
  
  const user = JSON.parse(storedUser);
  return `${user.first_name} ${user.last_name}`;
}
