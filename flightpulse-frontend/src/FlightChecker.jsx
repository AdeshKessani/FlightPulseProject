import React, { useState } from 'react';

function FlightChecker() {
  const [flightNumber, setFlightNumber] = useState('');
  const [date, setDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [flightData, setFlightData] = useState(null);

  const handleCheckStatus = async () => {
    if (!flightNumber.trim()) {
      setError('❗ Please enter a valid flight number (e.g., DL345).');
      return;
    }

    if (!date) {
      setError('❗ Please select a date.');
      return;
    }

    setLoading(true);
    setError('');
    setFlightData(null);

    try {
      const formattedDate = new Date(date).toISOString().split('T')[0];
      const response = await fetch(
        `http://127.0.0.1:3000/check-flight?flightNumber=${flightNumber.trim()}&date=${formattedDate}`
      );

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('No flight data found for this flight.');
        }
        throw new Error('Flight not found or backend error.');
      }

      const data = await response.json();
      setFlightData(data);
    } catch (err) {
      setError(`⚠️ ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const isDisrupted = (status) => {
    const lowered = status?.toLowerCase() || '';
    return lowered.includes('cancelled') || lowered.includes('diverted') || lowered.includes('delayed');
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#eef2f3',
      paddingTop: '60px',
      paddingBottom: '60px',
      fontFamily: 'Arial, sans-serif',
      overflowY: 'auto',
    }}>
      <div style={{
        backgroundColor: '#fff',
        padding: '30px',
        borderRadius: '15px',
        boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.15)',
        maxWidth: '700px',
        margin: '0 auto',
        textAlign: 'center'
      }}>
        <h1 style={{
          padding: '10px 20px',
          border: '2px solid black',
          borderRadius: '10px',
          display: 'inline-block',
          marginBottom: '30px',
          backgroundColor: '#fff',
          boxShadow: '2px 2px 6px rgba(0, 0, 0, 0.2)',
        }}>
          <span style={{
            color: '#2e86de',
            WebkitTextStroke: '1px black',
            fontWeight: 'bold',
            fontSize: '2.5rem'
          }}>
            FlightPulse
          </span> ✈️
        </h1>

        <div style={{
          display: 'flex',
          justifyContent: 'center',
          flexWrap: 'wrap',
          gap: '10px',
          marginBottom: '20px'
        }}>
          <input
            type="text"
            placeholder="Flight Number (e.g. DL345)"
            value={flightNumber}
            onChange={(e) => setFlightNumber(e.target.value)}
            style={{
              padding: '10px',
              width: '220px',
              borderRadius: '6px',
              border: '1px solid #ccc',
              boxShadow: '2px 2px 6px rgba(0, 0, 0, 0.1)',
            }}
          />
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            style={{
              padding: '10px',
              borderRadius: '6px',
              border: '1px solid #ccc',
              boxShadow: '2px 2px 6px rgba(0, 0, 0, 0.1)',
            }}
          />
          <button
            onClick={handleCheckStatus}
            style={{
              padding: '10px 15px',
              backgroundColor: '#2e86de',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              boxShadow: '2px 2px 6px rgba(0, 0, 0, 0.2)',
            }}
          >
            Check Status
          </button>
        </div>

        {loading && <p>🔄 Checking flight status...</p>}
        {error && <p style={{ color: 'red', fontWeight: 'bold' }}>{error}</p>}

        {flightData && (
          <div
            style={{
              border: '1px solid #e0e0e0',
              padding: '20px',
              borderRadius: '10px',
              backgroundColor: '#f9f9f9',
              boxShadow: '2px 2px 12px rgba(0, 0, 0, 0.1)',
              marginTop: '20px',
              textAlign: 'left'
            }}
          >
            <h2>🛫 Flight {flightData.flight_number} - {flightData.airline}</h2>

            {isDisrupted(flightData.status) && (
              <div style={{
                backgroundColor: '#ffe3e3',
                color: '#b30000',
                border: '1px solid #b30000',
                borderRadius: '6px',
                padding: '10px',
                marginBottom: '15px',
                fontWeight: 'bold',
              }}>
                ⚠️ Disruption Alert: This flight is {flightData.status.toUpperCase()}
              </div>
            )}

            <p><strong>Status:</strong> {flightData.status}</p>
            <p><strong>Departure:</strong> {flightData.departure} at {new Date(flightData.departure_time).toLocaleString()}</p>
            <p><strong>Arrival:</strong> {flightData.arrival} at {new Date(flightData.arrival_time).toLocaleString()}</p>
            <p><strong>Aircraft:</strong> {flightData.aircraft}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default FlightChecker;
