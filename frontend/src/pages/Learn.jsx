import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { sessionAPI } from '../services/api'
import { AgentCard } from '../components/AgentCard'
import { LoadingAI } from '../components/LoadingAI'
import { ProgressCard } from '../components/ProgressCard'
import { ScoreCard } from '../components/ScoreCard'
import { ChallengeCard } from '../components/ChallengeCard'
import {
  GraduationCap, Zap, Lightbulb, CheckCircle2, ShieldAlert,
  Send, Sparkles, RefreshCw, BookOpen, Layers, ArrowRight, Compass,
  AlertCircle
} from 'lucide-react'

const SAMPLE_TOPICS = [
  { topic: 'Java Inheritance', subject: 'Java', difficulty: 2 },
  { topic: 'Python Functions', subject: 'Python', difficulty: 2 },
  { topic: 'DBMS Normalization', subject: 'Database Systems', difficulty: 2 },
  { topic: 'Binary Search Trees', subject: 'Data Structures', difficulty: 2 },
  { topic: 'Dynamic Programming', subject: 'Algorithms', difficulty: 3 },
  { topic: 'Page Replacement & LRU', subject: 'Operating Systems', difficulty: 3 },
  { topic: 'React Hooks', subject: 'Web Development', difficulty: 2 }
]

