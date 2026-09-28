import React, { createContext, useContext, useState, useEffect } from 'react'
import { supabase } from '../services/supabase'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check initial auth session
    const initAuth = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        if (session?.user) {
          setUser(session.user)
          localStorage.setItem('peerx_token', session.access_token)
        } else {
          // Check for demo guest mode in localStorage
          const savedGuest = localStorage.getItem('peerx_demo_user')
          if (savedGuest) {
            setUser(JSON.parse(savedGuest))
          } else {
            // Default demo user for instant hackathon demonstration
            const demoUser = {
              id: 'demo-student-001',
              email: 'alex.student@peerx.ai',
              user_metadata: {
                full_name: 'Alex Rivera',
                college: 'Stanford Computer Science',
                education_level: 'undergraduate'
              }
            }
            setUser(demoUser)
            localStorage.setItem('peerx_demo_user', JSON.stringify(demoUser))
          }
        }
      } catch (err) {
        console.warn('Supabase auth fallback:', err)
      } finally {
        setLoading(false)
      }
    }

    initAuth()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        setUser(session.user)
        localStorage.setItem('peerx_token', session.access_token)
      }
    })

    return () => subscription?.unsubscribe()
  }, [])

  const login = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    if (data?.session) {
      setUser(data.user)
      localStorage.setItem('peerx_token', data.session.access_token)
    }
    return data
  }

  const register = async (email, password, metadata = {}) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: metadata }
    })
    if (error) throw error
    return data
  }

  const logout = async () => {
    await supabase.auth.signOut()
    localStorage.removeItem('peerx_token')
    localStorage.removeItem('peerx_demo_user')
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
