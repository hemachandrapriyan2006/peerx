import React from 'react'
import { GraduationCap, Zap, Lightbulb, CheckCircle2, ShieldAlert, Sparkles, MessageSquare } from 'lucide-react'

const AGENT_CONFIGS = {
  mentor: {
    title: 'Sophia (Mentor AI)',
    role: 'Guide & Explainer',
    icon: GraduationCap,
    color: '#10b981',
    bgColor: 'rgba(16, 185, 129, 0.1)',
    borderColor: 'rgba(16, 185, 129, 0.3)',
    tag: 'Socratic Facilitator'
  },
  challenger: {
    title: 'Ares (Challenger AI)',
    role: 'Debater & Counter-Arguer',
    icon: Zap,
    color: '#a855f7',
    bgColor: 'rgba(168, 85, 247, 0.1)',
    borderColor: 'rgba(168, 85, 247, 0.3)',
    tag: 'Critical Examiner'
  },
  creative: {
    title: 'Nova (Creative AI)',
    role: 'Analogy & Real-World Visualizer',
    icon: Lightbulb,
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.1)',
    borderColor: 'rgba(245, 158, 11, 0.3)',
    tag: 'Lateral Thinker'
  },
  reviewer: {
    title: 'Argus (Reviewer AI)',
    role: 'Evaluator & Gap Detector',
    icon: CheckCircle2,
    color: '#3b82f6',
    bgColor: 'rgba(59, 130, 246, 0.1)',
    borderColor: 'rgba(59, 130, 246, 0.3)',
    tag: 'Diagnostic Evaluator'
  },
  problem_solver: {
    title: 'Apex (Problem Solver)',
    role: 'Adaptive Challenge Architect',
    icon: ShieldAlert,
    color: '#ef4444',
    bgColor: 'rgba(239, 68, 68, 0.1)',
    borderColor: 'rgba(239, 68, 68, 0.3)',
    tag: 'Challenge Creator'
  }
}

export const AgentCard = ({ agentType, content, isThinking = false, onPromptAgent }) => {
  const config = AGENT_CONFIGS[agentType] || AGENT_CONFIGS.mentor
  const Icon = config.icon

  return (
    <div
      className="glass-card"
      style={{
        padding: '20px',
        borderLeft: `4px solid ${config.color}`,
        position: 'relative',
        marginBottom: '16px'
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: config.bgColor,
            border: `1px solid ${config.borderColor}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Icon size={20} color={config.color} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              {config.title}
            </h4>
            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
              {config.role}
            </span>
          </div>
        </div>

        <span style={{
          fontSize: '0.7rem',
          fontWeight: 600,
          color: config.color,
          background: config.bgColor,
          border: `1px solid ${config.borderColor}`,
          padding: '3px 10px',
          borderRadius: '9999px'
        }}>
          {config.tag}
        </span>
      </div>

      {/* Body / Message Content */}
      {isThinking ? (
        <div style={{ padding: '16px 0', display: 'flex', alignItems: 'center', gap: '10px', color: '#64748b' }}>
          <Sparkles className="pulse" size={18} color={config.color} />
          <span style={{ fontSize: '0.85rem', fontStyle: 'italic' }}>
            {config.title} is synthesizing insights...
          </span>
        </div>
      ) : (
        <div style={{ fontSize: '0.92rem', color: '#1e293b', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
          {typeof content === 'string' ? (
            content
          ) : typeof content === 'object' && content !== null ? (
            <div>
              {(content.explanation || content.message || content.text || content.content || content.teaching_content) && (
                <div style={{ marginBottom: '12px' }}>
                  {content.explanation || content.message || content.text || content.content || content.teaching_content}
                </div>
              )}
              {content.code_example && (
                <div style={{ marginBottom: '12px' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0284c7', textTransform: 'uppercase' }}>Code Example:</span>
                  <div className="code-box">
                    <pre><code>{content.code_example}</code></pre>
                  </div>
                </div>
              )}
              {content.example && (
                <div style={{ marginBottom: '8px', padding: '10px 14px', background: '#f8fafc', borderRadius: '8px', borderLeft: `3px solid ${config.color}` }}>
                  <strong style={{ color: config.color }}>Example: </strong>{content.example}
                </div>
              )}
              {content.key_takeaway && (
                <div style={{ marginTop: '10px', fontSize: '0.88rem', fontWeight: 600, color: '#0f172a' }}>
                  💡 Key Takeaway: {content.key_takeaway}
                </div>
              )}
              {content.perspective && !(content.explanation || content.message || content.text || content.content || content.teaching_content) && (
                <div>{content.perspective}</div>
              )}
              {content.analogy && (
                <div style={{ marginTop: '8px', fontStyle: 'italic', color: '#475569' }}>
                  🎨 Analogy: {content.analogy}
                </div>
              )}
              {content.question && !(content.explanation || content.message || content.text || content.content || content.teaching_content) && (
                <div style={{ fontWeight: 600, fontSize: '1rem', color: '#0f172a' }}>{content.question}</div>
              )}
              {content.hint && (
                <div style={{ marginTop: '8px', fontSize: '0.85rem', color: '#64748b' }}>
                  💡 Hint: {content.hint}
                </div>
              )}
            </div>
          ) : (
            JSON.stringify(content, null, 2)
          )}
        </div>

      )}

      {/* Action footer */}
      {onPromptAgent && !isThinking && (
        <div style={{ marginTop: '14px', paddingTop: '10px', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={() => onPromptAgent(agentType)}
            style={{
              background: '#ffffff',
              border: `1px solid ${config.borderColor}`,
              color: config.color,
              padding: '4px 12px',
              borderRadius: '6px',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <MessageSquare size={14} />
            Ask {config.title.split(' ')[0]}
          </button>
        </div>
      )}
    </div>
  )
}
