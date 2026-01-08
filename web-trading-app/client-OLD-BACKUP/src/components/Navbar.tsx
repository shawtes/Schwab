import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar: React.FC = () => {
  const location = useLocation();

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        📈 Trading Platform
      </Link>
      <ul className="navbar-links">
        <li>
          <Link 
            to="/" 
            className={location.pathname === '/' ? 'active' : ''}
          >
            Dashboard
          </Link>
        </li>
        <li>
          <Link 
            to="/screener" 
            className={location.pathname === '/screener' ? 'active' : ''}
          >
            Stock Screener
          </Link>
        </li>
        <li>
          <Link 
            to="/chart" 
            className={location.pathname.startsWith('/chart') ? 'active' : ''}
          >
            Live Charts
          </Link>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;


