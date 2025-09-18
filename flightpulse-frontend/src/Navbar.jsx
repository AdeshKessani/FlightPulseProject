import React from 'react';
import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      padding: '15px',
      background: '#2e86de',
      color: 'white',
      boxSizing: 'border-box',
      zIndex: 1000
    }}>
      <Link to="/" style={{ color: 'white', marginRight: '30px', textDecoration: 'none', fontWeight: 'bold' }}>
        Flight Status Checker
      </Link>
      <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold' }}>
        Operational Dashboard
      </Link>
    </nav>
  );
}

export default Navbar;
