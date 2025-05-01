import { BookOpen } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import OnSaleSection from './components/OnSaleSection';
import FeaturedBooks from './components/FeaturedBooks';
import ShopPage from './pages/ShopPage';
import ProductPage from './pages/ProductPage';
import { createContext, useState, useContext, useEffect } from 'react';
import CartPage from './pages/CartPage';
import AboutPage from './pages/AboutPage';
import SignInPage from './pages/SignInPage';
import UserDropdown from './components/UserDropdown';
import { getCartItemCount, clearCart } from './services/cart';
import { isAuthenticated, getUserFullName } from './services/api/auth';

// Cart context
export const CartContext = createContext<{cartCount: number, addToCart: (qty: number) => void}>({ cartCount: 0, addToCart: () => {} });

function App() {
  const [cartCount, setCartCount] = useState(0);
  const [userName, setUserName] = useState('');
  const [isAuth, setIsAuth] = useState(false);

  // Initialize cart count from localStorage and check authentication
  useEffect(() => {
    // Get the actual count from cart items
    const actualCount = getCartItemCount();
    setCartCount(actualCount);

    // Check authentication status and get user info
    updateAuthState();
  }, []);

  // Function to update authentication state
  const updateAuthState = () => {
    const authStatus = isAuthenticated();
    setIsAuth(authStatus);
    if (authStatus) {
      setUserName(getUserFullName());

      // Update cart count in navbar to reflect the user's cart count
      const userCartItemsCount = getCartItemCount();
      setCartCount(userCartItemsCount);
    } else {
      setUserName('');
    }
  };

  // Handle user logout
  const handleLogout = () => {
    // Clear user's cart when user logs out (this will only clear the user's cart, not the guest cart)
    clearCart();

    // Update authentication state
    updateAuthState();

    // After updating auth state, we need to get the guest cart count
    // This is important because getCartItemCount() will now return the guest cart count
    const guestCartItemsCount = getCartItemCount();

    // Update cart count in navbar to reflect the guest cart count
    setCartCount(guestCartItemsCount);
  };

  // Function to add items to cart
  const addToCart = (qty: number) => {
    setCartCount(c => c + qty);
    // Note: The actual cart item is added in the ProductPage component
  };

  return (
    <CartContext.Provider value={{ cartCount, addToCart }}>
      <Router>
        <div className="min-h-screen bg-white">
          {/* Header */}
          <header className="bg-white border-b">
            <div className="container mx-auto px-4">
              <div className="flex items-center justify-between h-16">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-gray-200 flex items-center justify-center">
                    <BookOpen className="w-8 h-8 text-gray-600" />
                  </div>
                  <span className="text-xl font-bold">BOOKWORM</span>
                </div>
                <div className="flex items-center space-x-8">
                  <NavLink to="/" end className={({ isActive }) => isActive ? "text-blue-700 underline font-semibold" : "text-gray-700 hover:text-blue-600"}>Home</NavLink>
                  <NavLink to="/shop" className={({ isActive }) => isActive ? "text-blue-700 underline font-semibold" : "text-gray-700 hover:text-blue-600"}>Shop</NavLink>
                  <NavLink to="/about" className={({ isActive }) => isActive ? "text-blue-700 underline font-semibold" : "text-gray-700 hover:text-blue-600"}>About</NavLink>
                  <NavLink to="/cart" className={({ isActive }) => isActive ? "text-blue-700 underline font-semibold" : "text-gray-700 hover:text-blue-600"}>Cart ({cartCount})</NavLink>
                  {isAuth ? (
                    <UserDropdown fullName={userName} onLogout={handleLogout} />
                  ) : (
                    <NavLink to="/signin" className={({ isActive }) => isActive ? "text-blue-700 underline font-semibold" : "text-gray-700 hover:text-blue-600"}>Sign In</NavLink>
                  )}
                </div>
              </div>
            </div>
          </header>
          <main className="container mx-auto px-4">
            <Routes>
              <Route path="/shop" element={<ShopPage />} />
              <Route path="/cart" element={<CartPage onLoginSuccess={updateAuthState} />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/signin" element={<SignInPage onLoginSuccess={updateAuthState} />} />
              <Route path="/product/:id" element={<ProductPageWrapper />} />
              <Route
                path="/"
                element={
                  <main className="container mx-auto px-4 py-8">
                    <OnSaleSection />
                    <FeaturedBooks />
                  </main>
                }
              />
            </Routes>
          </main>
          {/* Footer */}
          <footer className="bg-gray-100 py-8 mt-12">
            <div className="container mx-auto px-4">
              <div className="flex items-center">
                <div className="w-16 h-16 bg-gray-200 flex items-center justify-center">
                  <BookOpen className="w-8 h-8 text-gray-600" />
                </div>
                <div className="ml-4">
                  <div className="font-bold">BOOKWORM</div>
                  <div className="text-gray-600">Address: 49C Lê Quang Kim P8 Q8 HCM</div>
                  <div className="text-gray-600">Phone: 0777957957</div>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </CartContext.Provider>
  );
}

// Wrapper để truyền context vào ProductPage
const ProductPageWrapper = () => {
  const { cartCount, addToCart } = useContext(CartContext);
  return <ProductPage cartCount={cartCount} addToCart={addToCart} />;
};

export default App;
