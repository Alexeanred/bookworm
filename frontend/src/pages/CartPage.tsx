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
      <div className="container mx-auto px-4 sm:px-6 py-6 sm:py-8 flex-1">
        <h2 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">Your cart: {totalItems} items</h2>

        {/* Responsive layout - stack on mobile, side-by-side on larger screens */}
        <div className="flex flex-col lg:flex-row gap-4 lg:gap-8">
          {/* Cart Items - Responsive container */}
          <div className="flex-1 bg-white border rounded">
            {/* Desktop view - Table layout */}
            <div className="hidden md:block">
              <table className="w-full text-left">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="p-4 w-3/5">Product</th>
                    <th className="pl-2 w-1/6">Price</th>
                    <th className="text-center w-1/6">Quantity</th>
                    <th className="text-right pr-4 w-1/12">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {cart.map(item => (
                    <tr key={item.id} className="border-b hover:bg-gray-50">
                      <td className="p-4 flex items-center gap-4 cursor-pointer" onClick={() => window.open(`/product/${item.id}`, '_blank')}>
                        <img
                          src={item.image}
                          alt={item.title}
                          onError={(e) => {
                            e.currentTarget.src = '/covers/default.jpg';
                          }}
                          className="w-16 sm:w-20 h-24 sm:h-28 object-cover bg-gray-200 rounded"
                        />
                        <div className="overflow-hidden">
                          <div className="font-semibold text-base sm:text-lg truncate">{item.title}</div>
                          <div className="text-gray-600 text-xs sm:text-sm">{item.author}</div>
                        </div>
                      </td>
                      <td className="font-semibold">
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
                      <td className="text-center">
                        <div className="flex items-center justify-center gap-2 mx-auto" style={{ width: '90px' }}>
                          <button className="border px-2 rounded" onClick={() => handleQtyChange(item.id, Math.max(0, item.quantity - 1))} disabled={item.quantity <= 0}>-</button>
                          <span className="px-3 min-w-[20px] text-center">{item.quantity}</span>
                          <button className="border px-2 rounded" onClick={() => handleQtyChange(item.id, Math.min(8, item.quantity + 1))} disabled={item.quantity >= 8}>+</button>
                        </div>
                      </td>
                      <td className="font-semibold">
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

            {/* Mobile view - Card layout */}
            <div className="md:hidden">
              {cart.length === 0 ? (
                <div className="text-center py-8 text-gray-500">Your cart is empty.</div>
              ) : (
                <div className="divide-y">
                  {cart.map(item => (
                    <div key={item.id} className="p-4 hover:bg-gray-50">
                      {/* Product info */}
                      <div className="flex gap-3 mb-3 cursor-pointer" onClick={() => window.open(`/product/${item.id}`, '_blank')}>
                        <img
                          src={item.image}
                          alt={item.title}
                          onError={(e) => {
                            e.currentTarget.src = '/covers/default.jpg';
                          }}
                          className="w-16 h-24 object-cover bg-gray-200 rounded flex-shrink-0"
                        />
                        <div className="overflow-hidden">
                          <div className="font-semibold text-base truncate">{item.title}</div>
                          <div className="text-gray-600 text-xs">{item.author}</div>

                          {/* Price - Mobile view */}
                          <div className="mt-1 font-semibold">
                            {item.discountPrice ? (
                              <>
                                <span className="text-black">${item.discountPrice.toFixed(2)}</span>
                                <span className="ml-1 text-xs text-gray-400 line-through">${item.price.toFixed(2)}</span>
                              </>
                            ) : (
                              <span>${item.price.toFixed(2)}</span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Quantity and total - Mobile view */}
                      <div className="flex justify-between items-center mt-2">
                        <div className="flex items-center gap-2">
                          <button className="border px-2 rounded" onClick={() => handleQtyChange(item.id, Math.max(0, item.quantity - 1))} disabled={item.quantity <= 0}>-</button>
                          <span className="px-3 min-w-[20px] text-center">{item.quantity}</span>
                          <button className="border px-2 rounded" onClick={() => handleQtyChange(item.id, Math.min(8, item.quantity + 1))} disabled={item.quantity >= 8}>+</button>
                        </div>
                        <div className="font-semibold">
                          Total: ${((item.discountPrice ?? item.price) * item.quantity).toFixed(2)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Cart Totals - Responsive width */}
          <div className="w-full lg:w-80 xl:w-96 bg-white border rounded h-fit">
            <div className="p-4 sm:p-6 pb-2 sm:pb-4">
              <div className="font-semibold text-lg text-center">Cart Totals</div>
            </div>
            <hr className="border-t border-gray-300 mx-0 my-0" />
            <div className="p-4 sm:p-6 pt-2 sm:pt-4">
              <div className="text-2xl sm:text-3xl font-bold mb-4 sm:mb-6 text-center">${total.toFixed(2)}</div>
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
