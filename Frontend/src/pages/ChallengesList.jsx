import { useEffect, useState } from 'react'
import { fetchChallenges } from '../api/challenges'
import { Link } from 'react-router'

export default function ChallengesList() {
  const [challenges, setChallenges] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchChallenges()
      .then((data) => {
        setChallenges(data.results || data)
        setLoading(false)
      })
      .catch((err) => {
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
        <div className="text-center py-16 bg-slate-900/50 border border-slate-800 rounded-2xl">
          <p className="text-slate-400 text-base">No challenges available right now.</p>
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
                className="inline-flex items-center gap-1.5 text-xs font-bold text-sky-400 group-hover:text-sky-300 bg-sky-950/40 group-hover:bg-sky-900/50 px-3 py-1.5 rounded-xl border border-sky-800/40 transition-all"
              >
                Start Challenge
                <span className="group-hover:translate-x-0.5 transition-transform">→</span>
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

