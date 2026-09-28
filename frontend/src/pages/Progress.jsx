import React, { useState, useEffect } from 'react'
import { progressAPI, learningAPI } from '../services/api'
import { TrendingUp, Award, CheckCircle2, AlertCircle, BarChart, BookOpen, Layers } from 'lucide-react'

export const Progress = () => {
  const [topics, setTopics] = useState([
    { topic: 'Data Structures', questions_attempted: 12, questions_correct: 10, accuracy: 83.3, mastery_score: 85.0, current_difficulty: 3 },
    { topic: 'Algorithms', questions_attempted: 8, questions_correct: 6, accuracy: 75.0, mastery_score: 72.0, current_difficulty: 3 },
    { topic: 'Operating Systems', questions_attempted: 5, questions_correct: 4, accuracy: 80.0, mastery_score: 78.5, current_difficulty: 2 },
    { topic: 'Database Systems', questions_attempted: 3, questions_correct: 2, accuracy: 66.7, mastery_score: 64.0, current_difficulty: 2 }
  ])

  const [gaps, setGaps] = useState([
    { id: '1', topic: 'Data Structures', concept: 'Recursion Base Cases', severity: 'high', status: 'active', created_at: '2026-09-18' },
    { id: '2', topic: 'Algorithms', concept: 'Graph Cycle Detection', severity: 'medium', status: 'active', created_at: '2026-09-17' },
    { id: '3', topic: 'Operating Systems', concept: 'Page Replacement LRU', severity: 'low', status: 'improving', created_at: '2026-09-16' }
  ])

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resTopics, resGaps] = await Promise.all([
          progressAPI.getTopicMastery(),
          learningAPI.getKnowledgeGaps()
        ])
        if (resTopics.data) setTopics(resTopics.data)
        if (resGaps.data) setGaps(resGaps.data)
      } catch (err) {
        console.warn('Backend API connection fallback to mock progress dataset:', err)
      }
    }
    fetchData()
  }, [])

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
          Learning Progress & Diagnostic Analytics
        </h1>
        <p style={{ color: '#64748b', fontSize: '0.95rem', marginTop: '4px' }}>
          Detailed breakdown of topic mastery scores, accuracy metrics, and identified knowledge gaps
        </p>
      </div>

      {/* Topic Mastery Grid */}
      <div className="glass-card" style={{ padding: '28px', marginBottom: '32px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BookOpen size={20} color="#0284c7" />
          Topic Mastery Breakdown
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px' }}>
          {topics.map((t, idx) => (
            <div key={idx} style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              padding: '20px',
              borderRadius: '12px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                  {t.topic}
                </h4>
                <span className="badge" style={{ background: '#e0f2fe', color: '#0284c7' }}>
                  Lvl {t.current_difficulty}
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                <span style={{ color: '#64748b' }}>Mastery Index</span>
                <span style={{ fontWeight: 700, color: '#0284c7' }}>{t.mastery_score.toFixed(1)}%</span>
              </div>

              <div style={{ height: '8px', background: '#e2e8f0', borderRadius: '4px', overflow: 'hidden', marginBottom: '14px' }}>
                <div style={{
                  height: '100%',
                  width: `${t.mastery_score}%`,
                  background: 'linear-gradient(90deg, #0284c7, #7e22ce)',
                  borderRadius: '4px'
                }} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#64748b' }}>
                <span>Accuracy: <strong style={{ color: '#0f172a' }}>{t.accuracy.toFixed(1)}%</strong></span>
                <span>Attempts: <strong style={{ color: '#0f172a' }}>{t.questions_attempted}</strong></span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comprehensive Knowledge Gap Log */}
      <div className="glass-card" style={{ padding: '28px' }}>
        <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertCircle size={20} color="#dc2626" />
          Active Diagnostic Knowledge Gap Log
        </h3>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #e2e8f0', color: '#64748b' }}>
                <th style={{ padding: '12px' }}>Topic</th>
                <th style={{ padding: '12px' }}>Concept Gap</th>
                <th style={{ padding: '12px' }}>Severity</th>
                <th style={{ padding: '12px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {gaps.map((gap, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #f1f5f9', color: '#334155' }}>
                  <td style={{ padding: '14px 12px', fontWeight: 600 }}>{gap.topic}</td>
                  <td style={{ padding: '14px 12px' }}>{gap.concept}</td>
                  <td style={{ padding: '14px 12px' }}>
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      color: gap.severity === 'high' ? '#dc2626' : gap.severity === 'medium' ? '#d97706' : '#059669',
                      background: gap.severity === 'high' ? '#fef2f2' : '#fffbeb',
                      padding: '3px 8px',
                      borderRadius: '6px'
                    }}>
                      {gap.severity}
                    </span>
                  </td>
                  <td style={{ padding: '14px 12px' }}>
                    <span style={{
                      fontSize: '0.75rem',
                      color: gap.status === 'resolved' ? '#059669' : '#0284c7',
                      textTransform: 'capitalize'
                    }}>
                      {gap.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
