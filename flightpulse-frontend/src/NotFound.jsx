import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <h1 style={{ color: '#e74c3c' }}>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <Link to="/" style={{ color: '#2e86de', fontWeight: 'bold' }}>Go Home</Link>
    </div>
  );
}

export default NotFound;
