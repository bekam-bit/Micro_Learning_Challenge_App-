import { useEffect, useState } from 'react'
import { fetchMySubmissions, fetchChallenge, fetchSubmissionById } from '../api/challenges'
import { Link } from 'react-router'

export default function SubmissionHistory() {
  const [submissions, setSubmissions] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedSubmission, setSelectedSubmission] = useState(null)
  const [selectedChallenge, setSelectedChallenge] = useState(null)
  const [viewMode, setViewMode] = useState('list') // 'list' or 'detail'

  useEffect(() => {
    loadSubmissions()
  }, [])

  const loadSubmissions = async () => {
    try {
      const data = await fetchMySubmissions()
      setSubmissions(data.results || [])
      setLoading(false)
    } catch (err) {
      console.error('Error loading submissions:', err)
      setLoading(false)
    }
  }

  const viewSubmissionDetail = async (submission) => {
    try {
      // Load the challenge details to get question info
      const challengeData = await fetchChallenge(submission.challenge)
      
      // Load the graded submission result by submission ID
      const gradedResult = await fetchSubmissionById(submission.id)
      
      console.log('Challenge data:', challengeData)
      console.log('Graded result:', gradedResult)
      
      // The gradedResult should already have the complete structure with results field
      const enrichedSubmission = {
        ...submission,
        ...gradedResult // Merge all graded data including the results field
      }
      
      console.log('Enriched submission:', enrichedSubmission)
      
      setSelectedChallenge(challengeData)
      setSelectedSubmission(enrichedSubmission)
      setViewMode('detail')
    } catch (err) {
      console.error('Error loading submission details:', err)
      console.error('Error response:', err.response?.data)
      alert('Failed to load submission details. Please try again.')
    }
  }

  const backToList = () => {
    setViewMode('list')
    setSelectedSubmission(null)
    setSelectedChallenge(null)
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto w-full p-8 bg-slate-900/60 border border-slate-800 rounded-3xl animate-pulse space-y-6">
        <div className="h-8 w-48 bg-slate-800 rounded"></div>
        <div className="space-y-4">
          <div className="h-24 bg-slate-800/60 rounded-2xl"></div>
          <div className="h-24 bg-slate-800/60 rounded-2xl"></div>
          <div className="h-24 bg-slate-800/60 rounded-2xl"></div>
        </div>
      </div>
    )
  }

  // Detail View
  if (viewMode === 'detail' && selectedSubmission && selectedChallenge) {
    const result = selectedSubmission
    const challenge = selectedChallenge

    return (
      <div className="max-w-4xl mx-auto w-full space-y-6">
        <button
          onClick={backToList}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-sky-300 transition-colors"
        >
          ← Back to Submission History
        </button>

        <section className="bg-slate-900/70 border border-slate-800/80 backdrop-blur-2xl rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
          {/* Header with Score */}
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <span className="text-4xl">
                {result.results.total_score === result.results.answers.reduce((sum, a) => sum + (challenge.questions.find(q => q.id === a.question)?.max_score || 0), 0) ? '🎉' : result.results.total_score > 0 ? '👍' : '💪'}
              </span>
              <div>
                <h2 className="text-2xl font-bold text-white">{result.challenge_title}</h2>
                <p className="text-sm text-slate-400">
                  Attempt #{result.attempt} • {new Date(result.submitted_at).toLocaleString()}
                </p>
                <p className="text-xs text-slate-500">
                  {result.submission_timing_status === 'on_time' ? '✓ Submitted on time' : '⚠ Submitted late'}
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
              const isCorrect = answer.score > 0
              const question = challenge.questions.find(q => q.id === answer.question)
              
              const submittedAnswers = Array.isArray(answer.submitted_answer) 
                ? answer.submitted_answer.map(a => String(a).toUpperCase())
                : [String(answer.submitted_answer).toUpperCase()]
              
              const correctAnswers = Array.isArray(answer.correct_answer_value)
                ? answer.correct_answer_value.map(a => String(a).toUpperCase())
                : [String(answer.correct_answer_value).toUpperCase()]

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
                      <p className="text-sm font-semibold text-slate-200 leading-snug">
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
        </section>
      </div>
    )
  }

  // List View
  return (
    <div className="max-w-5xl mx-auto w-full space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-white">Submission History</h1>
          <p className="text-sm text-slate-400 mt-1">Review all your past challenge attempts</p>
        </div>
        <Link
          to="/challenges"
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-xl border border-slate-700 transition-all"
        >
          Browse Challenges
        </Link>
      </div>

      {submissions.length === 0 ? (
        <div className="bg-slate-900/70 border border-slate-800/80 rounded-3xl p-12 text-center space-y-4">
          <span className="text-6xl">📭</span>
          <h2 className="text-xl font-bold text-white">No Submissions Yet</h2>
          <p className="text-slate-400 text-sm max-w-md mx-auto">
            You haven't submitted any challenges yet. Start a challenge to see your submission history here!
          </p>
          <Link
            to="/challenges"
            className="inline-block px-6 py-3 bg-gradient-to-r from-sky-400 to-cyan-400 hover:from-sky-300 hover:to-cyan-300 text-slate-950 font-bold rounded-xl shadow-lg transition-all mt-4"
          >
            Browse Challenges
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {submissions.map((submission) => {
            const accuracy = submission.results 
              ? Math.round((submission.results.total_score / submission.results.answers.reduce((sum, a) => sum + a.score, 0)) * 100) || 0
              : 0
            const isPerfect = accuracy === 100

            return (
              <div
                key={submission.id}
                className="bg-slate-900/70 border border-slate-800/80 backdrop-blur-xl rounded-2xl p-5 hover:border-slate-700 transition-all group"
              >
                <div className="flex items-center justify-between gap-4 flex-wrap">
                  <div className="flex items-center gap-4 flex-1">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-2xl ${
                      isPerfect ? 'bg-emerald-950/50 border-2 border-emerald-700/50' : 'bg-slate-950/50 border-2 border-slate-700/50'
                    }`}>
                      {isPerfect ? '🎉' : submission.results?.total_score > 0 ? '👍' : '💪'}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-white group-hover:text-sky-400 transition-colors">
                        {submission.challenge_title}
                      </h3>
                      <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                        <span>Attempt #{submission.attempt}</span>
                        <span>•</span>
                        <span>{new Date(submission.submitted_at).toLocaleDateString()}</span>
                        <span>•</span>
                        <span className={submission.submission_timing_status === 'on_time' ? 'text-emerald-400' : 'text-amber-400'}>
                          {submission.submission_timing_status === 'on_time' ? '✓ On Time' : '⚠ Late'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-2xl font-bold text-sky-400">
                        {submission.results?.total_score || submission.score || 0}
                      </div>
                      <div className="text-xs text-slate-400">Score</div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-emerald-400">
                        +{submission.points_awarded}
                      </div>
                      <div className="text-xs text-slate-400">Points</div>
                    </div>
                    <button
                      onClick={() => viewSubmissionDetail(submission)}
                      className="px-4 py-2 bg-sky-900/50 hover:bg-sky-800/50 text-sky-300 hover:text-sky-200 border border-sky-800/50 rounded-xl text-sm font-semibold transition-all"
                    >
                      View Details →
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
