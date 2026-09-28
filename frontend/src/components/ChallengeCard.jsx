import React, { useState } from 'react'
import { ShieldAlert, HelpCircle, ArrowRight, Sparkles } from 'lucide-react'

export const ChallengeCard = ({ challenge, onAcceptChallenge }) => {
  const [showHint, setShowHint] = useState(false)

  if (!challenge) return null

  const { question, difficulty = 1, concept, hint, expected_skill } = challenge

  const diffLabels = ['Beginner', 'Easy', 'Intermediate', 'Advanced', 'Expert']

  return (
    <div className="glass-card" style={{
      padding: '24px',
      borderLeft: '4px solid #dc2626',
      background: '#fff5f5',
      marginBottom: '20px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldAlert size={20} color="#dc2626" />
          <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
            🎯 Targeted Practice Question (Gap Reinforcement)
          </h4>
        </div>

        <span style={{
          fontSize: '0.72rem',
          fontWeight: 700,
          background: '#fee2e2',
          color: '#dc2626',
          border: '1px solid #fca5a5',
          padding: '3px 10px',
          borderRadius: '9999px'
        }}>
          Level {difficulty}: {diffLabels[difficulty - 1]}
        </span>
      </div>

      <p style={{ fontSize: '1rem', color: '#0f172a', fontWeight: 600, marginBottom: '14px', lineHeight: 1.5 }}>
        {question}
      </p>

      {(concept || expected_skill) && (
        <div style={{ display: 'flex', gap: '8px', marginBottom: '14px', flexWrap: 'wrap' }}>
          {concept && (
            <span style={{ fontSize: '0.75rem', background: '#f1f5f9', color: '#475569', border: '1px solid #e2e8f0', padding: '2px 8px', borderRadius: '4px' }}>
              Targeted Concept: {concept}
            </span>
          )}
          {expected_skill && (
            <span style={{ fontSize: '0.75rem', background: '#f1f5f9', color: '#475569', border: '1px solid #e2e8f0', padding: '2px 8px', borderRadius: '4px' }}>
              Required Skill: {expected_skill}
            </span>
          )}
        </div>
      )}

      {/* Hint toggle */}
      {hint && (
        <div style={{ marginBottom: '16px' }}>
          {!showHint ? (
            <button
              onClick={() => setShowHint(true)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#d97706',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: 0
              }}
            >
              <HelpCircle size={14} /> Need a hint?
            </button>
          ) : (
            <div style={{
              background: '#fffbeb',
              border: '1px solid #fde68a',
              padding: '10px 14px',
              borderRadius: '8px',
              fontSize: '0.85rem',
              color: '#92400e'
            }}>
              💡 <strong>Hint:</strong> {hint}
            </div>
          )}
        </div>
      )}

      {onAcceptChallenge && (
        <button
          onClick={() => onAcceptChallenge(question)}
          className="btn-primary"
          style={{ width: '100%', justifyContent: 'center', padding: '10px' }}
        >
          <span>Attempt Targeted Practice</span>
          <ArrowRight size={16} />
        </button>
      )}
    </div>
  )
}
