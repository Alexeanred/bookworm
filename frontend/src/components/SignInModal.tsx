import React, { useState } from "react";

interface SignInModalProps {
  open: boolean;
  onClose: () => void;
  onSignIn: (email: string, password: string) => void;
  error?: string;
  isLoading?: boolean;
}

const SignInModal: React.FC<SignInModalProps> = ({ open, onClose, onSignIn, error, isLoading = false }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [touched, setTouched] = useState(false);

  if (!open) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (email && password) {
      onSignIn(email, password);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded shadow-lg w-full max-w-sm p-8 relative">
        <button className="absolute top-2 right-2 text-gray-400 hover:text-black" onClick={onClose}>&times;</button>
        <h2 className="text-xl font-bold mb-6 text-center">Sign In</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block mb-1 font-semibold">Email</label>
            <input
              type="email"
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoFocus
            />
            {touched && !email && <div className="text-red-500 text-sm mt-1">Email is required</div>}
          </div>
          <div className="mb-4">
            <label className="block mb-1 font-semibold">Password</label>
            <input
              type="password"
              className="w-full border rounded px-3 py-2 focus:outline-none focus:ring"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
            {touched && !password && <div className="text-red-500 text-sm mt-1">Password is required</div>}
          </div>
          {error && <div className="text-red-600 text-sm mb-3">{error}</div>}
          <button
            type="submit"
            className={`w-full py-2 rounded font-semibold transition ${
              isLoading
                ? "bg-gray-500 text-white cursor-not-allowed"
                : "bg-black text-white hover:bg-gray-800"
            }`}
            disabled={isLoading}
          >
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignInModal;
