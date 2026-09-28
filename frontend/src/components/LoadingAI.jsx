import React from 'react'
import { Sparkles, Cpu } from 'lucide-react'

export const LoadingAI = ({ message = 'AI peer swarm analyzing response...' }) => {
  return (
    <div className="glass-card" style={{
      padding: '32px',
      textAlign: 'center',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '16px',
      margin: '20px 0'
    }}>
      <div style={{
        position: 'relative',
        width: '60px',
        height: '60px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <div style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '50%',
          border: '2px dashed #38bdf8',
          animation: 'spin 3s linear infinite'
        }} />
        <Cpu size={28} color="#38bdf8" />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f8fafc', fontWeight: 600 }}>
        <Sparkles size={18} color="#c084fc" className="pulse" />
        <span>{message}</span>
      </div>

      <p style={{ fontSize: '0.8rem', color: '#94a3b8', maxWidth: '400px' }}>
        Mentor, Challenger, and Reviewer agents are collaborating to score your reasoning and detect knowledge gaps.
      </p>

      <style>{`
        @keyframes spin {
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  )
}
