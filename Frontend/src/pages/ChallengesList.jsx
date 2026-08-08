import { useEffect, useState } from 'react'
import { fetchChallenges, fetchMySubmissions } from '../api/challenges'
import { Link } from 'react-router'

export default function ChallengesList() {
  const [challenges, setChallenges] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [totalChallenges, setTotalChallenges] = useState(0) // Track total challenges in system
  const [allCompleted, setAllCompleted] = useState(false) // Track if user completed all

  useEffect(() => {
    // Load both challenges and user's submissions
    // Use cache busting (true) to get fresh data and avoid stale cache issues
    Promise.all([
      fetchChallenges(true),
      fetchMySubmissions() // Get all submissions to filter out completed challenges
    ])
      .then(([challengesData, submissionsData]) => {
        const allChallenges = challengesData.results || challengesData
        
        // Get IDs of challenges the user has already submitted
        const submittedChallengeIds = new Set(
          (submissionsData.results || []).map(sub => sub.challenge)
        )
        
        // DEBUG: Log the data
        console.log('🔍 DEBUG: Challenges List Data')
        console.log('Total challenges from API:', allChallenges.length)
        console.log('All challenges:', allChallenges.map(c => ({ id: c.id, title: c.title })))
        console.log('Total submissions:', submissionsData.results?.length || 0)
        console.log('Submitted challenge IDs:', Array.from(submittedChallengeIds))
        
        // Filter out completed challenges
        const availableChallenges = allChallenges.filter(
          challenge => !submittedChallengeIds.has(challenge.id)
        )
        
        console.log('Available challenges (after filter):', availableChallenges.length)
        console.log('Available:', availableChallenges.map(c => ({ id: c.id, title: c.title })))
        
        // Set state to distinguish between "no challenges exist" vs "all completed"
        setTotalChallenges(allChallenges.length)
        setAllCompleted(allChallenges.length > 0 && availableChallenges.length === 0)
        setChallenges(availableChallenges)
        setLoading(false)
      })
      .catch((err) => {
        console.error('❌ Error loading challenges:', err)
        setError(
          err?.response?.status === 401
            ? 'You must be logged in to view challenges.'
            : 'Failed to load challenges from the server.'
        )
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="space-y-6 max-w-5xl mx-auto w-full">
        <div className="flex items-center justify-between">
          <div className="h-8 w-48 bg-slate-800 rounded-lg animate-pulse"></div>
          <div className="h-6 w-24 bg-slate-800 rounded-full animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div
              key={n}
              className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 h-48 animate-pulse flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="h-4 w-1/3 bg-slate-800 rounded"></div>
                <div className="h-6 w-3/4 bg-slate-800 rounded"></div>
              </div>
              <div className="h-4 w-1/2 bg-slate-800 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto w-full space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/70 border border-slate-800/80 backdrop-blur-xl rounded-2xl p-6 shadow-xl">
        <div>
          <span className="text-xs font-bold tracking-widest text-sky-400 uppercase bg-sky-950/60 border border-sky-800/50 px-2.5 py-0.5 rounded-full">
            Available Modules
          </span>
          <h1 className="text-2xl font-bold text-white mt-1">Learning Challenges</h1>
        </div>
        <div className="text-xs font-semibold text-slate-400 bg-slate-950/60 px-3.5 py-1.5 rounded-xl border border-slate-800">
          Total: <span className="text-sky-300 font-bold">{challenges.length}</span>
        </div>
      </div>

      {error && (
        <div className="bg-rose-950/40 border border-rose-800/60 rounded-2xl p-5 text-rose-300 flex items-center justify-between gap-4 shadow-lg">
          <div className="flex items-center gap-3">
            <span className="text-lg">⚠️</span>
            <p className="text-sm font-medium">{error}</p>
          </div>
          <Link
            to="/login"
            className="px-4 py-2 text-xs font-bold bg-rose-900/60 hover:bg-rose-900 text-rose-100 rounded-xl border border-rose-700/60 transition-all"
          >
            Go to Login
          </Link>
        </div>
      )}

      {challenges.length === 0 && !error && (
        <div className="text-center py-16 bg-slate-900/50 border border-slate-800 rounded-2xl space-y-4">
          {allCompleted ? (
            // User has completed all available challenges
            <>
              <span className="text-5xl">🎉</span>
              <p className="text-slate-300 text-lg font-semibold">All challenges completed!</p>
              <p className="text-slate-400 text-sm">
                Amazing work! You've completed all {totalChallenges} available challenge{totalChallenges !== 1 ? 's' : ''}. 
                Check back later for new ones!
              </p>
              <Link
                to="/submissions"
                className="inline-block mt-4 px-6 py-3 bg-gradient-to-r from-sky-400 to-cyan-400 hover:from-sky-300 hover:to-cyan-300 text-slate-950 font-bold rounded-xl shadow-lg transition-all"
              >
                View Your Submissions 📋
              </Link>
            </>
          ) : (
            // No challenges exist in the system yet
            <>
              <span className="text-5xl">📚</span>
              <p className="text-slate-300 text-lg font-semibold">No challenges available yet</p>
              <p className="text-slate-400 text-sm">
                There are no challenges in the system at the moment. Check back soon!
              </p>
            </>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {challenges.map((c, index) => (
          <div
            key={c.id || index}
            className="group relative bg-slate-900/70 border border-slate-800/80 hover:border-sky-500/40 rounded-2xl p-6 transition-all duration-300 hover:shadow-xl hover:shadow-sky-500/10 hover:-translate-y-1 backdrop-blur-xl flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold text-sky-400 bg-sky-950/80 border border-sky-800/50 px-2.5 py-0.5 rounded-md">
                  Challenge #{c.id || index + 1}
                </span>
                {c.category && (
                  <span className="text-[11px] font-medium text-slate-400 bg-slate-950 px-2 py-0.5 rounded">
                    {c.category}
                  </span>
                )}
              </div>
              <h2 className="text-lg font-bold text-white group-hover:text-sky-300 transition-colors line-clamp-2">
                {c.title}
              </h2>
              {c.summary && <p className="text-slate-400 text-xs leading-relaxed line-clamp-3">{c.summary}</p>}
            </div>

            <div className="pt-5 mt-4 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-xs text-slate-500 font-medium">
                {c.questions ? `${c.questions.length} Questions` : 'Interactive Quiz'}
              </span>
              <Link
                to={`/challenges/${c.id}`}
                className={`inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1.5 rounded-xl border transition-all ${
                  c.has_active_attempt
                    ? 'text-amber-400 group-hover:text-amber-300 bg-amber-950/40 group-hover:bg-amber-900/50 border-amber-800/40'
                    : 'text-sky-400 group-hover:text-sky-300 bg-sky-950/40 group-hover:bg-sky-900/50 border-sky-800/40'
                }`}
              >
                {c.has_active_attempt ? (
                  <>
                    <span>⏱️</span> Continue Challenge
                    <span className="group-hover:translate-x-0.5 transition-transform">→</span>
                  </>
                ) : (
                  <>
                    Start Challenge
                    <span className="group-hover:translate-x-0.5 transition-transform">→</span>
                  </>
                )}
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

