import React from 'react'
import { Target, Award, Flame, AlertCircle } from 'lucide-react'

export const ProgressCard = ({ topic, masteryScore = 0, questionsAttempted = 0, currentDifficulty = 1, gaps = [] }) => {
  const getDifficultyColor = (diff) => {
    switch(diff) {
      case 1: return '#34d399' // Beginner
      case 2: return '#38bdf8' // Easy
      case 3: return '#fbbf24' // Intermediate
      case 4: return '#f472b6' // Advanced
      case 5: return '#fb7185' // Expert
      default: return '#38bdf8'
    }
  }

  const diffLabels = ['Beginner', 'Easy', 'Intermediate', 'Advanced', 'Expert']

  return (
    <div className="glass-card" style={{ padding: '20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div>
          <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.05em' }}>
            📈 Current Progress
          </span>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
            {topic || 'Computer Science'}
          </h3>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: '#f8fafc',
          padding: '6px 12px',
          borderRadius: '8px',
          border: `1px solid ${getDifficultyColor(currentDifficulty)}`
        }}>
          <Flame size={16} color={getDifficultyColor(currentDifficulty)} />
          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: getDifficultyColor(currentDifficulty) }}>
            Lvl {currentDifficulty}: {diffLabels[currentDifficulty - 1] || 'Intermediate'}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div style={{ marginBottom: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
          <span style={{ color: '#475569' }}>Mastery Index</span>
          <span style={{ fontWeight: 700, color: '#0284c7' }}>{masteryScore.toFixed(1)}%</span>
        </div>
        <div style={{
          height: '8px',
          width: '100%',
          background: '#e2e8f0',
          borderRadius: '4px',
          overflow: 'hidden'
        }}>
          <div style={{
            height: '100%',
            width: `${Math.min(100, Math.max(0, masteryScore))}%`,
            background: 'linear-gradient(90deg, #0284c7 0%, #7e22ce 100%)',
            borderRadius: '4px',
            transition: 'width 0.5s ease-out'
          }} />
        </div>
      </div>

      {/* Stats summary */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', padding: '10px', borderRadius: '8px' }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Attempts</div>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a' }}>{questionsAttempted}</div>
        </div>
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', padding: '10px', borderRadius: '8px' }}>
          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Active Gaps</div>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: gaps.length > 0 ? '#dc2626' : '#059669' }}>
            {gaps.length}
          </div>
        </div>
      </div>

      {/* Active Knowledge Gaps */}
      {gaps.length > 0 && (
        <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: '#dc2626', fontWeight: 600, marginBottom: '8px' }}>
            <AlertCircle size={14} />
            Detected Knowledge Gaps:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {gaps.map((gap, i) => (
              <span key={i} style={{
                fontSize: '0.72rem',
                background: '#fef2f2',
                border: '1px solid #fecaca',
                color: '#991b1b',
                padding: '2px 8px',
                borderRadius: '6px'
              }}>
                {typeof gap === 'string' ? gap : gap.concept}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
