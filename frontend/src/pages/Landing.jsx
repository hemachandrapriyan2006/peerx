import React from 'react'
import { Link } from 'react-router-dom'
import { Cpu, GraduationCap, Zap, Lightbulb, CheckCircle2, ShieldAlert, ArrowRight, Sparkles, Network, BrainCircuit, Activity } from 'lucide-react'

export const Landing = () => {
  const agents = [
    { name: 'Sophia', role: 'Mentor AI', desc: 'Explains concepts using Socratic questions', color: '#10b981', icon: GraduationCap },
    { name: 'Ares', role: 'Challenger AI', desc: 'Debates your logic and finds edge cases', color: '#a855f7', icon: Zap },
    { name: 'Nova', role: 'Creative AI', desc: 'Provides real-world analogies and visual metaphors', color: '#f59e0b', icon: Lightbulb },
    { name: 'Argus', role: 'Reviewer AI', desc: 'Scores reasoning quality and pinpoints knowledge gaps', color: '#3b82f6', icon: CheckCircle2 },
    { name: 'Apex', role: 'Problem Solver', desc: 'Dynamically adapts difficulty and creates personalized challenges', color: '#ef4444', icon: ShieldAlert }
  ]

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '40px 24px' }}>
      {/* Hero Section */}
      <div style={{
        textAlign: 'center',
        padding: '60px 20px',
        position: 'relative'
      }}>
        {/* Glow badge */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#e0f2fe', border: '1px solid #bae6fd', padding: '6px 16px', borderRadius: '9999px', fontSize: '0.85rem', fontWeight: 600, color: '#0284c7', marginBottom: '24px' }}>
          <Sparkles size={16} />
          Teaching-First Adaptive Learning • Multi-Agent AI Study Swarm
        </div>

        <h1 style={{
          fontSize: '3.5rem',
          fontWeight: 800,
          lineHeight: 1.15,
          color: '#0f172a',
          marginBottom: '20px',
          letterSpacing: '-0.03em'
        }}>
          Autonomous AI <span style={{
            background: 'linear-gradient(135deg, #0284c7 0%, #7e22ce 50%, #db2777 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>Peer-Learning Network</span>
        </h1>

        <p style={{
          fontSize: '1.2rem',
          color: '#475569',
          maxWidth: '750px',
          margin: '0 auto 36px auto',
          lineHeight: 1.6
        }}>
          Experience a teaching-first adaptive flow powered by a <strong>swarm of 5 specialized AI study peers</strong> that teach first, reinforce with analogies, challenge your reasoning, evaluate responses, and generate targeted practice!
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <Link to="/learn" className="btn-primary" style={{ textDecoration: 'none', padding: '14px 32px', fontSize: '1.05rem' }}>
            <span>Enter AI Study Room</span>
            <ArrowRight size={20} />
          </Link>
          <Link to="/dashboard" className="btn-secondary" style={{ textDecoration: 'none', padding: '14px 28px', fontSize: '1.05rem' }}>
            <span>View Dashboard</span>
          </Link>
        </div>
      </div>

      {/* Differentiator Pipeline diagram */}
      <div className="glass-card" style={{ padding: '36px', margin: '40px 0', textTransform: 'none' }}>
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 700, color: '#0f172a', marginBottom: '8px' }}>
            Teaching-First Closed-Loop Engine
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.95rem' }}>
            From initial concept teaching to targeted gap reinforcement
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '16px',
          alignItems: 'center'
        }}>
          {[
            { step: '1. 📚 Mentor Teaches', icon: GraduationCap, color: '#059669' },
            { step: '2. 💡 Creative Reinforces', icon: Lightbulb, color: '#d97706' },
            { step: '3. 🧠 Challenger Assesses', icon: Zap, color: '#7e22ce' },
            { step: '4. 🔍 Reviewer Evaluates', icon: CheckCircle2, color: '#2563eb' },
            { step: '5. 🎯 Targeted Practice', icon: ShieldAlert, color: '#dc2626' }
          ].map((item, idx) => {
            const Icon = item.icon
            return (
              <div key={idx} style={{
                background: '#f8fafc',
                border: `1px solid ${item.color}30`,
                padding: '16px',
                borderRadius: '12px',
                textAlign: 'center'
              }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '10px',
                  background: `${item.color}15`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 10px auto'
                }}>
                  <Icon size={22} color={item.color} />
                </div>
                <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a' }}>
                  {item.step}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Agents Swarm Overview Grid */}
      <div style={{ marginTop: '50px' }}>
        <h3 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#0f172a', textAlign: 'center', marginBottom: '24px' }}>
          Meet Your Specialized AI Peer Swarm
        </h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))',
          gap: '20px'
        }}>
          {agents.map((agent, i) => {
            const Icon = agent.icon
            return (
              <div key={i} className="glass-card" style={{ padding: '24px', borderTop: `4px solid ${agent.color}` }}>
                <div style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: '10px',
                  background: `${agent.color}15`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '14px'
                }}>
                  <Icon size={24} color={agent.color} />
                </div>
                <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
                  {agent.name}
                </h4>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: agent.color, textTransform: 'uppercase', marginBottom: '10px' }}>
                  {agent.role}
                </div>
                <p style={{ fontSize: '0.88rem', color: '#475569', lineHeight: 1.5 }}>
                  {agent.desc}
                </p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
