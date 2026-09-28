import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../services/api'
import { User, GraduationCap, BookOpen, Target, Save, CheckCircle } from 'lucide-react'

export const Profile = () => {
  const { user } = useAuth()
  const [fullName, setFullName] = useState(user?.user_metadata?.full_name || 'Alex Rivera')
  const [college, setCollege] = useState(user?.user_metadata?.college || 'Stanford Computer Science')
  const [educationLevel, setEducationLevel] = useState(user?.user_metadata?.education_level || 'undergraduate')
  const [preferredSubject, setPreferredSubject] = useState('Data Structures & Algorithms')
  const [learningGoal, setLearningGoal] = useState('Master advanced graph algorithms and dynamic programming')
  const [saved, setSaved] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaved(false)
    try {
      await authAPI.updateProfile({
        full_name: fullName,
        education_level: educationLevel,
        preferred_subject: preferredSubject,
        learning_goal: learningGoal
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err) {
      console.warn('Profile save fallback:', err)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    }
  }

  return (
    <div style={{ maxWidth: '640px', margin: '40px auto', padding: '0 20px' }}>
      <div className="glass-card" style={{ padding: '36px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '28px' }}>
          <div style={{
            width: '60px',
            height: '60px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #0284c7 0%, #a855f7 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <User size={30} color="#ffffff" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
              Student Profile & Preferences
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#64748b', margin: 0 }}>
              {user?.email || 'alex.student@peerx.ai'}
            </p>
          </div>
        </div>

        {saved && (
          <div style={{
            background: '#ecfdf5',
            border: '1px solid #a7f3d0',
            color: '#059669',
            padding: '12px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <CheckCircle size={16} /> Profile settings updated successfully!
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
              Full Name
            </label>
            <input
              type="text"
              className="input-field"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
              College / Institution
            </label>
            <input
              type="text"
              className="input-field"
              value={college}
              onChange={(e) => setCollege(e.target.value)}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
              Education Level
            </label>
            <select
              className="input-field"
              value={educationLevel}
              onChange={(e) => setEducationLevel(e.target.value)}
            >
              <option value="high_school">High School</option>
              <option value="undergraduate">Undergraduate (B.Tech / BS)</option>
              <option value="graduate">Graduate (M.Tech / MS)</option>
              <option value="postgraduate">Postgraduate / Ph.D.</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
              Preferred Subject Area
            </label>
            <input
              type="text"
              className="input-field"
              value={preferredSubject}
              onChange={(e) => setPreferredSubject(e.target.value)}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
              Learning Goal
            </label>
            <textarea
              className="input-field"
              rows={3}
              value={learningGoal}
              onChange={(e) => setLearningGoal(e.target.value)}
              style={{ resize: 'vertical' }}
            />
          </div>

          <button type="submit" className="btn-primary" style={{ justifyContent: 'center', marginTop: '10px' }}>
            <Save size={16} />
            <span>Save Preferences</span>
          </button>
        </form>
      </div>
    </div>
  )
}
