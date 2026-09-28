-- ============================================================
-- PeerX Database Schema
-- Run this in the Supabase SQL Editor
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. PROFILES
-- ============================================================
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    education_level TEXT DEFAULT 'undergraduate',
    preferred_subject TEXT,
    learning_goal TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================
-- 2. LEARNING SESSIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS learning_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    subject TEXT NOT NULL,
    difficulty INTEGER DEFAULT 1 CHECK (difficulty BETWEEN 1 AND 5),
    goal TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused')),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON learning_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON learning_sessions(status);

-- ============================================================
-- 3. LEARNING ATTEMPTS
-- ============================================================
CREATE TABLE IF NOT EXISTS learning_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    student_answer TEXT,
    score INTEGER CHECK (score BETWEEN 0 AND 100),
    correctness TEXT CHECK (correctness IN ('correct', 'mostly_correct', 'partially_correct', 'incorrect')),
    reasoning_quality TEXT CHECK (reasoning_quality IN ('excellent', 'good', 'fair', 'poor')),
    feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_attempts_session ON learning_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_attempts_user ON learning_attempts(user_id);

-- ============================================================
-- 4. KNOWLEDGE GAPS
-- ============================================================
CREATE TABLE IF NOT EXISTS knowledge_gaps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    session_id UUID REFERENCES learning_sessions(id) ON DELETE SET NULL,
    topic TEXT NOT NULL,
    concept TEXT NOT NULL,
    severity TEXT DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'improving', 'resolved')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gaps_user ON knowledge_gaps(user_id);
CREATE INDEX IF NOT EXISTS idx_gaps_status ON knowledge_gaps(status);

-- ============================================================
-- 5. LEARNING PROGRESS
-- ============================================================
CREATE TABLE IF NOT EXISTS learning_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    questions_attempted INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    accuracy REAL DEFAULT 0.0,
    mastery_score REAL DEFAULT 0.0,
    current_difficulty INTEGER DEFAULT 1 CHECK (current_difficulty BETWEEN 1 AND 5),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, topic)
);

CREATE INDEX IF NOT EXISTS idx_progress_user ON learning_progress(user_id);

-- ============================================================
-- 6. AI INTERACTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS ai_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    agent_type TEXT NOT NULL CHECK (agent_type IN ('mentor', 'challenger', 'creative', 'reviewer', 'problem_solver')),
    input_context TEXT,
    output TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_interactions_session ON ai_interactions(session_id);

-- ============================================================
-- 7. CHALLENGES
-- ============================================================
CREATE TABLE IF NOT EXISTS challenges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    concept TEXT,
    difficulty INTEGER DEFAULT 1 CHECK (difficulty BETWEEN 1 AND 5),
    question TEXT NOT NULL,
    expected_skill TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_challenges_session ON challenges(session_id);
CREATE INDEX IF NOT EXISTS idx_challenges_user ON challenges(user_id);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE challenges ENABLE ROW LEVEL SECURITY;

-- PROFILES policies
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- LEARNING SESSIONS policies
CREATE POLICY "Users can view own sessions" ON learning_sessions
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own sessions" ON learning_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own sessions" ON learning_sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- LEARNING ATTEMPTS policies
CREATE POLICY "Users can view own attempts" ON learning_attempts
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own attempts" ON learning_attempts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- KNOWLEDGE GAPS policies
CREATE POLICY "Users can view own gaps" ON knowledge_gaps
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own gaps" ON knowledge_gaps
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own gaps" ON knowledge_gaps
    FOR UPDATE USING (auth.uid() = user_id);

-- LEARNING PROGRESS policies
CREATE POLICY "Users can view own progress" ON learning_progress
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own progress" ON learning_progress
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own progress" ON learning_progress
    FOR UPDATE USING (auth.uid() = user_id);

-- AI INTERACTIONS policies (access via session ownership)
CREATE POLICY "Users can view own interactions" ON ai_interactions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM learning_sessions
            WHERE learning_sessions.id = ai_interactions.session_id
            AND learning_sessions.user_id = auth.uid()
        )
    );
CREATE POLICY "Users can create interactions for own sessions" ON ai_interactions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM learning_sessions
            WHERE learning_sessions.id = ai_interactions.session_id
            AND learning_sessions.user_id = auth.uid()
        )
    );

-- CHALLENGES policies
CREATE POLICY "Users can view own challenges" ON challenges
    FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create own challenges" ON challenges
    FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own challenges" ON challenges
    FOR UPDATE USING (auth.uid() = user_id);
