import React from 'react'
import { Award, CheckCircle2, AlertTriangle, TrendingUp } from 'lucide-react'

export const ScoreCard = ({ review }) => {
  if (!review) return null

  const { score = 0, correctness = 'correct', reasoning_quality = 'good', feedback = '', strengths = [], weaknesses = [] } = review

  const getScoreColor = (s) => {
    if (s >= 80) return '#059669'
    if (s >= 60) return '#0284c7'
    if (s >= 40) return '#d97706'
    return '#dc2626'
  }

  return (
    <div className="glass-card" style={{
      padding: '24px',
      borderLeft: `4px solid ${getScoreColor(score)}`,
      background: '#ffffff',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: `${getScoreColor(score)}15`,
            border: `1px solid ${getScoreColor(score)}40`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.3rem',
            fontWeight: 800,
            color: getScoreColor(score)
          }}>
            {score}
          </div>
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Reviewer Assessment
            </h3>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
              Reasoning Quality: <strong style={{ color: getScoreColor(score), textTransform: 'capitalize' }}>{reasoning_quality}</strong>
            </span>
          </div>
        </div>

        <span className="badge" style={{
          background: `${getScoreColor(score)}15`,
          color: getScoreColor(score),
          border: `1px solid ${getScoreColor(score)}40`
        }}>
          {correctness.replace('_', ' ')}
        </span>
      </div>

      {/* Feedback Text */}
      <p style={{ fontSize: '0.92rem', color: '#1e293b', marginBottom: '16px', lineHeight: 1.6 }}>
        {feedback}
      </p>

      {/* Strengths & Weaknesses grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        {strengths.length > 0 && (
          <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', padding: '12px', borderRadius: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#059669', fontWeight: 700, marginBottom: '6px' }}>
              <CheckCircle2 size={14} /> Key Strengths
            </div>
            <ul style={{ paddingLeft: '16px', margin: 0, fontSize: '0.8rem', color: '#064e3b' }}>
              {strengths.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
          </div>
        )}

        {weaknesses.length > 0 && (
          <div style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '12px', borderRadius: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: '#dc2626', fontWeight: 700, marginBottom: '6px' }}>
              <AlertTriangle size={14} /> Areas to Improve / Mistakes
            </div>
            <ul style={{ paddingLeft: '16px', margin: 0, fontSize: '0.8rem', color: '#7f1d1d' }}>
              {weaknesses.map((w, i) => <li key={i}>{w}</li>)}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
