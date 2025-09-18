import { useEffect, useState } from 'react';
import './Dashboard.css';

function Dashboard() {
  const [summaryData, setSummaryData] = useState(null);
  const [error,       setError]       = useState('');
  const [loading,     setLoading]     = useState(true);

  // 1) Airport list & state
  const airports = ['ATL', 'JFK', 'LAX', 'ORD'];
  const [airport, setAirport] = useState(airports[0]);

  useEffect(() => {
    const fetchSummary = async () => {
      setLoading(true);
      setError('');
      try {
        const url = `http://127.0.0.1:3000/dashboard-flights?airport=${encodeURIComponent(airport)}`;
        console.log('Fetching dashboard summary from:', url);

        const res = await fetch(url);
        if (!res.ok) throw new Error(`Failed (status ${res.status})`);
        const data = await res.json();
        setSummaryData(data);
      } catch (err) {
        console.error('Error fetching dashboard summary:', err);
        setError('⚠️ Unable to fetch summary data.');
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, [airport]);

  return (
    <div className="dashboard-container">
      <div className="airport-selector">
        <label htmlFor="airport">Select Airport:</label>
        <select
          id="airport"
          value={airport}
          onChange={e => setAirport(e.target.value)}
        >
          {airports.map(code => (
            <option key={code} value={code}>
              {code}
            </option>
          ))}
        </select>
      </div>

      <h1 className="dashboard-title">📊 Flight Status Dashboard</h1>
      {loading && <p>Loading summary...</p>}
      {error   && <p className="error">{error}</p>}
      {summaryData && (
        <div className="status-grid">
          {['on_time', 'delayed', 'cancelled'].map(status => (
            <div key={status} className="status-card">
              <h2>{status.replace('_', ' ').toUpperCase()}</h2>
              <p>{summaryData.summary[status]}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
 