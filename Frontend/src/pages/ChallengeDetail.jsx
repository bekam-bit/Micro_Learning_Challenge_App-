import { useEffect, useState } from 'react'
import { fetchChallenge, submitAttempt, fetchMySubmissions } from '../api/challenges'
import { useParams, Link, useNavigate } from 'react-router'

export default function ChallengeDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [challenge, setChallenge] = useState(null)
  const [loading, setLoading] = useState(true)
  const [answers, setAnswers] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [hasSubmitted, setHasSubmitted] = useState(false)
  const [timeLeft, setTimeLeft] = useState(null) // Seconds remaining
  const [timerStarted, setTimerStarted] = useState(false)
  const [timeExpired, setTimeExpired] = useState(false)
  const [clockOffset, setClockOffset] = useState(0) // Server time - client time offset
  const [validationError, setValidationError] = useState('')
  const [validationAttempted, setValidationAttempted] = useState(false)

  const isQuestionAnswered = (question, answer) => {
    if (answer === undefined || answer === null) return false

    if (question.question_type === 'single_choice') {
      return typeof answer === 'string' && answer.trim() !== ''
    }

    if (question.question_type === 'multiple_choice') {
      return Array.isArray(answer) && answer.length > 0
    }

    if (question.question_type === 'true_false') {
      return answer === 'true' || answer === 'false'
    }

    if (question.question_type === 'numeric') {
      if (typeof answer === 'number') return !isNaN(answer)
      return typeof answer === 'string' && answer.trim() !== '' && !isNaN(Number(answer))
    }

    return typeof answer === 'string' && answer.trim() !== ''
  }

  useEffect(() => {
    // Warn user before leaving page
    const handleBeforeUnload = (e) => {
      if (!result && !hasSubmitted && timerStarted) {
        e.preventDefault()
        e.returnValue = 'You have an active challenge. Your answers may be lost if you leave.'
        return e.returnValue
      }
    }

    // Handle tab visibility change - recalculate time when tab becomes active
    const handleVisibilityChange = () => {
      if (!document.hidden && challenge && challenge.has_active_attempt && challenge.attempt_deadline) {
        // Tab became visible - recalculate time from deadline
        const deadline = new Date(challenge.attempt_deadline).getTime()
        const now = Date.now() + clockOffset
        const remainingSeconds = Math.max(0, Math.floor((deadline - now) / 1000))
        
        console.log('Tab became active. Recalculating time:', {
          deadline: new Date(deadline).toISOString(),
          now: new Date(now).toISOString(),
          remainingSeconds
        })
        
        setTimeLeft(remainingSeconds)
        
        // If time expired while user was away, auto-submit
        if (remainingSeconds === 0 && !result && !hasSubmitted) {
          console.log('Time expired while away. Auto-submitting...')
          setTimeExpired(true)
          setTimeout(() => {
            onSubmit()
          }, 1000)
        }
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    document.addEventListener('visibilitychange', handleVisibilityChange)
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [result, hasSubmitted, timerStarted, challenge, clockOffset])

  useEffect(() => {
    // Load challenge details
    fetchChallenge(id)
      .then((data) => {
        setChallenge(data)
        setLoading(false)
        
        // Restore saved answers from localStorage if available
        try {
          const savedAnswers = localStorage.getItem(`challenge_answers_${id}`)
          if (savedAnswers) {
            const parsedAnswers = JSON.parse(savedAnswers)
            setAnswers(parsedAnswers)
            console.log('Restored saved answers from localStorage')
          }
        } catch (e) {
          console.error('Failed to restore saved answers:', e)
        }
        
        // Calculate clock offset for synchronization
        if (data.server_time) {
          const serverTime = new Date(data.server_time).getTime()
          const clientTime = Date.now()
          const offset = serverTime - clientTime
          setClockOffset(offset)
          console.log(`Clock offset: ${offset}ms (server ${offset > 0 ? 'ahead' : 'behind'})`)
        }
        
        // Check if user has active attempt with deadline
        if (data.has_active_attempt && data.attempt_deadline) {
          // Calculate remaining time from deadline using server time
          const deadline = new Date(data.attempt_deadline).getTime()
          const now = Date.now() + (data.server_time ? (new Date(data.server_time).getTime() - Date.now()) : 0)
          const remainingSeconds = Math.max(0, Math.floor((deadline - now) / 1000))
          
          if (remainingSeconds > 0) {
            setTimeLeft(remainingSeconds)
            setTimerStarted(true)
          } else {
            // Time already expired!
            console.log('Challenge time expired. Auto-submitting...')
            setTimeExpired(true)
            setTimeLeft(0)
            setTimerStarted(true)
            
            // Auto-submit after a brief moment
            setTimeout(() => {
              onSubmit()
            }, 1000)
          }
        } else if (data.time_limit_minutes) {
          // New attempt - initialize with full time
          const totalSeconds = data.time_limit_minutes * 60
          setTimeLeft(totalSeconds)
          setTimerStarted(true)
        }
        
        // Check if user has already submitted this challenge
        fetchMySubmissions(id)
          .then((submissionData) => {
            if (submissionData.results && submissionData.results.length > 0) {
              setHasSubmitted(true)
              // Clear saved answers since challenge is completed
              localStorage.removeItem(`challenge_answers_${id}`)
              // Redirect to submissions page after a short delay
              setTimeout(() => {
                navigate('/submissions', { 
                  state: { message: 'This challenge has already been completed. View your submission below.' }
                })
              }, 2000)
            }
          })
          .catch(() => {
            // Ignore errors - user just hasn't submitted
          })
      })
      .catch((err) => {
        console.error('Error loading challenge:', err)
        setLoading(false)
      })
  }, [id, navigate])

  // Countdown timer effect
  useEffect(() => {
    if (!timerStarted || timeLeft === null || timeLeft <= 0 || result || hasSubmitted) {
      return
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          // Time's up! Auto-submit
          clearInterval(timer)
          onSubmit()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [timerStarted, timeLeft, result, hasSubmitted])

  // Periodically save answers to localStorage (every 10 seconds)
  useEffect(() => {
    if (!challenge || result || hasSubmitted || Object.keys(answers).length === 0) {
      return
    }

    const saveInterval = setInterval(() => {
      try {
        localStorage.setItem(`challenge_answers_${challenge.id}`, JSON.stringify(answers))
        console.log('Auto-saved answers to localStorage')
      } catch (e) {
        console.error('Failed to auto-save answers:', e)
      }
    }, 10000) // Save every 10 seconds

    return () => clearInterval(saveInterval)
  }, [challenge, answers, result, hasSubmitted])

  // Format time as MM:SS
  const formatTime = (seconds) => {
    if (seconds === null) return '--:--'
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
  }

  // Determine timer color based on remaining time
  const getTimerColor = () => {
    if (timeLeft === null) return 'text-slate-400'
    const totalTime = challenge?.time_limit_minutes * 60 || 0
    const percentage = (timeLeft / totalTime) * 100
    
    if (percentage <= 10) return 'text-red-400'  // Last 10% - red
    if (percentage <= 25) return 'text-amber-400' // Last 25% - amber
    return 'text-sky-400' // Normal - sky blue
  }

  // Format time in user-friendly way
  const formatTimeUserFriendly = (seconds) => {
    if (!seconds || seconds === 0) return '0s'
    
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    const parts = []
    if (hours > 0) parts.push(`${hours}h`)
    if (minutes > 0) parts.push(`${minutes}m`)
    if (secs > 0 || parts.length === 0) parts.push(`${secs}s`)
    
    return parts.join(' ')
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto w-full p-8 bg-slate-900/60 border border-slate-800 rounded-3xl animate-pulse space-y-6">
        <div className="h-6 w-32 bg-slate-800 rounded"></div>
        <div className="h-10 w-3/4 bg-slate-800 rounded"></div>
        <div className="h-4 w-full bg-slate-800 rounded"></div>
        <div className="space-y-4 pt-6">
          <div className="h-24 bg-slate-800/60 rounded-2xl"></div>
          <div className="h-24 bg-slate-800/60 rounded-2xl"></div>
        </div>
      </div>
    )
  }

  if (!challenge) {
    return (
      <div className="max-w-md mx-auto w-full text-center py-12 px-6 bg-slate-900/70 border border-slate-800 rounded-3xl space-y-4">
        <span className="text-4xl">🔍</span>
        <h2 className="text-xl font-bold text-white">Challenge Not Found</h2>
        <p className="text-slate-400 text-sm">The requested challenge could not be loaded or doesn't exist.</p>
        <Link
          to="/challenges"
          className="inline-block px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-xl border border-slate-700 transition-all"
        >
          ← Back to Challenges
        </Link>
      </div>
    )
  }

  const onChangeSingle = (questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }))
  }

  const onChangeMultiple = (questionId, optionLabel, checked) => {
    setAnswers((prev) => {
      const current = prev[questionId] || []
      const newValue = checked
        ? [...current, optionLabel]
        : current.filter((label) => label !== optionLabel)
      return { ...prev, [questionId]: newValue }
    })
  }

  const onSubmit = async () => {
    setValidationError('')

    // Validate answers before manual submission (bypass validation if time expired to allow auto-submit)
    if (!timeExpired && challenge?.questions && challenge.questions.length > 0) {
      const unansweredQuestions = challenge.questions.filter((q) => !isQuestionAnswered(q, answers[q.id]))

      if (unansweredQuestions.length > 0) {
        setValidationAttempted(true)
        const unansweredIndices = unansweredQuestions.map((q) => {
          const idx = challenge.questions.findIndex((item) => item.id === q.id)
          return `Question #${idx + 1}`
        })

        const errorMsg = `Please answer all questions before submitting. Unanswered: ${unansweredIndices.join(', ')}.`
        setValidationError(errorMsg)

        // Smooth scroll to the first unanswered question
        const firstUnansweredId = unansweredQuestions[0].id
        setTimeout(() => {
          const el = document.getElementById(`question-${firstUnansweredId}`)
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' })
          }
        }, 100)

        return
      }
    }

    setSubmitting(true)
    try {
      const answersArray = challenge.questions.map((q) => {
        const answer = answers[q.id] || ''
        
        if (q.question_type === 'multiple_choice') {
          return {
            question_id: q.id,
            answer_options: Array.isArray(answer) ? answer : [],
          }
        }
        
        if (q.question_type === 'single_choice') {
          return {
            question_id: q.id,
            answer_text: answer,
          }
        }
        
        if (q.question_type === 'true_false') {
          return {
            question_id: q.id,
            answer_boolean: answer === 'true',
          }
        }
        
        if (q.question_type === 'numeric') {
          return {
            question_id: q.id,
            answer_number: parseFloat(answer) || 0,
          }
        }
        
        return {
          question_id: q.id,
          answer_text: answer,
        }
      })

      console.log('Submitting answers:', answersArray)

      const payload = { answers: answersArray }
      const idempotencyKey = `attempt-${id}-${Date.now()}`
      const res = await submitAttempt(challenge.id, payload, idempotencyKey)
      
      console.log('Submission successful:', res)
      console.log('Does res have results?', res.results)
      console.log('Type of res:', typeof res)
      console.log('Keys in res:', Object.keys(res))
      
      // Store the full result in localStorage for persistence
      try {
        localStorage.setItem(`challenge_result_${challenge.id}`, JSON.stringify(res))
      } catch (e) {
        console.error('Failed to save result to localStorage:', e)
      }
      
      setResult(res)
    } catch (err) {
      console.error('Submission error:', err)
      console.error('Error response:', err.response?.data)
      
      // Check if it's a session timeout error
      if (err.response?.status === 401) {
        alert('Your session has expired. Please login again. Your answers have been saved locally and you can retry after logging in.')
        // Save answers to localStorage before redirect
        try {
          localStorage.setItem(`challenge_answers_${challenge.id}`, JSON.stringify(answers))
        } catch (e) {
          console.error('Failed to save answers:', e)
        }
        navigate('/login?session_expired=true')
        return
      }
      
      const errorMessage = err.response?.data?.detail 
        || err.response?.data?.message
        || JSON.stringify(err.response?.data)
        || err.message
        || 'Unknown error occurred'
      
      alert(`Submission failed: ${errorMessage}`)
    } finally {
      setSubmitting(false)
    }
  }

  const renderQuestion = (q, idx) => {
    const { id: qid, question_text, question_type, options } = q
    const isDisabled = timeExpired
    const isAnswered = isQuestionAnswered(q, answers[qid])
    const isMissing = validationAttempted && !isAnswered

    const containerStyle = `rounded-2xl p-5 space-y-4 shadow-inner transition-all border ${
      isMissing
        ? 'bg-rose-950/40 border-rose-600/80 shadow-rose-950/40 ring-1 ring-rose-500/40'
        : 'bg-slate-950/60 border-slate-800/80'
    }`

    const headerBadge = isAnswered ? (
      <span className="flex-shrink-0 text-[11px] font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-800/50 px-2.5 py-0.5 rounded-full flex items-center gap-1">
        ✓ Answered
      </span>
    ) : isMissing ? (
      <span className="flex-shrink-0 text-[11px] font-bold text-rose-200 bg-rose-950/90 border border-rose-600/80 px-2.5 py-0.5 rounded-full flex items-center gap-1 animate-pulse">
        ⚠️ Answer Required
      </span>
    ) : (
      <span className="flex-shrink-0 text-[11px] font-medium text-slate-500 bg-slate-900 border border-slate-800 px-2.5 py-0.5 rounded-full">
        Not answered
      </span>
    )

    // Multiple Choice - Checkboxes
    if (question_type === 'multiple_choice') {
      return (
        <div
          id={`question-${qid}`}
          key={qid}
          className={containerStyle}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3 flex-1">
              <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-xs font-bold flex items-center justify-center mt-0.5">
                {idx + 1}
              </span>
              <p className="text-sm font-semibold text-slate-200 leading-snug whitespace-pre-wrap">{question_text}</p>
            </div>
            {headerBadge}
          </div>

          <div className="space-y-2 pl-9">
            <p className="text-xs text-slate-400 mb-3">Select all that apply:</p>
            {options && options.map((opt) => {
              const optionLabel = opt.label || opt
              const optionText = opt.text || opt
              const isChecked = (answers[qid] || []).includes(optionLabel)

              return (
                <label
                  key={optionLabel}
                  className="flex items-start gap-3 p-3 rounded-lg bg-slate-900/50 border border-slate-800/50 hover:border-sky-700/50 cursor-pointer transition-all group"
                >
                  <input
                    type="checkbox"
                    checked={isChecked}
                    disabled={isDisabled}
                    onChange={(e) => onChangeMultiple(qid, optionLabel, e.target.checked)}
                    className="mt-0.5 w-4 h-4 rounded border-slate-700 text-sky-500 focus:ring-sky-500 focus:ring-offset-slate-950 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <span className="text-sm text-slate-300 group-hover:text-slate-200 transition-colors">
                    <span className="font-semibold text-sky-400">{optionLabel}.</span> {optionText}
                  </span>
                </label>
              )
            })}
          </div>
        </div>
      )
    }

    // Single Choice - Radio Buttons
    if (question_type === 'single_choice') {
      return (
        <div
          id={`question-${qid}`}
          key={qid}
          className={containerStyle}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3 flex-1">
              <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-xs font-bold flex items-center justify-center mt-0.5">
                {idx + 1}
              </span>
              <p className="text-sm font-semibold text-slate-200 leading-snug whitespace-pre-wrap">{question_text}</p>
            </div>
            {headerBadge}
          </div>

          <div className="space-y-2 pl-9">
            <p className="text-xs text-slate-400 mb-3">Select one:</p>
            {options && options.map((opt) => {
              const optionLabel = opt.label || opt
              const optionText = opt.text || opt
              const isChecked = answers[qid] === optionLabel

              return (
                <label
                  key={optionLabel}
                  className="flex items-start gap-3 p-3 rounded-lg bg-slate-900/50 border border-slate-800/50 hover:border-sky-700/50 cursor-pointer transition-all group"
                >
                  <input
                    type="radio"
                    name={`question-${qid}`}
                    checked={isChecked}
                    disabled={isDisabled}
                    onChange={() => onChangeSingle(qid, optionLabel)}
                    className="mt-0.5 w-4 h-4 border-slate-700 text-sky-500 focus:ring-sky-500 focus:ring-offset-slate-950 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <span className="text-sm text-slate-300 group-hover:text-slate-200 transition-colors">
                    <span className="font-semibold text-sky-400">{optionLabel}.</span> {optionText}
                  </span>
                </label>
              )
            })}
          </div>
        </div>
      )
    }

    // True/False
    if (question_type === 'true_false') {
      return (
        <div
          id={`question-${qid}`}
          key={qid}
          className={containerStyle}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3 flex-1">
              <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-xs font-bold flex items-center justify-center mt-0.5">
                {idx + 1}
              </span>
              <p className="text-sm font-semibold text-slate-200 leading-snug whitespace-pre-wrap">{question_text}</p>
            </div>
            {headerBadge}
          </div>

          <div className="flex gap-3 pl-9">
            {['true', 'false'].map((value) => (
              <label
                key={value}
                className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-900/50 border border-slate-800/50 hover:border-sky-700/50 cursor-pointer transition-all group"
              >
                <input
                  type="radio"
                  name={`question-${qid}`}
                  checked={answers[qid] === value}
                  disabled={isDisabled}
                  onChange={() => onChangeSingle(qid, value)}
                  className="w-4 h-4 border-slate-700 text-sky-500 focus:ring-sky-500 focus:ring-offset-slate-950 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                />
                <span className="text-sm font-semibold text-slate-300 group-hover:text-slate-200 transition-colors capitalize">
                  {value}
                </span>
              </label>
            ))}
          </div>
        </div>
      )
    }

    // Text/Numeric Input
    return (
      <div
        id={`question-${qid}`}
        key={qid}
        className={containerStyle}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1">
            <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-xs font-bold flex items-center justify-center mt-0.5">
              {idx + 1}
            </span>
            <p className="text-sm font-semibold text-slate-200 leading-snug whitespace-pre-wrap">{question_text}</p>
          </div>
          {headerBadge}
        </div>
        <div className="pl-9">
          <input
            type={question_type === 'numeric' ? 'number' : 'text'}
            value={answers[qid] || ''}
            placeholder="Type your answer here..."
            disabled={isDisabled}
            onChange={(e) => onChangeSingle(qid, e.target.value)}
            className="w-full px-4 py-3 bg-slate-900/90 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-400/20 text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto w-full space-y-6">
      <Link
        to="/challenges"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-sky-300 transition-colors"
      >
        ← Back to Challenges
      </Link>

      <section className="bg-slate-900/70 border border-slate-800/80 backdrop-blur-2xl rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
        <div>
          <div className="flex items-center justify-between flex-wrap gap-4 mb-2">
            <span className="text-xs font-bold tracking-widest text-sky-400 uppercase bg-sky-950/60 border border-sky-800/50 px-2.5 py-0.5 rounded-full">
              Challenge Details
            </span>
            
            {/* Show "Continuing..." badge if user returned to active attempt */}
            {challenge.has_active_attempt && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-amber-950/50 border border-amber-700/50 rounded-xl">
                <span className="text-sm">↻</span>
                <span className="text-xs font-bold text-amber-300">Continuing Challenge</span>
              </div>
            )}
            
            {/* Countdown Timer */}
            {!result && !hasSubmitted && timeLeft !== null && (
              <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border-2 transition-all ${
                timeLeft <= challenge?.time_limit_minutes * 6 
                  ? 'bg-red-950/50 border-red-700/50 animate-pulse' 
                  : timeLeft <= challenge?.time_limit_minutes * 15 
                  ? 'bg-amber-950/50 border-amber-700/50' 
                  : 'bg-slate-950/50 border-slate-700/50'
              }`}>
                <span className="text-xl">⏱️</span>
                <div>
                  <div className={`text-2xl font-bold font-mono ${getTimerColor()}`}>
                    {formatTime(timeLeft)}
                  </div>
                  <div className="text-xs text-slate-400">Time Remaining</div>
                </div>
              </div>
            )}
          </div>
          
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-2 mb-2">{challenge.title}</h1>
          {challenge.description && <p className="text-slate-400 text-sm leading-relaxed">{challenge.description}</p>}
        </div>

        {/* Time Warning Alert */}
        {!result && !hasSubmitted && timeLeft !== null && timeLeft <= challenge?.time_limit_minutes * 6 && timeLeft > 0 && (
          <div className="bg-red-950/30 border-2 border-red-700/50 rounded-xl p-4 animate-pulse">
            <div className="flex items-center gap-3">
              <span className="text-3xl">⚠️</span>
              <div>
                <p className="text-sm font-bold text-red-300">Time Running Out!</p>
                <p className="text-xs text-red-400/80">Only {formatTime(timeLeft)} remaining. Submit your answers soon!</p>
              </div>
            </div>
          </div>
        )}

        {/* Time Expired Alert */}
        {!result && !hasSubmitted && timeExpired && (
          <div className="bg-red-950/50 border-2 border-red-600/70 rounded-xl p-4">
            <div className="flex items-center gap-3">
              <span className="text-4xl">⏱️</span>
              <div>
                <p className="text-base font-bold text-red-200">Time Expired!</p>
                <p className="text-sm text-red-300/90">The challenge time limit has been reached. Auto-submitting your answers...</p>
              </div>
            </div>
          </div>
        )}

        {/* Show message if already submitted */}
        {hasSubmitted && !result && (
          <div className="text-center py-12 space-y-4">
            <span className="text-6xl block">✅</span>
            <h2 className="text-2xl font-bold text-white">Challenge Already Completed</h2>
            <p className="text-slate-400 text-sm max-w-md mx-auto">
              You've already submitted this challenge. Redirecting you to your submission history...
            </p>
            <div className="flex gap-3 justify-center pt-4">
              <Link
                to="/challenges"
                className="px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl border border-slate-700 transition-all text-sm"
              >
                ← Back to Challenges
              </Link>
              <Link
                to="/submissions"
                className="px-6 py-3 bg-gradient-to-r from-sky-400 to-cyan-400 hover:from-sky-300 hover:to-cyan-300 text-slate-950 font-bold rounded-xl shadow-lg transition-all text-sm"
              >
                View Submission History 📋
              </Link>
            </div>
          </div>
        )}

        {/* Only show questions and submit button if not yet submitted */}
        {!result && !hasSubmitted && (
          <>
            {/* Question Completion Progress & Navigation Pills */}
            {challenge.questions && challenge.questions.length > 0 && (() => {
              const answeredCount = challenge.questions.filter((q) => isQuestionAnswered(q, answers[q.id])).length
              const totalQuestions = challenge.questions.length
              const isAllAnswered = answeredCount === totalQuestions && totalQuestions > 0
              const completionPercentage = totalQuestions > 0 ? Math.round((answeredCount / totalQuestions) * 100) : 0

              return (
                <div className="bg-slate-950/70 border border-slate-800/80 rounded-2xl p-4 space-y-3 backdrop-blur-xl shadow-lg">
                  <div className="flex items-center justify-between gap-4 flex-wrap">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-white">Progress</span>
                      <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                        isAllAnswered
                          ? 'text-emerald-300 bg-emerald-950/60 border-emerald-700/60'
                          : 'text-sky-300 bg-sky-950/60 border-sky-800/50'
                      }`}>
                        {answeredCount} of {totalQuestions} answered ({completionPercentage}%)
                      </span>
                    </div>

                    {isAllAnswered ? (
                      <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                        <span>🎉</span> All questions answered! Ready to submit.
                      </span>
                    ) : (
                      <span className="text-xs text-slate-400 font-medium">
                        Answer all questions to submit
                      </span>
                    )}
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
                    <div
                      className={`h-full transition-all duration-500 rounded-full ${
                        isAllAnswered ? 'bg-gradient-to-r from-emerald-500 to-teal-400' : 'bg-gradient-to-r from-sky-500 to-cyan-400'
                      }`}
                      style={{ width: `${completionPercentage}%` }}
                    ></div>
                  </div>

                  {/* Question Jump Pills */}
                  <div className="flex items-center gap-1.5 flex-wrap pt-1">
                    <span className="text-[11px] font-medium text-slate-400 mr-1">Questions:</span>
                    {challenge.questions.map((q, idx) => {
                      const answered = isQuestionAnswered(q, answers[q.id])
                      const missing = validationAttempted && !answered

                      return (
                        <button
                          key={q.id}
                          type="button"
                          onClick={() => {
                            const el = document.getElementById(`question-${q.id}`)
                            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
                          }}
                          className={`text-[11px] font-bold px-2.5 py-1 rounded-lg border transition-all cursor-pointer flex items-center gap-1 ${
                            missing
                              ? 'bg-rose-950/80 border-rose-600/80 text-rose-300 animate-pulse'
                              : answered
                              ? 'bg-emerald-950/50 border-emerald-700/50 text-emerald-300 hover:bg-emerald-900/60'
                              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                          }`}
                        >
                          <span>Q{idx + 1}</span>
                          {answered ? <span>✓</span> : missing ? <span>!</span> : null}
                        </button>
                      )
                    })}
                  </div>
                </div>
              )
            })()}

            {/* Validation Error Banner */}
            {validationError && (
              <div className="bg-rose-950/60 border-2 border-rose-600/80 rounded-2xl p-5 text-rose-200 shadow-xl animate-pulse space-y-2">
                <div className="flex items-start gap-3">
                  <span className="text-3xl flex-shrink-0">⚠️</span>
                  <div className="flex-1 space-y-1">
                    <h4 className="text-sm font-bold text-rose-100">Answer All Questions Before Submitting</h4>
                    <p className="text-xs text-rose-300/90 leading-relaxed">{validationError}</p>
                    <p className="text-[11px] text-rose-400 font-medium pt-1">
                      Check questions marked with <span className="text-rose-200 font-bold bg-rose-900/80 px-2 py-0.5 rounded border border-rose-700">⚠️ Answer Required</span> above.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-4 pt-2">
              {challenge.questions && challenge.questions.length > 0 ? (
                challenge.questions.map((q, idx) => renderQuestion(q, idx))
              ) : (
                <p className="text-slate-500 text-sm italic">No questions found for this challenge.</p>
              )}
            </div>

            <div className="pt-4 flex flex-col items-end gap-3">
              {validationError && (
                <div className="w-full sm:w-auto text-xs font-semibold text-rose-300 bg-rose-950/90 border border-rose-600/80 px-4 py-2.5 rounded-xl flex items-center gap-2 shadow-lg animate-pulse">
                  <span>⚠️</span> {validationError}
                </div>
              )}
              <button
                onClick={onSubmit}
                disabled={submitting || timeExpired}
                className="w-full sm:w-auto px-8 py-3.5 bg-gradient-to-r from-sky-400 to-cyan-400 hover:from-sky-300 hover:to-cyan-300 text-slate-950 font-bold rounded-xl shadow-lg shadow-sky-500/20 hover:shadow-sky-500/35 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer flex items-center justify-center gap-2 text-sm"
              >
                {submitting ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-slate-950" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                    </svg>
                    Submitting Attempt...
                  </>
                ) : timeExpired ? (
                  '⏱️ Time Expired - Submitting...'
                ) : (
                  'Submit Attempt ✓'
                )}
              </button>
            </div>
          </>
        )}

        {result && result.results && (
          <section className="mt-8 pt-6 border-t border-slate-800/80 space-y-6">
            {/* Debug: Log the result data */}
            {console.log('Result data:', result)}
            {console.log('Result.results:', result.results)}
            {console.log('Result.results.answers:', result.results.answers)}
            
            {/* Info Banner */}
            <div className="bg-sky-950/30 border border-sky-700/50 rounded-xl p-4">
              <div className="flex items-center gap-2 text-sky-300">
                <span className="text-xl">ℹ️</span>
                <div className="flex-1">
                  <p className="text-sm font-semibold">This challenge has been completed</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    You can only submit each challenge once. View your other attempts in your submission history.
                  </p>
                </div>
              </div>
            </div>

            {/* Header with Score */}
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-3">
                <span className="text-4xl">
                  {result.results.total_score === result.results.answers.reduce((sum, a) => sum + (challenge.questions.find(q => q.id === a.question)?.max_score || 0), 0) ? '🎉' : result.results.total_score > 0 ? '👍' : '💪'}
                </span>
                <div>
                  <h2 className="text-2xl font-bold text-white">Challenge Complete!</h2>
                  <p className="text-sm text-slate-400">
                    {result.submission_timing_status === 'on_time' ? '✓ Submitted on time' : '⚠ Submitted late'}
                    {' • '}
                    {new Date(result.submitted_at).toLocaleString()}
                  </p>
                </div>
              </div>
              
              <div className="flex gap-4">
                <div className="px-4 py-2 bg-sky-950/50 border border-sky-800/50 rounded-xl text-center">
                  <div className="text-2xl font-bold text-sky-400">{result.results.total_score}</div>
                  <div className="text-xs text-slate-400">Your Score</div>
                </div>
                <div className="px-4 py-2 bg-emerald-950/50 border border-emerald-800/50 rounded-xl text-center">
                  <div className="text-2xl font-bold text-emerald-400">+{result.points_awarded}</div>
                  <div className="text-xs text-slate-400">Points Earned</div>
                </div>
              </div>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl text-center">
                <div className="text-lg font-bold text-white">
                  {result.results.answers.filter((a, idx) => {
                    const question = challenge.questions[idx]
                    return question && a.score === question.max_score
                  }).length}/{result.results.answers.length}
                </div>
                <div className="text-xs text-slate-400">Correct</div>
              </div>
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl text-center">
                <div className="text-lg font-bold text-white">
                  {Math.round((result.results.total_score / result.results.answers.reduce((sum, a) => sum + (challenge.questions.find(q => q.id === a.question)?.max_score || 0), 0)) * 100)}%
                </div>
                <div className="text-xs text-slate-400">Accuracy</div>
              </div>
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl text-center">
                <div className="text-lg font-bold text-white">
                  {formatTimeUserFriendly(result.results.completion_time_seconds)}
                </div>
                <div className="text-xs text-slate-400">Time Taken</div>
              </div>
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl text-center">
                <div className="text-lg font-bold text-white capitalize">
                  {result.status}
                </div>
                <div className="text-xs text-slate-400">Status</div>
              </div>
            </div>

            {/* Answer Review */}
            <div className="space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <span>📝</span> Answer Review
              </h3>
              
              {result.results.answers.map((answer, idx) => {
                console.log(`Answer ${idx}:`, answer)
                console.log(`Has score?`, answer.score)
                console.log(`Has correct_answer_value?`, answer.correct_answer_value)
                console.log(`Has explanation?`, answer.explanation)
                
                const isCorrect = answer.score > 0
                const question = challenge.questions.find(q => q.id === answer.question)
                
                console.log(`Question found?`, question)
                console.log(`isCorrect?`, isCorrect)
                
                // Normalize submitted and correct answers to arrays of uppercase strings
                const submittedAnswers = Array.isArray(answer.submitted_answer) 
                  ? answer.submitted_answer.map(a => String(a).toUpperCase())
                  : [String(answer.submitted_answer).toUpperCase()]
                
                const correctAnswers = Array.isArray(answer.correct_answer_value)
                  ? answer.correct_answer_value.map(a => String(a).toUpperCase())
                  : [String(answer.correct_answer_value).toUpperCase()]
                
                console.log(`submittedAnswers:`, submittedAnswers)
                console.log(`correctAnswers:`, correctAnswers)

                return (
                  <div
                    key={answer.question}
                    className={`p-5 rounded-2xl border-2 ${
                      isCorrect
                        ? 'bg-emerald-950/30 border-emerald-800/50'
                        : 'bg-rose-950/30 border-rose-800/50'
                    }`}
                  >
                    {/* Question Header */}
                    <div className="flex items-start gap-3 mb-4">
                      <span className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-lg font-bold ${
                        isCorrect ? 'bg-emerald-900 text-emerald-300' : 'bg-rose-900 text-rose-300'
                      }`}>
                        {isCorrect ? '✓' : '✗'}
                      </span>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-slate-200 leading-snug whitespace-pre-wrap">
                          Question {idx + 1}
                        </p>
                        <p className="text-xs text-slate-400 mt-0.5 capitalize">
                          {answer.question_type.replace('_', ' ')}
                        </p>
                      </div>
                      <div className={`px-3 py-1.5 rounded-lg text-xs font-bold ${
                        isCorrect ? 'bg-emerald-900/50 text-emerald-300' : 'bg-rose-900/50 text-rose-300'
                      }`}>
                        {answer.score}/{question?.max_score || 0} pts
                      </div>
                    </div>

                    {/* Question Text */}
                    <div className="mb-4 pl-11">
                      <p className="text-sm text-slate-300 whitespace-pre-wrap">{answer.question_text}</p>
                    </div>

                    {/* Options Display (for multiple_choice and single_choice) */}
                    {(answer.question_type === 'multiple_choice' || answer.question_type === 'single_choice') && question?.options && (
                      <div className="space-y-2 pl-11 mb-4">
                        {question.options.map((opt) => {
                          const optionLabel = (opt.label || opt).toUpperCase()
                          const optionText = opt.text || opt
                          const isUserAnswer = submittedAnswers.includes(optionLabel)
                          const isCorrectAnswer = correctAnswers.includes(optionLabel)
                          
                          // Determine the styling based on answer status
                          let optionStyle = 'bg-slate-900/50 border-slate-800/50'
                          let iconStyle = ''
                          let icon = null
                          
                          if (isUserAnswer && isCorrectAnswer) {
                            // User selected correct answer
                            optionStyle = 'bg-emerald-950/40 border-emerald-700/60'
                            iconStyle = 'text-emerald-400'
                            icon = '✓'
                          } else if (isUserAnswer && !isCorrectAnswer) {
                            // User selected wrong answer
                            optionStyle = 'bg-rose-950/40 border-rose-700/60'
                            iconStyle = 'text-rose-400'
                            icon = '✗'
                          } else if (!isUserAnswer && isCorrectAnswer) {
                            // Correct answer that user didn't select
                            optionStyle = 'bg-emerald-950/20 border-emerald-800/40'
                            iconStyle = 'text-emerald-500'
                            icon = '✓'
                          }

                          return (
                            <div
                              key={optionLabel}
                              className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${optionStyle}`}
                            >
                              {answer.question_type === 'multiple_choice' ? (
                                <div className={`mt-0.5 w-4 h-4 rounded border-2 flex items-center justify-center text-xs font-bold ${
                                  isUserAnswer ? 'border-current bg-current/20' : 'border-slate-600'
                                } ${iconStyle}`}>
                                  {isUserAnswer && '✓'}
                                </div>
                              ) : (
                                <div className={`mt-0.5 w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                                  isUserAnswer ? 'border-current' : 'border-slate-600'
                                } ${iconStyle}`}>
                                  {isUserAnswer && <div className="w-2 h-2 rounded-full bg-current"></div>}
                                </div>
                              )}
                              <span className="text-sm text-slate-300 flex-1">
                                <span className="font-semibold text-sky-400">{optionLabel}.</span> {optionText}
                              </span>
                              {icon && (
                                <span className={`text-lg font-bold ${iconStyle}`}>
                                  {icon}
                                </span>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )}

                    {/* True/False Display */}
                    {answer.question_type === 'true_false' && (
                      <div className="flex gap-3 pl-11 mb-4">
                        {['TRUE', 'FALSE'].map((value) => {
                          const isUserAnswer = submittedAnswers.includes(value)
                          const isCorrectAnswer = correctAnswers.includes(value)
                          
                          let optionStyle = 'bg-slate-900/50 border-slate-800/50'
                          let iconStyle = ''
                          let icon = null
                          
                          if (isUserAnswer && isCorrectAnswer) {
                            optionStyle = 'bg-emerald-950/40 border-emerald-700/60'
                            iconStyle = 'text-emerald-400'
                            icon = '✓'
                          } else if (isUserAnswer && !isCorrectAnswer) {
                            optionStyle = 'bg-rose-950/40 border-rose-700/60'
                            iconStyle = 'text-rose-400'
                            icon = '✗'
                          } else if (!isUserAnswer && isCorrectAnswer) {
                            optionStyle = 'bg-emerald-950/20 border-emerald-800/40'
                            iconStyle = 'text-emerald-500'
                            icon = '✓'
                          }

                          return (
                            <div
                              key={value}
                              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg border transition-all ${optionStyle}`}
                            >
                              <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                                isUserAnswer ? 'border-current' : 'border-slate-600'
                              } ${iconStyle}`}>
                                {isUserAnswer && <div className="w-2 h-2 rounded-full bg-current"></div>}
                              </div>
                              <span className="text-sm font-semibold text-slate-300 capitalize">
                                {value.toLowerCase()}
                              </span>
                              {icon && (
                                <span className={`text-lg font-bold ml-auto ${iconStyle}`}>
                                  {icon}
                                </span>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )}

                    {/* Text/Numeric Answer Display */}
                    {(answer.question_type === 'text' || answer.question_type === 'numeric') && (
                      <div className="pl-11 mb-4 space-y-2">
                        <div className={`p-3 rounded-lg border ${
                          isCorrect 
                            ? 'bg-emerald-950/40 border-emerald-700/60' 
                            : 'bg-rose-950/40 border-rose-700/60'
                        }`}>
                          <p className="text-xs text-slate-400 mb-1">Your Answer:</p>
                          <p className={`text-sm font-semibold ${
                            isCorrect ? 'text-emerald-300' : 'text-rose-300'
                          }`}>
                            {submittedAnswers[0] || '(No answer)'}
                          </p>
                        </div>
                        {!isCorrect && (
                          <div className="p-3 rounded-lg border bg-emerald-950/20 border-emerald-800/40">
                            <p className="text-xs text-slate-400 mb-1">Correct Answer:</p>
                            <p className="text-sm font-semibold text-emerald-300">
                              {correctAnswers[0]}
                            </p>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Explanation */}
                    {answer.explanation && (
                      <div className="mt-4 pt-4 border-t border-slate-700/50 pl-11">
                        <div className="bg-sky-950/30 border border-sky-800/40 rounded-lg p-3">
                          <p className="text-xs font-semibold text-sky-400 mb-1 flex items-center gap-1.5">
                            <span>💡</span> Explanation
                          </p>
                          <p className="text-xs text-slate-300 leading-relaxed">
                            {answer.explanation}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <Link
                to="/challenges"
                className="flex-1 px-6 py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-xl border border-slate-700 transition-all text-center text-sm"
              >
                ← Back to Challenges
              </Link>
              <Link
                to="/submissions"
                className="flex-1 px-6 py-3 bg-sky-900/50 hover:bg-sky-800/50 text-sky-300 hover:text-sky-200 font-semibold rounded-xl border border-sky-800/50 transition-all text-center text-sm"
              >
                View All Submissions 📋
              </Link>
            </div>
          </section>
        )}
      </section>
    </div>
  )
}
