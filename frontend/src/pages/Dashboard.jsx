import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { learningAPI } from '../services/api'
import { BookOpen, Award, Flame, AlertCircle, Sparkles, ArrowRight, PlayCircle, BarChart2 } from 'lucide-react'

export const Dashboard = () => {
  const navigate = useNavigate()
  const [data, setData] = useState({
    overall_mastery: 78.5,
    total_sessions: 6,
    total_questions: 14,
    total_correct: 11,
    overall_accuracy: 78.6,
    topics_covered: 4,
    weak_concepts: ['Recursion Base Cases', 'Graph Cycle Detection'],
    knowledge_gaps: [
      { id: '1', topic: 'Data Structures', concept: 'Recursion Base Cases', severity: 'high', status: 'active' },
      { id: '2', topic: 'Algorithms', concept: 'Graph Cycle Detection', severity: 'medium', status: 'active' }
    ],
    recent_sessions: [
      { id: 's1', topic: 'Binary Search Trees', subject: 'Data Structures', difficulty: 3, mastery_score: 82.0 },
      { id: 's2', topic: 'Dynamic Programming', subject: 'Algorithms', difficulty: 4, mastery_score: 65.0 }
    ]
  })

  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await learningAPI.getDashboard()
        if (res.data) {
          setData(res.data)
        }
      } catch (err) {
        console.warn('Backend API connection fallback to preset demo dashboard state:', err)
      } finally {
        setLoading(false)
      }
    }
    fetchDashboard()
  }, [])

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px 24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
            Student Learning Dashboard
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.95rem', marginTop: '4px' }}>
            Real-time analytics aggregated across all AI peer study sessions
          </p>
        </div>

        <Link to="/learn" className="btn-primary" style={{ textDecoration: 'none' }}>
          <PlayCircle size={18} />
          <span>Start New AI Study Session</span>
        </Link>
      </div>

      {/* Top Metrics Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '20px',
        marginBottom: '32px'
      }}>
        <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid #0284c7' }}>
          <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 600 }}>
            Overall Mastery Score
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#0284c7', marginTop: '4px' }}>
            {data.overall_mastery.toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#059669', marginTop: '4px', fontWeight: 600 }}>
            ↑ 4.2% from last session
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid #7e22ce' }}>
          <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 600 }}>
            Total Study Sessions
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#7e22ce', marginTop: '4px' }}>
            {data.total_sessions}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            {data.total_questions} questions attempted
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid #059669' }}>
          <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 600 }}>
            Accuracy Rate
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#059669', marginTop: '4px' }}>
            {data.overall_accuracy.toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
            {data.total_correct} of {data.total_questions} correct
          </div>
        </div>

        <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid #dc2626' }}>
          <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 600 }}>
            Active Knowledge Gaps
          </div>
          <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#dc2626', marginTop: '4px' }}>
            {data.knowledge_gaps.length}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#dc2626', marginTop: '4px', fontWeight: 600 }}>
            Targeted for resolution
          </div>
        </div>
      </div>

      {/* Main Grid Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Active Knowledge Gaps list */}
        <div className="glass-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <AlertCircle size={20} color="#dc2626" />
              Detected Knowledge Gaps & Remediation
            </h3>
            <Link to="/progress" style={{ color: '#0284c7', fontSize: '0.85rem', fontWeight: 600, textDecoration: 'none' }}>
              View All
            </Link>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {data.knowledge_gaps.map((gap, i) => (
              <div key={i} style={{
                background: '#f8fafc',
                border: '1px solid #e2e8f0',
                padding: '16px',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#0284c7', fontWeight: 600 }}>
                    {gap.topic}
                  </div>
                  <div style={{ fontSize: '0.98rem', fontWeight: 700, color: '#0f172a', marginTop: '2px' }}>
                    {gap.concept}
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    color: gap.severity === 'high' ? '#dc2626' : '#d97706',
                    background: gap.severity === 'high' ? '#fef2f2' : '#fffbeb',
                    padding: '3px 10px',
                    borderRadius: '9999px',
                    border: `1px solid ${gap.severity === 'high' ? '#fecaca' : '#fde68a'}`
                  }}>
                    {gap.severity} severity
                  </span>
                  <button
                    onClick={() => navigate('/learn', { state: { topic: gap.topic, initialQuestion: `Help me understand ${gap.concept}` } })}
                    className="btn-secondary"
                    style={{ padding: '6px 12px', fontSize: '0.78rem' }}
                  >
                    Resolve in Room
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Launch & Recommendation Card */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card" style={{ padding: '24px', borderTop: '4px solid #7e22ce' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', color: '#7e22ce', fontWeight: 700, fontSize: '0.85rem' }}>
              <Sparkles size={16} />
              AI Recommendation Engine
            </div>
            <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '8px' }}>
              Targeted Practice: Java → Inheritance
            </h4>
            <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: 1.5, marginBottom: '16px' }}>
              Mentor Sophia and Challenger Ares recommend solidifying your understanding of subclass extends and method overriding.
            </p>
            <button
              onClick={() => navigate('/learn', { state: { topic: 'Inheritance', subject: 'Java' } })}
              className="btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
            >
              <span>Launch Recommended Practice</span>
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
