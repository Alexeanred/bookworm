import { booksApi } from './api/books';
import { getToken } from './api/auth';

// Use the BookDetail interface from the books API
type BookDetail = Parameters<typeof booksApi.getBookDetail>[0] extends number
  ? Awaited<ReturnType<typeof booksApi.getBookDetail>>
  : never;

export interface CartItem {
  id: number;
  title: string;
  author: string;
  image: string;
  price: number;
  discountPrice: number | null;
  quantity: number;
}

const GUEST_CART_KEY = 'bookworm_guest_cart';
const USER_CART_PREFIX = 'bookworm_user_cart_';

/**
 * Get the appropriate cart storage key based on authentication status
 */
function getCartKey(): string {
  const token = getToken();
  if (token) {
    // Try to extract user ID from token (assuming JWT)
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if (payload.sub) {
        return `${USER_CART_PREFIX}${payload.sub}`;
      }
    } catch (e) {
      console.error('Error parsing token:', e);
    }
  }
  return GUEST_CART_KEY;
}

/**
 * Get cart items from localStorage
 */
export function getCartItems(): CartItem[] {
  const cartKey = getCartKey();
  const cartData = localStorage.getItem(cartKey);
  if (!cartData) return [];

  try {
    return JSON.parse(cartData);
  } catch (error) {
    console.error('Error parsing cart data:', error);
    return [];
  }
}

/**
 * Save cart items to localStorage
 */
export function saveCartItems(items: CartItem[]): void {
  const cartKey = getCartKey();
  localStorage.setItem(cartKey, JSON.stringify(items));
}

/**
 * Add item to cart
 * @returns The actual quantity that was added (may be less than requested due to the 8-item limit)
 */
export function addToCart(book: BookDetail, quantity: number): number {
  const cart = getCartItems();

  // Check if item already exists in cart
  const existingItemIndex = cart.findIndex(item => item.id === book.id);

  // Helper function to parse price
  const parsePrice = (price: string | number | undefined): number => {
    if (typeof price === 'number') return price;
    if (typeof price === 'string') {
      const cleanPrice = price.replace(/[^0-9.]/g, '');
      return parseFloat(cleanPrice) || 0;
    }
    return 0;
  };

  let actualQuantityAdded = quantity;

  if (existingItemIndex >= 0) {
    // Calculate how many items can be added before hitting the limit
    const currentQty = cart[existingItemIndex].quantity;
    const maxAddable = Math.max(0, 8 - currentQty);
    actualQuantityAdded = Math.min(quantity, maxAddable);

    // Update quantity if item exists
    const newQuantity = Math.min(currentQty + quantity, 8);
    cart[existingItemIndex].quantity = newQuantity;
  } else {
    // Add new item if it doesn't exist
    actualQuantityAdded = Math.min(quantity, 8);

    cart.push({
      id: book.id,
      title: book.title,
      author: book.author.name,
      image: book.cover ? `/covers/${book.cover}.jpg` : '/covers/default.jpg',
      price: parsePrice(book.original_price),
      discountPrice: book.discount_price ? parsePrice(book.discount_price) : null,
      quantity: actualQuantityAdded
    });
  }

  saveCartItems(cart);
  return actualQuantityAdded;
}

/**
 * Update item quantity in cart
 */
export function updateCartItemQuantity(bookId: number, quantity: number): void {
  const cart = getCartItems();

  if (quantity <= 0) {
    // Remove item if quantity is 0 or less
    removeFromCart(bookId);
    return;
  }

  // Find and update item
  const updatedCart = cart.map(item =>
    item.id === bookId
      ? { ...item, quantity: Math.min(quantity, 8) }
      : item
  );

  saveCartItems(updatedCart);
}

/**
 * Remove item from cart
 */
export function removeFromCart(bookId: number): void {
  const cart = getCartItems();
  const updatedCart = cart.filter(item => item.id !== bookId);
  saveCartItems(updatedCart);
}

/**
 * Clear cart
 */
export function clearCart(): void {
  const cartKey = getCartKey();
  localStorage.removeItem(cartKey);
}

/**
 * Get cart total price
 */
export function getCartTotal(): number {
  const cart = getCartItems();
  return cart.reduce((sum, item) =>
    sum + (item.discountPrice ?? item.price) * item.quantity, 0
  );
}

/**
 * Get total number of items in cart
 */
export function getCartItemCount(): number {
  const cart = getCartItems();
  return cart.reduce((sum, item) => sum + item.quantity, 0);
}

/**
 * Merge guest cart with user cart when logging in
 * This would be called after login
 */
export function mergeGuestCart(): number {
  // Get guest cart
  const guestCartData = localStorage.getItem(GUEST_CART_KEY);
  if (!guestCartData) return 0;

  try {
    // Parse guest cart
    const guestCart = JSON.parse(guestCartData);
    if (!guestCart.length) return 0;

    // Get current user cart
    const userCart = getCartItems();

    // Track how many items were added
    let addedItems = 0;

    // Merge items
    for (const guestItem of guestCart) {
      const existingItemIndex = userCart.findIndex(item => item.id === guestItem.id);

      if (existingItemIndex >= 0) {
        // Update quantity if item exists
        const currentQty = userCart[existingItemIndex].quantity;
        const newQuantity = Math.min(currentQty + guestItem.quantity, 8);
        const addedQty = newQuantity - currentQty;

        userCart[existingItemIndex].quantity = newQuantity;
        addedItems += addedQty;
      } else {
        // Add new item if it doesn't exist
        userCart.push(guestItem);
        addedItems += guestItem.quantity;
      }
    }

    // Save merged cart
    saveCartItems(userCart);

    // Clear guest cart
    localStorage.removeItem(GUEST_CART_KEY);

    return addedItems;
  } catch (error) {
    console.error('Error merging cart data:', error);
    return 0;
  }
}

