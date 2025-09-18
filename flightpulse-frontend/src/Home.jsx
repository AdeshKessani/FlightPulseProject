import React from 'react';
import FlightChecker from './FlightChecker';

function Home() {
  return (
    <div style={{ 
      padding: '40px', 
      textAlign: 'center',
      marginTop: '60px' // Add margin to account for the fixed navbar
    }}>
      <h1 style={{ color: '#2e86de', marginBottom: '30px' }}>Flight Status Checker</h1>
      <FlightChecker />
    </div>
  );
}

export default Home;
