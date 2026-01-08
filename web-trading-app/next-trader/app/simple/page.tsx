export default function SimplePage() {
  return (
    <div style={{ 
      padding: '40px', 
      backgroundColor: '#1e293b',
      color: 'white',
      minHeight: '100vh',
      fontFamily: 'sans-serif'
    }}>
      <h1 style={{ fontSize: '32px', marginBottom: '20px' }}>
        🎯 Simple Test Page
      </h1>
      <p style={{ fontSize: '18px', marginBottom: '10px' }}>
        ✅ Next.js is working
      </p>
      <p style={{ fontSize: '18px', marginBottom: '10px' }}>
        ✅ Server is rendering
      </p>
      <p style={{ fontSize: '16px', color: '#94a3b8' }}>
        Navigate to <code>/</code> for the trading interface
      </p>
    </div>
  );
}


