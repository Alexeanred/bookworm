import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../services/api/auth';

interface UserDropdownProps {
  fullName: string;
  onLogout: () => void;
}

const UserDropdown: React.FC<UserDropdownProps> = ({ fullName, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSignOut = async () => {
    try {
      await logout();
      onLogout();
      navigate('/');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        className="flex items-center px-3 py-1 bg-gray-100 rounded hover:bg-gray-200 min-w-[100px] justify-between"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="font-medium">{fullName}</span>
        <ChevronDown size={14} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1 min-w-[100px] bg-white shadow-lg z-10 p-2">
          <button
            className="w-full text-center py-2 border border-gray-300 rounded text-sm hover:bg-gray-100"
            onClick={handleSignOut}
          >
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
};

export default UserDropdown;
