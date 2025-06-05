'use client'

export default function TestPage() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#111827', 
      color: '#FFFFFF',
      padding: '2rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem'
    }}>
      <h1 style={{ fontSize: '2rem', fontWeight: 'bold' }}>Test Page</h1>
      <p style={{ fontSize: '1.125rem' }}>This is a simple test page to verify the frontend is working.</p>
      
      <div style={{ 
        backgroundColor: '#1F2937', 
        border: '1px solid #374151',
        borderRadius: '0.5rem',
        padding: '1rem'
      }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>Test Form</h2>
        <input 
          type="text" 
          placeholder="Enter some text"
          style={{
            width: '100%',
            padding: '0.5rem',
            backgroundColor: '#374151',
            border: '1px solid #4B5563',
            borderRadius: '0.375rem',
            color: '#FFFFFF',
            marginBottom: '1rem'
          }}
        />
        <button 
          style={{
            backgroundColor: '#2563EB',
            color: '#FFFFFF',
            padding: '0.5rem 1rem',
            borderRadius: '0.375rem',
            border: 'none',
            cursor: 'pointer'
          }}
          onClick={() => alert('Test button works!')}
        >
          Test Button
        </button>
      </div>
      
      <div style={{ marginTop: '2rem' }}>
        <a 
          href="/analysis" 
          style={{ 
            color: '#60A5FA', 
            textDecoration: 'underline' 
          }}
        >
          Go back to Analysis page
        </a>
      </div>
    </div>
  )
}