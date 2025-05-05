export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    // Xử lý các mã lỗi cụ thể
    if (response.status === 401) {
      throw new Error('Wrong email or password');
    } else if (response.status === 403) {
      throw new Error('You do not have permission to access this resource');
    } else if (response.status === 404) {
      throw new Error('The requested resource was not found');
    } else if (response.status === 500) {
      throw new Error('Server error. Please try again later');
    } else {
      throw new Error(`Request failed with status: ${response.status}`);
    }
  }
  return response.json();
}
