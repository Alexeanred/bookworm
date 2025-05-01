import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import SignInModal from "../components/SignInModal";
import { login } from "../services/api/auth";
import { mergeGuestCart } from "../services/cart";

interface SignInPageProps {
  onLoginSuccess?: () => void;
}

const SignInPage: React.FC<SignInPageProps> = ({ onLoginSuccess }) => {
  const [open, setOpen] = useState(true);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSignIn = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      // Call login API
      await login(email, password);

      // Merge guest cart with user cart
      // Note: We don't need to update cart count here because updateAuthState will do it
      mergeGuestCart();

      // Update authentication state in parent component
      if (onLoginSuccess) {
        onLoginSuccess();
      }

      setOpen(false);
      setError("");
      // Redirect to home after successful login
      setTimeout(() => navigate("/"), 500);
    } catch (error: any) {
      console.error('Login error:', error);
      setError(error.message || 'Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Div chiếm không gian để đẩy footer xuống dưới */}
      <div className="min-h-[calc(100vh-200px)]"></div>

      {/* Modal đăng nhập */}
      <SignInModal
        open={open}
        onClose={() => navigate("/")}
        onSignIn={handleSignIn}
        error={error}
        isLoading={isLoading}
      />
    </>
  );
};

export default SignInPage;
