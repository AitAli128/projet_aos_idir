import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const navigate = useNavigate();
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <nav className="bg-blue-800 text-white p-4 shadow-lg">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold">MarketPharm</Link>
        <div className="space-x-4">
          <Link to="/" className="hover:text-blue-200">Catalog</Link>
          <button onClick={handleLogout} className="bg-red-500 px-3 py-1 rounded hover:bg-red-600 transition-colors">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