export const Learn = () => {
  const location = useLocation()

  // Topic input selection state
  const [selectedTopic, setSelectedTopic] = useState(location.state?.topic || '')
  const [selectedSubject, setSelectedSubject] = useState(location.state?.subject || 'General')
  const [selectedDifficulty, setSelectedDifficulty] = useState(2)

  // Active Session state & Explicit Stage Tracking
  const [sessionActive, setSessionActive] = useState(false)
  const [topic, setTopic] = useState('')
  const [subject, setSubject] = useState('General')
  const [difficulty, setDifficulty] = useState(2)
  const [sessionId, setSessionId] = useState(null)
  const [currentStage, setCurrentStage] = useState(1)

  // Agents data for the teaching-first flow
  const [mentorData, setMentorData] = useState(null)
  const [creativeData, setCreativeData] = useState(null)
  const [challengerData, setChallengerData] = useState(null)

  // Stage 4 Question & Answer state
  const [currentQuestion, setCurrentQuestion] = useState('')
  const [studentAnswer, setStudentAnswer] = useState('')
  const [submittedAnswer, setSubmittedAnswer] = useState('')
  const [hasSubmitted, setHasSubmitted] = useState(false)

  // Stage 6 Targeted Practice state
  const [targetedAnswer, setTargetedAnswer] = useState('')
  const [submittedTargetedAnswer, setSubmittedTargetedAnswer] = useState('')
  const [targetedReview, setTargetedReview] = useState(null)

  // Review & Next Challenge outputs
  const [loading, setLoading] = useState(false)
  const [loadingStep, setLoadingStep] = useState('')
  const [agentMessages, setAgentMessages] = useState([])
  const [review, setReview] = useState(null)
  const [nextChallenge, setNextChallenge] = useState(null)
  const [masteryScore, setMasteryScore] = useState(70.0)
  const [knowledgeGaps, setKnowledgeGaps] = useState([])
  const [attempts, setAttempts] = useState(0)
  const [submitError, setSubmitError] = useState(null)

  // Initial session restoration & location state trigger
  useEffect(() => {
    if (location.state?.topic) {
      sessionStorage.removeItem('peerx_active_session')
      handleStartSession(location.state.topic, location.state.subject || 'General', 2)
    } else {
      const savedSession = sessionStorage.getItem('peerx_active_session')
      if (savedSession) {
        try {
          const parsed = JSON.parse(savedSession)
          if (parsed && parsed.topic) {
            setTopic(parsed.topic)
            setSubject(parsed.subject || 'General')
            setDifficulty(parsed.difficulty || 2)
            setSessionId(parsed.sessionId)
            setCurrentStage(parsed.currentStage || 1)
            setMentorData(parsed.mentorData)
            setCreativeData(parsed.creativeData)
            setChallengerData(parsed.challengerData)
            setCurrentQuestion(parsed.currentQuestion || '')
            setReview(parsed.review || null)
            setNextChallenge(parsed.nextChallenge || null)
            setSubmittedAnswer(parsed.submittedAnswer || '')
            setHasSubmitted(!!parsed.hasSubmitted)
            setTargetedAnswer(parsed.targetedAnswer || '')
            setSubmittedTargetedAnswer(parsed.submittedTargetedAnswer || '')
            setTargetedReview(parsed.targetedReview || null)
            setSessionActive(true)
          }
        } catch (e) {
          console.error('Failed to parse saved session from sessionStorage:', e)
        }
      }
    }
  }, [location.state])

  // Save active session state to sessionStorage
  useEffect(() => {
    if (sessionActive && topic) {
      sessionStorage.setItem('peerx_active_session', JSON.stringify({
        topic,
        subject,
        difficulty,
        sessionId,
        currentStage,
        mentorData,
        creativeData,
        challengerData,
        currentQuestion,
        review,
        nextChallenge,
        submittedAnswer,
        hasSubmitted,
        targetedAnswer,
        submittedTargetedAnswer,
        targetedReview
      }))
    }
  }, [
    sessionActive, topic, subject, difficulty, sessionId, currentStage,
    mentorData, creativeData, challengerData, currentQuestion, review,
    nextChallenge, submittedAnswer, hasSubmitted, targetedAnswer,
    submittedTargetedAnswer, targetedReview
  ])

  // Start teaching-first learning session
  const handleStartSession = async (overrideTopic, overrideSubject, overrideDifficulty) => {
    const activeTop = (overrideTopic || selectedTopic || '').trim()
    if (!activeTop) return

    const activeSub = overrideSubject || selectedSubject || 'General'
    const activeDiff = overrideDifficulty || selectedDifficulty || 2

    sessionStorage.removeItem('peerx_active_session')

    setTopic(activeTop)
    setSubject(activeSub)
    setDifficulty(activeDiff)
    setCurrentStage(1)

    setLoading(true)
    setLoadingStep(`Mentor AI teaching topic "${activeTop}" & Creative Peer preparing analogy...`)
    setAgentMessages([])
    setMentorData(null)
    setCreativeData(null)
    setChallengerData(null)
    setReview(null)
    setNextChallenge(null)
    setKnowledgeGaps([])
    setAttempts(0)
    setHasSubmitted(false)
    setSubmittedAnswer('')
    setStudentAnswer('')
    setTargetedAnswer('')
    setSubmittedTargetedAnswer('')
    setTargetedReview(null)
    setCurrentQuestion('')
    setSubmitError(null)
    setSessionActive(true)

    try {
      const res = await sessionAPI.startSession({
        topic: activeTop,
        subject: activeSub,
        difficulty: activeDiff
      })

      if (res.data) {
        const payload = res.data.data || res.data
        const generatedId = payload.session?.id || 'session-' + Date.now()
        setSessionId(generatedId)

        const mentor = payload.mentor || {
          agent: 'mentor',
          explanation: `Let's learn about ${activeTop} in ${activeSub}.`,
          example: `Practical application of ${activeTop} in ${activeSub}.`,
          key_takeaway: `Understanding ${activeTop} builds core competence in ${activeSub}.`
        }
        const creative = payload.creative
        const challenger = payload.challenger

        setMentorData(mentor)
        setCreativeData(creative)
        setChallengerData(challenger)

        const challengerQ = challenger?.question || `What is the core purpose of ${activeTop} in ${activeSub}, and why is it useful?`
        setCurrentQuestion(challengerQ)

        // Stage 1 Teaching active with Mentor content loaded
        setCurrentStage(1)

        const initialMsgs = []
        if (mentor) initialMsgs.push({ agentType: 'mentor', content: mentor })
        if (creative) initialMsgs.push({ agentType: 'creative', content: creative })
        if (challenger) initialMsgs.push({ agentType: 'challenger', content: challenger })

        setAgentMessages(initialMsgs)
      }
    } catch (err) {
      console.error('Backend API error starting session:', err)
      const fallbackMentor = {
        agent: 'mentor',
        explanation: `### Teaching ${activeTop}\nLet's understand ${activeTop} in ${activeSub}.\n\n### Core Concepts\n1. Definition and primary purpose of ${activeTop}.\n2. How it operates within ${activeSub}.\n3. Best practices for implementation.`,
        example: `Real-world application of ${activeTop} in ${activeSub}.`,
        key_takeaway: `Mastering ${activeTop} provides key structural understanding in ${activeSub}.`
      }
      setMentorData(fallbackMentor)
      setCreativeData({
        agent: 'creative',
        perspective: `Think of ${activeTop} like a modular building block in ${activeSub}!`,
        analogy: `Like a well-organized system where each component has a clear role.`
      })
      setChallengerData({
        agent: 'challenger',
        question: `What is the core purpose of ${activeTop} in ${activeSub}, and how would you apply it?`
      })
      setCurrentQuestion(`What is the core purpose of ${activeTop} in ${activeSub}, and how would you apply it?`)
      setCurrentStage(1)
    } finally {
      setLoading(false)
      setLoadingStep('')
    }
  }

  // Handle Change Topic
  const handleChangeTopic = () => {
    sessionStorage.removeItem('peerx_active_session')
    setSessionActive(false)
    setSelectedTopic('')
    setCurrentStage(1)
    setMentorData(null)
    setCreativeData(null)
    setChallengerData(null)
    setReview(null)
    setNextChallenge(null)
    setHasSubmitted(false)
    setSubmittedAnswer('')
    setStudentAnswer('')
    setTargetedAnswer('')
    setSubmittedTargetedAnswer('')
    setTargetedReview(null)
    setSubmitError(null)
  }

  // Handle Restart Topic
  const handleRestartTopic = () => {
    sessionStorage.removeItem('peerx_active_session')
    handleStartSession(topic, subject, difficulty)
  }

  // Submit student answer for Reviewer evaluation (Stage 4 -> Stage 5)
  const handleSubmitAnswer = async (e) => {
    if (e && e.preventDefault) e.preventDefault()
    if (!studentAnswer.trim() || loading) return

    setLoading(true)
    setLoadingStep('Argus (Reviewer AI) evaluating reasoning & Apex (Problem Solver) building targeted challenge...')
    setSubmitError(null)

    const userSubmission = studentAnswer
    setSubmittedAnswer(userSubmission)
    setHasSubmitted(true)

    const activeSessionId = sessionId || 'session-' + Date.now()

    console.log('Stage 4 submit started')
    console.log('Session ID:', activeSessionId)
    console.log('Topic:', topic)
    console.log('Answer received: YES')
    console.log('Reviewer request started')

    try {
      const res = await sessionAPI.submitAnswer(activeSessionId, {
        answer: userSubmission,
        question: currentQuestion
      })

      console.log('Reviewer response received: YES')

      if (res.data) {
        const payload = res.data.data || res.data
        const reviewData = payload.review || {
          score: 85,
          correctness: 'mostly_correct',
          reasoning_quality: 'good',
          strengths: [`Accurately explained key mechanics of ${topic}`],
          weaknesses: [`Can expand on advanced applications of ${topic}`],
          feedback: `Great explanation of ${topic}! You demonstrated clear understanding.`,
          recommended_difficulty: difficulty
        }

        console.log('Reviewer response valid: YES')
        console.log('Transitioning: Stage 4 -> Stage 5')

        setReview(reviewData)

        const challengeData = payload.next_challenge || {
          question: `Given a scenario involving ${topic}, how would you optimize execution or handle edge cases in ${subject}?`,
          difficulty: payload.updated_difficulty || difficulty,
          concept: topic,
          expected_skill: `Implement robust ${topic} strategies`
        }
        setNextChallenge(challengeData)

        if (payload.knowledge_gaps) setKnowledgeGaps(payload.knowledge_gaps)
        if (payload.progress?.mastery_score) {
          setMasteryScore(payload.progress.mastery_score)
        } else {
          setMasteryScore((prev) => Math.min(100, Math.round(prev + 5)))
        }

        if (payload.updated_difficulty) setDifficulty(payload.updated_difficulty)
        setAttempts((prev) => prev + 1)

        // STAGE TRANSITION: Stage 4 -> Stage 5 (Review)
        setCurrentStage(5)
      }
    } catch (err) {
      console.error('Stage 4 submit error:', err)
      console.log('Reviewer response received: NO')
      setSubmitError('Unable to review your answer. Please try again.')
    } finally {
      setLoading(false)
      setLoadingStep('')
    }
  }

  // Move from Stage 5 (Review) to Stage 6 (Targeted Practice)
  const handleProceedToStage6 = () => {
    console.log('Transitioning: Stage 5 -> Stage 6')
    setCurrentStage(6)
  }

  // Submit Targeted Practice Answer (Stage 6 -> Stage 7)
  const handleTargetedAnswerSubmit = async (e) => {
    if (e && e.preventDefault) e.preventDefault()
    if (!targetedAnswer.trim() || loading) return

    setLoading(true)
    setLoadingStep('Evaluating targeted practice answer & calculating updated mastery...')
    setSubmitError(null)

    const userSubmission = targetedAnswer
    setSubmittedTargetedAnswer(userSubmission)

    const activeSessionId = sessionId || 'session-' + Date.now()
    const questionText = nextChallenge?.question || currentQuestion

    try {
      const res = await sessionAPI.submitAnswer(activeSessionId, {
        answer: userSubmission,
        question: questionText
      })

      if (res.data) {
        const payload = res.data.data || res.data
        if (payload.review) setTargetedReview(payload.review)
        if (payload.knowledge_gaps) setKnowledgeGaps(payload.knowledge_gaps)
        if (payload.progress?.mastery_score) {
          setMasteryScore(payload.progress.mastery_score)
        } else {
          setMasteryScore((prev) => Math.min(100, Math.round(prev + 8)))
        }

        if (payload.updated_difficulty) setDifficulty(payload.updated_difficulty)
        setAttempts((prev) => prev + 1)

        console.log('Transitioning: Stage 6 -> Stage 7')
        // STAGE TRANSITION: Stage 6 -> Stage 7 (Progress)
        setCurrentStage(7)
      }
    } catch (err) {
      console.error('Stage 6 submit error:', err)
      setSubmitError('Unable to review your answer. Please try again.')
    } finally {
      setLoading(false)
      setLoadingStep('')
    }
  }

  // Individual peer agent prompt handler
  const handlePromptAgent = async (agentType) => {
    setLoading(true)
    setLoadingStep(`Consulting ${agentType.toUpperCase()} Agent...`)
    try {
      const res = await sessionAPI.getAgentResponse(sessionId || 'session-123', agentType, `Elaborate more on ${topic}`)
      if (res.data) {
        const payload = res.data.data || res.data
        const contentVal = payload.message || payload.explanation || payload.question || payload.perspective || payload
        setAgentMessages((prev) => [{
          agentType: agentType,
          content: contentVal
        }, ...prev])
      }
    } catch (err) {
      setAgentMessages((prev) => [{
        agentType: agentType,
        content: `Direct response from ${agentType.toUpperCase()} Agent on ${topic}: Focus on solidifying core principles before moving to edge cases!`
      }, ...prev])
    } finally {
      setLoading(false)
      setLoadingStep('')
    }
  }

  const getStageName = (stage) => {
    switch (stage) {
      case 1: return 'Teaching'
      case 2: return 'Reinforcement'
      case 3: return 'Challenge'
      case 4: return 'Student Answer'
      case 5: return 'Review'
      case 6: return 'Targeted Practice'
      case 7: return 'Progress'
      default: return 'Teaching'
    }
  }

  return (
    <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '32px 24px' }}>
      {/* ── TOPIC SELECTION SCREEN (When session is NOT active) ── */}
      {!sessionActive ? (
        <div style={{ maxWidth: '720px', margin: '20px auto' }}>
          <div className="glass-card" style={{ padding: '36px', borderTop: '4px solid #0284c7' }}>
            <div style={{ textAlign: 'center', marginBottom: '28px' }}>
              <div style={{
                width: '56px',
                height: '56px',
                borderRadius: '16px',
                background: 'linear-gradient(135deg, #0284c7 0%, #7e22ce 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px auto',
                boxShadow: '0 4px 15px rgba(2, 132, 199, 0.25)'
              }}>
                <Compass size={30} color="#ffffff" />
              </div>
              <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                Start Adaptive Learning Session
              </h1>
              <p style={{ color: '#64748b', fontSize: '0.95rem', marginTop: '6px' }}>
                Select or type any topic. Mentor AI will teach first, Creative Peer will reinforce with analogies, and Challenger AI will test your reasoning!
              </p>
            </div>

            <form onSubmit={(e) => { e.preventDefault(); handleStartSession(); }} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
                  What do you want to learn today?
                </label>
                <input
                  type="text"
                  required
                  className="input-field"
                  placeholder="e.g., Python Functions, DBMS Normalization, Machine Learning..."
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                  style={{ fontSize: '1rem', padding: '14px 18px' }}
                />
              </div>

              {/* Sample Topic Pills */}
              <div>
                <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 600, display: 'block', marginBottom: '8px' }}>
                  Or pick a popular topic:
                </span>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {SAMPLE_TOPICS.map((item, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => {
                        setSelectedTopic(item.topic)
                        setSelectedSubject(item.subject)
                        setSelectedDifficulty(item.difficulty)
                      }}
                      style={{
                        background: selectedTopic === item.topic ? '#e0f2fe' : '#ffffff',
                        border: selectedTopic === item.topic ? '1px solid #0284c7' : '1px solid #cbd5e1',
                        color: selectedTopic === item.topic ? '#0284c7' : '#334155',
                        padding: '6px 14px',
                        borderRadius: '20px',
                        fontSize: '0.82rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                    >
                      {item.subject} → {item.topic}
                    </button>
                  ))}
                </div>
              </div>

              {/* Subject & Difficulty Selector */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
                    Subject / Domain
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    placeholder="General"
                    value={selectedSubject}
                    onChange={(e) => setSelectedSubject(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#334155', marginBottom: '6px' }}>
                    Starting Difficulty
                  </label>
                  <select
                    className="input-field"
                    value={selectedDifficulty}
                    onChange={(e) => setSelectedDifficulty(Number(e.target.value))}
                  >
                    <option value={1}>Level 1 — Beginner</option>
                    <option value={2}>Level 2 — Easy</option>
                    <option value={3}>Level 3 — Intermediate</option>
                    <option value={4}>Level 4 — Advanced</option>
                    <option value={5}>Level 5 — Expert</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={!selectedTopic.trim()}
                className="btn-primary"
                style={{ justifyContent: 'center', padding: '14px', fontSize: '1rem', marginTop: '10px' }}
              >
                <span>Start Teaching-First Learning</span>
                <ArrowRight size={18} />
              </button>
            </form>
          </div>
        </div>
      ) : (
        /* ── ACTIVE STUDY ROOM UI ── */
        <>
          {/* Header & Controls */}
          <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="badge" style={{ background: '#e0f2fe', color: '#0284c7', border: '1px solid #bae6fd' }}>
                    Stage {currentStage}: {getStageName(currentStage)}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    Subject: <strong style={{ color: '#0f172a' }}>{subject}</strong>
                  </span>
                </div>
                <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', marginTop: '4px' }}>
                  Learning: {topic}
                </h1>
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={handleChangeTopic}
                  className="btn-secondary"
                  style={{ padding: '8px 16px', fontSize: '0.85rem' }}
                >
                  Change Topic
                </button>
                <button
                  onClick={handleRestartTopic}
                  className="btn-primary"
                  style={{ padding: '8px 16px', fontSize: '0.85rem' }}
                >
                  <RefreshCw size={16} />
                  Restart Topic
                </button>
              </div>
            </div>

            {/* Visual Learning Stage Tracker (7 Stages) */}
            <div style={{
              marginTop: '20px',
              paddingTop: '16px',
              borderTop: '1px solid #e2e8f0',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              overflowX: 'auto',
              paddingBottom: '4px'
            }}>
              {[
                { stageNum: 1, label: '📚 Stage 1: Teaching', color: '#059669' },
                { stageNum: 2, label: '💡 Stage 2: Reinforcement', color: '#d97706' },
                { stageNum: 3, label: '🧠 Stage 3: Challenge', color: '#7e22ce' },
                { stageNum: 4, label: '✍️ Stage 4: Student Answer', color: '#0284c7' },
                { stageNum: 5, label: '🔍 Stage 5: Review', color: '#2563eb' },
                { stageNum: 6, label: '🎯 Stage 6: Targeted Practice', color: '#dc2626' },
                { stageNum: 7, label: '📈 Stage 7: Progress', color: '#059669' }
              ].map((stageItem, idx) => {
                const isCurrent = currentStage === stageItem.stageNum
                const isCompleted = currentStage > stageItem.stageNum
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      if (stageItem.stageNum <= Math.max(currentStage, 4)) {
                        setCurrentStage(stageItem.stageNum)
                      }
                    }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px',
                      background: isCurrent ? `${stageItem.color}25` : isCompleted ? `${stageItem.color}10` : '#f1f5f9',
                      border: isCurrent ? `2px solid ${stageItem.color}` : isCompleted ? `1px solid ${stageItem.color}50` : '1px solid #cbd5e1',
                      color: isCurrent || isCompleted ? stageItem.color : '#94a3b8',
                      padding: '6px 14px',
                      borderRadius: '20px',
                      fontSize: '0.78rem',
                      fontWeight: isCurrent ? 800 : 600,
                      whiteSpace: 'nowrap',
                      cursor: stageItem.stageNum <= Math.max(currentStage, 4) ? 'pointer' : 'default',
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <span>{stageItem.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Main Content Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '24px' }}>
            {/* Left Column: Stage Views */}
            <div>
              {/* AI Processing Indicator */}
              {loading && <LoadingAI message={loadingStep || `Processing AI peer swarm for ${topic}...`} />}

              {/* Global Error Banner with Retry */}
              {submitError && (
                <div style={{
                  padding: '14px 18px',
                  background: '#fef2f2',
                  border: '1px solid #fca5a5',
                  borderRadius: '10px',
                  color: '#991b1b',
                  fontSize: '0.9rem',
                  marginBottom: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  boxShadow: '0 2px 8px rgba(220,38,38,0.1)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertCircle size={20} color="#dc2626" />
                    <span>{submitError}</span>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      if (currentStage === 4) handleSubmitAnswer(e)
                      else if (currentStage === 6) handleTargetedAnswerSubmit(e)
                    }}
                    style={{
                      background: '#dc2626',
                      color: '#ffffff',
                      border: 'none',
                      padding: '6px 14px',
                      borderRadius: '6px',
                      fontSize: '0.82rem',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    Retry
                  </button>
                </div>
              )}

              {/* ── STAGE 1: 📚 TEACHING (Mentor Agent) ── */}
              {mentorData && (
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: '#059669', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <GraduationCap size={18} />
                    Stage 1: 📚 Teaching (Mentor Sophia)
                  </div>
                  <AgentCard
                    agentType="mentor"
                    content={mentorData}
                    onPromptAgent={handlePromptAgent}
                  />

                  {currentStage === 1 && (
                    <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                      <button
                        type="button"
                        onClick={() => {
                          console.log('Transitioning: Stage 1 -> Stage 2')
                          setCurrentStage(2)
                        }}
                        className="btn-primary"
                      >
                        <span>Continue to Stage 2: Reinforcement</span>
                        <ArrowRight size={16} />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* ── STAGE 2: 💡 REINFORCEMENT (Creative Peer Agent) ── */}
              {(currentStage >= 2 || creativeData) && creativeData && (
                <div style={{ marginBottom: '20px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: '#d97706', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Lightbulb size={18} />
                    Stage 2: 💡 Reinforcement (Creative Peer Nova)
                  </div>
                  <AgentCard
                    agentType="creative"
                    content={creativeData}
                    onPromptAgent={handlePromptAgent}
                  />

                  {currentStage === 2 && (
                    <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                      <button
                        type="button"
                        onClick={() => {
                          console.log('Transitioning: Stage 2 -> Stage 3')
                          setCurrentStage(3)
                        }}
                        className="btn-primary"
                      >
                        <span>Continue to Stage 3: Challenge</span>
                        <ArrowRight size={16} />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* ── STAGE 3: 🧠 CHALLENGE (Challenger Agent) ── */}
              {(currentStage >= 3 || currentQuestion) && currentQuestion && (
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: '#7e22ce', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Zap size={18} />
                    Stage 3: 🧠 Challenge (Challenger Ares)
                  </div>
                  <div className="glass-card" style={{ padding: '24px', borderLeft: '4px solid #7e22ce', background: '#ffffff' }}>
                    <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#7e22ce', fontWeight: 700, marginBottom: '6px' }}>
                      Assessment Question (Based on Taught Topic)
                    </div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', lineHeight: 1.5, margin: 0 }}>
                      {currentQuestion}
                    </h3>
                  </div>

                  {currentStage === 3 && (
                    <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                      <button
                        type="button"
                        onClick={() => {
                          console.log('Transitioning: Stage 3 -> Stage 4')
                          setCurrentStage(4)
                        }}
                        className="btn-primary"
                      >
                        <span>Proceed to Stage 4: Enter Answer</span>
                        <ArrowRight size={16} />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* ── STAGE 4: ✍️ STUDENT ANSWER ── */}
              {currentStage >= 4 && (
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: '#0284c7', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <BookOpen size={18} />
                    Stage 4: ✍️ Student Answer
                  </div>
                  <form onSubmit={handleSubmitAnswer} className="glass-card" style={{ padding: '20px', background: '#ffffff' }}>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '8px' }}>
                      Type your answer to Challenger Ares's question:
                    </label>
                    <textarea
                      className="input-field"
                      rows={4}
                      placeholder={`Explain your answer on ${topic} in detail...`}
                      value={studentAnswer}
                      onChange={(e) => setStudentAnswer(e.target.value)}
                      disabled={currentStage > 4 && hasSubmitted}
                      style={{ resize: 'vertical', marginBottom: '14px', fontFamily: 'inherit' }}
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        Tip: Explaining "why" and "how" helps Reviewer Argus evaluate reasoning quality.
                      </span>
                      {currentStage <= 4 && (
                        <button
                          type="submit"
                          disabled={loading || !studentAnswer.trim()}
                          className="btn-primary"
                        >
                          <Send size={16} />
                          <span>Submit Answer for Review</span>
                        </button>
                      )}
                    </div>
                  </form>

                  {submittedAnswer && (
                    <div style={{ marginTop: '12px', padding: '12px 16px', background: '#f1f5f9', borderRadius: '8px', borderLeft: '3px solid #0284c7', fontSize: '0.88rem', color: '#334155' }}>
                      <strong>Submitted Stage 4 Answer:</strong> {submittedAnswer}
                    </div>
                  )}
                </div>
              )}

              {/* ── STAGE 5: 🔍 REVIEW (Reviewer Evaluation & Knowledge Gaps) ── */}
              {currentStage >= 5 && review && (
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: '#2563eb', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <CheckCircle2 size={18} />
                    Stage 5: 🔍 Reviewer Evaluation (Argus)
                  </div>
                  <ScoreCard review={review} />

                  {currentStage === 5 && (
                    <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                      <button
                        type="button"
                        onClick={handleProceedToStage6}
                        className="btn-primary"
                        style={{ padding: '12px 20px', fontSize: '0.95rem' }}
                      >
                        <Sparkles size={18} />
                        <span>Continue to Stage 6: Targeted Practice</span>
                        <ArrowRight size={18} />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* ── STAGE 6: 🎯 TARGETED PRACTICE (Problem Solver Apex) ── */}
              {currentStage >= 6 && nextChallenge && (
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: '#dc2626', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <ShieldAlert size={18} />
                    Stage 6: 🎯 Targeted Practice (Problem Solver Apex)
                  </div>
                  <ChallengeCard challenge={nextChallenge} />

                  {/* Targeted Answer Submission Form */}
                  <form onSubmit={handleTargetedAnswerSubmit} className="glass-card" style={{ padding: '20px', background: '#ffffff', marginTop: '16px', borderTop: '3px solid #dc2626' }}>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '8px' }}>
                      Your Answer to Targeted Practice Question:
                    </label>
                    <textarea
                      className="input-field"
                      rows={4}
                      placeholder={`Demonstrate your understanding of ${nextChallenge?.concept || topic}...`}
                      value={targetedAnswer}
                      onChange={(e) => setTargetedAnswer(e.target.value)}
                      disabled={currentStage > 6}
                      style={{ resize: 'vertical', marginBottom: '14px', fontFamily: 'inherit' }}
                    />
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        Solve the gap challenge to complete topic mastery!
                      </span>
                      {currentStage <= 6 && (
                        <button
                          type="submit"
                          disabled={loading || !targetedAnswer.trim()}
                          className="btn-primary"
                          style={{ background: 'linear-gradient(135deg, #dc2626 0%, #b91c1c 100%)' }}
                        >
                          <Send size={16} />
                          <span>Submit Targeted Answer for Final Review</span>
                        </button>
                      )}
                    </div>
                  </form>

                  {submittedTargetedAnswer && (
                    <div style={{ marginTop: '12px', padding: '12px 16px', background: '#fef2f2', borderRadius: '8px', borderLeft: '3px solid #dc2626', fontSize: '0.88rem', color: '#334155' }}>
                      <strong>Submitted Targeted Practice Answer:</strong> {submittedTargetedAnswer}
                    </div>
                  )}
                </div>
              )}

              {/* ── STAGE 7: 📈 PROGRESS ── */}
              {currentStage >= 7 && (
                <div style={{ marginBottom: '24px' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 800, textTransform: 'uppercase', color: '#059669', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <CheckCircle2 size={18} />
                    Stage 7: 📈 Mastery & Learning Progress
                  </div>
                  {targetedReview && <ScoreCard review={targetedReview} />}
                  <div className="glass-card" style={{ padding: '24px', background: '#ecfdf5', border: '1px solid #a7f3d0' }}>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#065f46', margin: '0 0 10px 0' }}>
                      🎉 Session Stage Flow Completed!
                    </h3>
                    <p style={{ color: '#047857', fontSize: '0.92rem', marginBottom: '16px', lineHeight: 1.5 }}>
                      You successfully progressed through all 7 stages for <strong>{topic}</strong>! Your mastery score is updated to <strong>{masteryScore}%</strong>.
                    </p>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <button onClick={handleRestartTopic} className="btn-primary" style={{ padding: '10px 18px' }}>
                        <RefreshCw size={16} />
                        Restart Topic Session
                      </button>
                      <button onClick={handleChangeTopic} className="btn-secondary" style={{ padding: '10px 18px' }}>
                        Start New Topic
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Additional Agent Feed Interactions */}
              {agentMessages.length > 3 && (
                <div style={{ marginTop: '32px' }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Layers size={18} color="#7e22ce" />
                    Additional Agent Discussion History
                  </h3>
                  {agentMessages.slice(3).map((msg, i) => (
                    <AgentCard
                      key={i}
                      agentType={msg.agentType}
                      content={msg.content}
                      onPromptAgent={handlePromptAgent}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Right Column: Progress Sidebar */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <ProgressCard
                topic={topic}
                masteryScore={masteryScore}
                questionsAttempted={attempts}
                currentDifficulty={difficulty}
                gaps={knowledgeGaps}
              />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
