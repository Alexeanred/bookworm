import { API_BASE_URL, handleResponse } from './index';
import { getToken } from './auth';
import { CartItem } from '../cart';

export interface OrderItemRequest {
  book_id: number;
  quantity: number;
}

export interface OrderResponse {
  success: boolean;
  order: {
    id: number;
    user_id: number;
    order_date: string;
    order_amount: number;
    items: {
      book_id: number;
      title: string;
      quantity: number;
      price: number;
      item_total: number;
    }[];
  };
}

/**
 * Create a new order
 */
export async function createOrder(items: CartItem[]): Promise<OrderResponse> {
  const token = getToken();
  if (!token) {
    throw new Error('Authentication required');
  }
  
  // Convert cart items to order items format
  const orderItems: OrderItemRequest[] = items.map(item => ({
    book_id: item.id,
    quantity: item.quantity
  }));
  
  const response = await fetch(`${API_BASE_URL}/orders/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(orderItems)
  });
  
  return handleResponse<OrderResponse>(response);
}

/**
 * Get user orders
 */
export async function getUserOrders() {
  const token = getToken();
  if (!token) {
    throw new Error('Authentication required');
  }
  
  const response = await fetch(`${API_BASE_URL}/orders/`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return handleResponse(response);
}
