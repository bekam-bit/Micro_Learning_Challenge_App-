import { useEffect, useState } from 'react'
import { fetchUserProfile, fetchMySubmissions } from '../api/challenges'
import { Link } from 'react-router'

export default function Dashboard() {
  const [profile, setProfile] = useState(null)
  const [submissions, setSubmissions] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalChallenges: 0,
    totalScore: 0,
    avgAccuracy: 0,
    perfectScores: 0,
  })

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [profileData, submissionsData] = await Promise.all([
        fetchUserProfile(),
        fetchMySubmissions()
      ])

      setProfile(profileData)
      setSubmissions(submissionsData.results || [])

      // Calculate stats
      const subs = submissionsData.results || []
      const totalScore = subs.reduce((sum, sub) => sum + (sub.results?.total_score || sub.score || 0), 0)
      const perfectScores = subs.filter(sub => {
        if (!sub.results?.answers) return false
        const total = sub.results.answers.reduce((sum, a) => sum + (a.score || 0), 0)
        return total === sub.results.total_score && sub.results.total_score > 0
      }).length

      // Calculate average accuracy
      let totalAccuracy = 0
      let validSubmissions = 0
      subs.forEach(sub => {
        if (sub.results?.answers && sub.results.answers.length > 0) {
          const maxScore = sub.results.answers.reduce((sum, a) => {
            return sum + (a.score || 0) + (a.score === 0 ? 10 : 0) // Assume 10 points per question
          }, 0)
          if (maxScore > 0) {
            totalAccuracy += ((sub.results.total_score / maxScore) * 100)
            validSubmissions++
          }
        }
      })

      setStats({
        totalChallenges: subs.length,
        totalScore,
        avgAccuracy: validSubmissions > 0 ? Math.round(totalAccuracy / validSubmissions) : 0,
        perfectScores,
      })

      setLoading(false)
    } catch (err) {
      console.error('Error loading dashboard:', err)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto w-full space-y-6 animate-pulse">
        <div className="h-10 w-64 bg-slate-800 rounded-lg"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="h-32 bg-slate-900/60 border border-slate-800 rounded-2xl"></div>
          ))}
        </div>
        <div className="h-64 bg-slate-900/60 border border-slate-800 rounded-3xl"></div>
      </div>
    )
  }

  const recentSubmissions = submissions.slice(0, 5)

  return (
    <div className="max-w-6xl mx-auto w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
            <span className="text-4xl">📊</span>
            Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1">Track your learning progress and achievements</p>
        </div>
        <Link
          to="/challenges"
          className="px-5 py-2.5 bg-gradient-to-r from-sky-400 to-cyan-400 hover:from-sky-300 hover:to-cyan-300 text-slate-950 font-bold rounded-xl shadow-lg transition-all text-sm"
        >
          Start Challenge
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Points */}
        <div className="bg-gradient-to-br from-sky-950/50 to-sky-900/30 border border-sky-800/50 backdrop-blur-xl rounded-2xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl">⭐</span>
            <div className="px-2 py-1 bg-sky-900/50 rounded-lg">
              <span className="text-xs font-bold text-sky-300">TOTAL</span>
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mb-1">
            {profile?.profile?.total_points || 0}
          </div>
          <div className="text-xs text-slate-400 font-medium">Points Earned</div>
        </div>

        {/* Challenges Completed */}
        <div className="bg-gradient-to-br from-emerald-950/50 to-emerald-900/30 border border-emerald-800/50 backdrop-blur-xl rounded-2xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl">✅</span>
            <div className="px-2 py-1 bg-emerald-900/50 rounded-lg">
              <span className="text-xs font-bold text-emerald-300">COUNT</span>
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mb-1">
            {stats.totalChallenges}
          </div>
          <div className="text-xs text-slate-400 font-medium">Challenges Attempted</div>
        </div>

        {/* Average Accuracy */}
        <div className="bg-gradient-to-br from-purple-950/50 to-purple-900/30 border border-purple-800/50 backdrop-blur-xl rounded-2xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl">🎯</span>
            <div className="px-2 py-1 bg-purple-900/50 rounded-lg">
              <span className="text-xs font-bold text-purple-300">AVG</span>
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mb-1">
            {stats.avgAccuracy}%
          </div>
          <div className="text-xs text-slate-400 font-medium">Average Accuracy</div>
        </div>

        {/* Perfect Scores */}
        <div className="bg-gradient-to-br from-amber-950/50 to-amber-900/30 border border-amber-800/50 backdrop-blur-xl rounded-2xl p-5 shadow-xl">
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl">🏆</span>
            <div className="px-2 py-1 bg-amber-900/50 rounded-lg">
              <span className="text-xs font-bold text-amber-300">BEST</span>
            </div>
          </div>
          <div className="text-3xl font-extrabold text-white mb-1">
            {stats.perfectScores}
          </div>
          <div className="text-xs text-slate-400 font-medium">Perfect Scores</div>
        </div>
      </div>

      {/* Progress & Streaks Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Streak */}
        <div className="bg-slate-900/70 border border-slate-800/80 backdrop-blur-xl rounded-3xl p-6 shadow-2xl">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>🔥</span> Learning Streak
          </h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-4xl font-extrabold text-transparent bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text">
                  {profile?.profile?.current_streak || 0} days
                </div>
                <div className="text-sm text-slate-400 mt-1">Current Streak</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-amber-400">
                  {profile?.profile?.max_streak || 0}
                </div>
                <div className="text-xs text-slate-400">Best Streak</div>
              </div>
            </div>
            {profile?.profile?.last_activity_date && (
              <div className="pt-3 border-t border-slate-800">
                <div className="text-xs text-slate-400">
                  Last Active: <span className="text-slate-300 font-semibold">
                    {new Date(profile.profile.last_activity_date).toLocaleDateString()}
                  </span>
                </div>
              </div>
            )}
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4">
              <div className="text-xs text-slate-400 mb-2">Keep your streak alive!</div>
              <div className="text-sm text-slate-300">
                Complete a challenge today to maintain your {profile?.profile?.current_streak || 0}-day streak 🚀
              </div>
            </div>
          </div>
        </div>

        {/* Completion Stats */}
        <div className="bg-slate-900/70 border border-slate-800/80 backdrop-blur-xl rounded-3xl p-6 shadow-2xl">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <span>📈</span> Progress Overview
          </h2>
          <div className="space-y-4">
            {/* Challenges Progress */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-300">Challenges</span>
                <span className="text-sm font-bold text-sky-400">
                  {profile?.profile?.challenges_completed_count || 0} / {profile?.profile?.challenges_total_count || 0}
                </span>
              </div>
              <div className="w-full bg-slate-950/80 rounded-full h-3 border border-slate-800">
                <div 
                  className="bg-gradient-to-r from-sky-500 to-cyan-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${profile?.profile?.challenges_completion_percentage || 0}%` }}
                ></div>
              </div>
              <div className="text-xs text-slate-400 mt-1">
                {Math.round(profile?.profile?.challenges_completion_percentage || 0)}% Complete
              </div>
            </div>

            {/* Modules Progress */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-300">Modules</span>
                <span className="text-sm font-bold text-emerald-400">
                  {profile?.profile?.modules_completed_count || 0} / {profile?.profile?.modules_total_count || 0}
                </span>
              </div>
              <div className="w-full bg-slate-950/80 rounded-full h-3 border border-slate-800">
                <div 
                  className="bg-gradient-to-r from-emerald-500 to-green-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${profile?.profile?.modules_completion_percentage || 0}%` }}
                ></div>
              </div>
              <div className="text-xs text-slate-400 mt-1">
                {Math.round(profile?.profile?.modules_completion_percentage || 0)}% Complete
              </div>
            </div>

            {/* Lessons Progress */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-300">Lessons</span>
                <span className="text-sm font-bold text-purple-400">
                  {profile?.profile?.lessons_completed_count || 0} / {profile?.profile?.lessons_total_count || 0}
                </span>
              </div>
              <div className="w-full bg-slate-950/80 rounded-full h-3 border border-slate-800">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-full rounded-full transition-all duration-500"
                  style={{ width: `${profile?.profile?.lessons_completion_percentage || 0}%` }}
                ></div>
              </div>
              <div className="text-xs text-slate-400 mt-1">
                {Math.round(profile?.profile?.lessons_completion_percentage || 0)}% Complete
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-slate-900/70 border border-slate-800/80 backdrop-blur-xl rounded-3xl p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span>⚡</span> Recent Activity
          </h2>
          <Link
            to="/submissions"
            className="text-sm font-semibold text-sky-400 hover:text-sky-300 transition-colors"
          >
            View All →
          </Link>
        </div>

        {recentSubmissions.length === 0 ? (
          <div className="text-center py-12">
            <span className="text-6xl mb-4 block">🎯</span>
            <h3 className="text-lg font-bold text-white mb-2">No Activity Yet</h3>
            <p className="text-sm text-slate-400 mb-4">Start a challenge to see your activity here!</p>
            <Link
              to="/challenges"
              className="inline-block px-6 py-3 bg-gradient-to-r from-sky-400 to-cyan-400 hover:from-sky-300 hover:to-cyan-300 text-slate-950 font-bold rounded-xl shadow-lg transition-all"
            >
              Browse Challenges
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {recentSubmissions.map((submission) => {
              const accuracy = submission.results 
                ? Math.round((submission.results.total_score / submission.results.answers.reduce((sum, a) => sum + (a.score || 0) + (a.score === 0 ? 10 : 0), 0)) * 100) || 0
                : 0

              return (
                <div
                  key={submission.id}
                  className="flex items-center justify-between p-4 bg-slate-950/60 border border-slate-800 rounded-xl hover:border-slate-700 transition-all group"
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl ${
                      accuracy === 100 ? 'bg-emerald-950/50 border-2 border-emerald-700/50' : 'bg-slate-900/50 border-2 border-slate-700/50'
                    }`}>
                      {accuracy === 100 ? '🎉' : accuracy >= 75 ? '👍' : accuracy >= 50 ? '📝' : '💪'}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white group-hover:text-sky-400 transition-colors">
                        {submission.challenge_title}
                      </h3>
                      <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                        <span>{new Date(submission.submitted_at).toLocaleDateString()}</span>
                        <span>•</span>
                        <span className={accuracy === 100 ? 'text-emerald-400' : accuracy >= 50 ? 'text-sky-400' : 'text-slate-400'}>
                          {accuracy}% accuracy
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-lg font-bold text-sky-400">
                        {submission.results?.total_score || submission.score || 0}
                        <span className="text-xs text-slate-500">/{submission.challenge_max_score || '?'}</span>
                      </div>
                      <div className="text-xs text-slate-400">Score</div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-emerald-400">
                        +{submission.points_awarded}
                        <span className="text-xs text-slate-500">/{submission.challenge_points || '?'}</span>
                      </div>
                      <div className="text-xs text-slate-400">Points</div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Achievements Section */}
      <div className="bg-slate-900/70 border border-slate-800/80 backdrop-blur-xl rounded-3xl p-6 shadow-2xl">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <span>🏅</span> Achievements
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {/* First Challenge */}
          <div className={`p-4 rounded-xl border-2 text-center ${
            stats.totalChallenges >= 1 
              ? 'bg-sky-950/30 border-sky-700/50' 
              : 'bg-slate-950/30 border-slate-800 opacity-40'
          }`}>
            <div className="text-3xl mb-2">🎯</div>
            <div className="text-xs font-bold text-slate-300">First Step</div>
            <div className="text-xs text-slate-500 mt-1">Complete 1 challenge</div>
          </div>

          {/* 5 Challenges */}
          <div className={`p-4 rounded-xl border-2 text-center ${
            stats.totalChallenges >= 5 
              ? 'bg-emerald-950/30 border-emerald-700/50' 
              : 'bg-slate-950/30 border-slate-800 opacity-40'
          }`}>
            <div className="text-3xl mb-2">🌟</div>
            <div className="text-xs font-bold text-slate-300">Getting Started</div>
            <div className="text-xs text-slate-500 mt-1">Complete 5 challenges</div>
          </div>

          {/* Perfect Score */}
          <div className={`p-4 rounded-xl border-2 text-center ${
            stats.perfectScores >= 1 
              ? 'bg-amber-950/30 border-amber-700/50' 
              : 'bg-slate-950/30 border-slate-800 opacity-40'
          }`}>
            <div className="text-3xl mb-2">💯</div>
            <div className="text-xs font-bold text-slate-300">Perfectionist</div>
            <div className="text-xs text-slate-500 mt-1">Get a perfect score</div>
          </div>

          {/* 7 Day Streak */}
          <div className={`p-4 rounded-xl border-2 text-center ${
            (profile?.profile?.max_streak || 0) >= 7 
              ? 'bg-orange-950/30 border-orange-700/50' 
              : 'bg-slate-950/30 border-slate-800 opacity-40'
          }`}>
            <div className="text-3xl mb-2">🔥</div>
            <div className="text-xs font-bold text-slate-300">On Fire</div>
            <div className="text-xs text-slate-500 mt-1">7-day streak</div>
          </div>

          {/* 1000 Points */}
          <div className={`p-4 rounded-xl border-2 text-center ${
            (profile?.profile?.total_points || 0) >= 1000 
              ? 'bg-purple-950/30 border-purple-700/50' 
              : 'bg-slate-950/30 border-slate-800 opacity-40'
          }`}>
            <div className="text-3xl mb-2">⭐</div>
            <div className="text-xs font-bold text-slate-300">Point Master</div>
            <div className="text-xs text-slate-500 mt-1">Earn 1000 points</div>
          </div>
        </div>
      </div>
    </div>
  )
}
