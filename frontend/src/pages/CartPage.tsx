import React, { useState, useEffect, useContext } from "react";
import SignInModal from "../components/SignInModal";
import {
  getCartItems,
  updateCartItemQuantity,
  removeFromCart,
  clearCart,
  CartItem,
  getCartItemCount
} from "../services/cart";
import { login, isAuthenticated } from "../services/api/auth";
import { createOrder } from "../services/api/orders";
import { CartContext } from "../App";
import { mergeGuestCart } from "../services/cart";

interface CartPageProps {
  onLoginSuccess?: () => void;
}

const CartPage: React.FC<CartPageProps> = ({ onLoginSuccess }) => {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showSignIn, setShowSignIn] = useState(false);
  const [isAuth, setIsAuth] = useState(false);
  const [orderMsg, setOrderMsg] = useState<string|null>(null);
  const [orderSuccess, setOrderSuccess] = useState(false);
  const [signInError, setSignInError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Get the addToCart function from context to update cart count in navbar
  const { addToCart } = useContext(CartContext);

  // Load cart items from localStorage on component mount and ensure navbar count is correct
  useEffect(() => {
    const items = getCartItems();
    setCart(items);
    setIsAuth(isAuthenticated());

    // Always synchronize the navbar count with the actual cart items
    // This ensures the count is correct regardless of how items were added
    const totalItems = items.reduce((sum, item) => sum + item.quantity, 0);

    // Reset the cart count in the navbar to match the actual total
    addToCart(-getCartItemCount()); // Reset to 0
    addToCart(totalItems);          // Set to correct total
  }, [addToCart]);

  // Update localStorage when cart changes
  useEffect(() => {
    // We don't need to save here as our cart service functions handle saving
  }, [cart]);

  const handleQtyChange = (id: number, qty: number) => {
    const currentCart = getCartItems();
    const item = currentCart.find(item => item.id === id);
    const oldQty = item ? item.quantity : 0;

    if (qty === 0) {
      removeFromCart(id);
    } else {
      updateCartItemQuantity(id, qty);
    }

    // Update local state
    const updatedCart = getCartItems();
    setCart(updatedCart);

    // Update cart count in navbar
    const qtyDifference = qty - oldQty;
    if (qtyDifference !== 0) {
      addToCart(qtyDifference);
    }
  };

  const total = cart.reduce((sum, item) => sum + (item.discountPrice ?? item.price) * item.quantity, 0);
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

  const handlePlaceOrder = async () => {
    if (!isAuth) {
      setShowSignIn(true);
      return;
    }

    try {
      setIsLoading(true);
      // Call API to create order
      await createOrder(cart);

      // Handle successful order
      setOrderSuccess(true);
      setOrderMsg("Order placed successfully! Redirecting to home...");

      // Get the total number of items before clearing
      const itemsToRemove = cart.reduce((sum, item) => sum + item.quantity, 0);

      // Clear cart after successful order
      clearCart();
      setCart([]);

      // Update cart count in navbar (subtract all items)
      addToCart(-itemsToRemove);

      // Redirect to home page after delay
      setTimeout(() => {
        setOrderMsg(null);
        window.location.href = "/";
      }, 10000); // 10 seconds as per requirement
    } catch (error: any) {
      // Handle error
      console.error('Order creation error:', error);

      // Check if it's an availability error
      if (error.message && error.message.includes('not available')) {
        // Extract book ID from error message if possible
        const bookId = extractBookIdFromError(error.message);
        if (bookId) {
          const unavailableItem = cart.find(item => item.id === bookId);
          if (unavailableItem) {
            setOrderMsg(`Item '${unavailableItem.title}' is not available and was removed from your cart.`);
            const qtyToRemove = unavailableItem.quantity;
            removeFromCart(bookId);
            setCart(getCartItems());
            // Update cart count in navbar
            addToCart(-qtyToRemove);
          } else {
            setOrderMsg(`Some items are not available and were removed from your cart.`);
          }
        } else {
          setOrderMsg(`Some items are not available and were removed from your cart.`);
        }
      } else {
        setOrderMsg(`Error creating order: ${error.message || 'Unknown error'}`);
      }
      setOrderSuccess(false);
      setTimeout(() => setOrderMsg(null), 4000);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to extract book ID from error message
  const extractBookIdFromError = (message: string): number | null => {
    // This is a placeholder - implement based on actual error format
    const match = message.match(/book_id: (\d+)/);
    return match ? parseInt(match[1]) : null;
  };

  return (
    <div className="min-h-screen flex flex-col bg-white">
      <div className="container mx-auto px-6 py-8 flex-1">
        <h2 className="text-2xl font-bold mb-6">Your cart: {totalItems} items</h2>
        <div className="flex gap-8">
          {/* Cart Items */}
          <div className="flex-1 bg-white border rounded">
            <table className="w-full text-left">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="p-4" style={{ width: '60%' }}>Product</th>
                  <th style={{ width: '15%' }} className="pl-2">Price</th>
                  <th style={{ width: '15%' }} className="text-center">Quantity</th>
                  <th style={{ width: '10%' }} className="text-right pr-4">Total</th>
                </tr>
              </thead>
              <tbody>
                {cart.map(item => (
                  <tr key={item.id} className="border-b hover:bg-gray-50">
                    <td className="p-4 flex items-center gap-4 cursor-pointer" style={{ width: '60%' }} onClick={() => window.open(`/product/${item.id}`, '_blank')}>
                      <img
                        src={item.image}
                        alt={item.title}
                        onError={(e) => {
                          // Khi ảnh lỗi, thay thế bằng ảnh mặc định
                          e.currentTarget.src = '/covers/default.jpg';
                        }}
                        className="w-20 h-28 object-cover bg-gray-200 rounded"
                      />
                      <div className="overflow-hidden">
                        <div className="font-semibold text-lg truncate">{item.title}</div>
                        <div className="text-gray-600 text-sm">{item.author}</div>
                      </div>
                    </td>
                    <td className="font-semibold" style={{ width: '15%' }}>
                      <div className="text-left pl-2 whitespace-nowrap">
                        {item.discountPrice ? (
                          <>
                            <span className="text-black">${item.discountPrice.toFixed(2)}</span>
                            <span className="block text-xs text-gray-400 line-through">${item.price.toFixed(2)}</span>
                          </>
                        ) : (
                          <span>${item.price.toFixed(2)}</span>
                        )}
                      </div>
                    </td>
                    <td style={{ width: '15%' }} className="text-center">
                      <div className="flex items-center justify-center gap-2 mx-auto" style={{ width: '90px' }}>
                        <button className="border px-2 rounded" onClick={() => handleQtyChange(item.id, Math.max(0, item.quantity - 1))} disabled={item.quantity <= 0}>-</button>
                        <span className="px-3 min-w-[20px] text-center">{item.quantity}</span>
                        <button className="border px-2 rounded" onClick={() => handleQtyChange(item.id, Math.min(8, item.quantity + 1))} disabled={item.quantity >= 8}>+</button>
                      </div>
                    </td>
                    <td className="font-semibold" style={{ width: '10%' }}>
                      <div className="text-right pr-4 whitespace-nowrap">
                        ${((item.discountPrice ?? item.price) * item.quantity).toFixed(2)}
                      </div>
                    </td>
                  </tr>
                ))}
                {cart.length === 0 && (
                  <tr>
                    <td colSpan={4} className="text-center py-8 text-gray-500">Your cart is empty.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          {/* Cart Totals */}
          <div className="w-96 bg-white border rounded h-fit">
            <div className="p-6 pb-4">
              <div className="font-semibold text-lg text-center">Cart Totals</div>
            </div>
            <hr className="border-t border-gray-300 mx-0 my-0" />
            <div className="p-6 pt-4">
              <div className="text-3xl font-bold mb-6 text-center">${total.toFixed(2)}</div>
              <button
                className={`w-full font-semibold py-2 rounded mb-2 transition ${
                  isLoading
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-gray-200 text-black hover:bg-gray-300"
                }`}
                onClick={handlePlaceOrder}
                disabled={cart.length === 0 || isLoading}
              >
                {isLoading ? "Processing..." : "Place order"}
              </button>
              {orderMsg && (
                <div className={`mt-2 text-center ${orderSuccess ? "text-green-600" : "text-red-600"}`}>
                  {orderMsg}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      {/* Sign In Popup */}
      <SignInModal
        open={showSignIn}
        onClose={() => setShowSignIn(false)}
        onSignIn={async (email, password) => {
          try {
            setIsLoading(true);
            // Call login API
            await login(email, password);

            // Merge guest cart with user cart
            const addedItems = mergeGuestCart();

            // Update cart count in navbar if items were added
            if (addedItems > 0) {
              addToCart(addedItems);
            }

            // Update authentication state
            setIsAuth(true);
            setShowSignIn(false);
            setSignInError("");

            // Update auth state in parent component
            if (onLoginSuccess) {
              onLoginSuccess();
            }

            // Show success message
            setOrderMsg("Sign in successful. You can now place your order.");
            setOrderSuccess(true);
            setTimeout(() => setOrderMsg(null), 3000);

            // Don't automatically place the order - let the user click the button again
          } catch (error: any) {
            console.error('Login error:', error);
            setSignInError(error.message || 'Invalid email or password');
          } finally {
            setIsLoading(false);
          }
        }}
        error={signInError}
        isLoading={isLoading}
      />
    </div>
  );
};

export default CartPage;
