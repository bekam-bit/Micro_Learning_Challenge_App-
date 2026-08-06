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

  useEffect(() => {
    // Load challenge details
    fetchChallenge(id)
      .then((data) => {
        setChallenge(data)
        setLoading(false)
        
        // Check if user has already submitted this challenge
        fetchMySubmissions(id)
          .then((submissionData) => {
            if (submissionData.results && submissionData.results.length > 0) {
              setHasSubmitted(true)
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

    // Multiple Choice - Checkboxes
    if (question_type === 'multiple_choice') {
      return (
        <div
          key={qid}
          className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 space-y-4 shadow-inner"
        >
          <div className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-xs font-bold flex items-center justify-center">
              {idx + 1}
            </span>
            <p className="text-sm font-semibold text-slate-200 leading-snug whitespace-pre-wrap">{question_text}</p>
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
                    onChange={(e) => onChangeMultiple(qid, optionLabel, e.target.checked)}
                    className="mt-0.5 w-4 h-4 rounded border-slate-700 text-sky-500 focus:ring-sky-500 focus:ring-offset-slate-950 cursor-pointer"
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
          key={qid}
          className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 space-y-4 shadow-inner"
        >
          <div className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-xs font-bold flex items-center justify-center">
              {idx + 1}
            </span>
            <p className="text-sm font-semibold text-slate-200 leading-snug whitespace-pre-wrap">{question_text}</p>
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
                    onChange={() => onChangeSingle(qid, optionLabel)}
                    className="mt-0.5 w-4 h-4 border-slate-700 text-sky-500 focus:ring-sky-500 focus:ring-offset-slate-950 cursor-pointer"
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
          key={qid}
          className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 space-y-4 shadow-inner"
        >
          <div className="flex items-start gap-3">
            <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-xs font-bold flex items-center justify-center">
              {idx + 1}
            </span>
            <p className="text-sm font-semibold text-slate-200 leading-snug whitespace-pre-wrap">{question_text}</p>
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
                  onChange={() => onChangeSingle(qid, value)}
                  className="w-4 h-4 border-slate-700 text-sky-500 focus:ring-sky-500 focus:ring-offset-slate-950 cursor-pointer"
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
        key={qid}
        className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 space-y-3 shadow-inner"
      >
        <div className="flex items-start gap-3">
          <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-xs font-bold flex items-center justify-center">
            {idx + 1}
          </span>
          <p className="text-sm font-semibold text-slate-200 leading-snug whitespace-pre-wrap">{question_text}</p>
        </div>
        <div className="pl-9">
          <input
            type={question_type === 'numeric' ? 'number' : 'text'}
            value={answers[qid] || ''}
            placeholder="Type your answer here..."
            onChange={(e) => onChangeSingle(qid, e.target.value)}
            className="w-full px-4 py-3 bg-slate-900/90 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-400/20 text-sm transition-all"
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
          <span className="text-xs font-bold tracking-widest text-sky-400 uppercase bg-sky-950/60 border border-sky-800/50 px-2.5 py-0.5 rounded-full">
            Challenge Details
          </span>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white mt-2 mb-2">{challenge.title}</h1>
          {challenge.description && <p className="text-slate-400 text-sm leading-relaxed">{challenge.description}</p>}
        </div>

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
            <div className="space-y-4 pt-2">
              {challenge.questions && challenge.questions.length > 0 ? (
                challenge.questions.map((q, idx) => renderQuestion(q, idx))
              ) : (
                <p className="text-slate-500 text-sm italic">No questions found for this challenge.</p>
              )}
            </div>

            <div className="pt-4 flex items-center justify-end">
              <button
                onClick={onSubmit}
                disabled={submitting}
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
                  {result.results.answers.filter(a => a.score > 0).length}/{result.results.answers.length}
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
                  {result.results.completion_time_seconds}s
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
