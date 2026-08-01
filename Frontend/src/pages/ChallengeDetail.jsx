import { useEffect, useState } from 'react'
import { fetchChallenge, submitAttempt } from '../api/challenges'
import { useParams, Link } from 'react-router'

export default function ChallengeDetail() {
  const { id } = useParams()
  const [challenge, setChallenge] = useState(null)
  const [loading, setLoading] = useState(true)
  const [answers, setAnswers] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult] = useState(null)

  useEffect(() => {
    fetchChallenge(id)
      .then((data) => {
        setChallenge(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [id])

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

  const onChange = (questionId, value) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }))
  }

  const onSubmit = async () => {
    setSubmitting(true)
    try {
      const payload = {
        attempt: {
          answers: Object.keys(answers).map((qid) => ({ question: qid, answer: answers[qid] })),
        },
      }
      const idempotencyKey = `attempt-${id}-${Date.now()}`
      const res = await submitAttempt(challenge.id, payload, idempotencyKey)
      setResult(res)
    } catch (err) {
      console.error(err)
      alert('Submission failed. Please check your answers and try again.')
    } finally {
      setSubmitting(false)
    }
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
          {challenge.summary && <p className="text-slate-400 text-sm leading-relaxed">{challenge.summary}</p>}
        </div>

        <div className="space-y-4 pt-2">
          {challenge.questions && challenge.questions.length > 0 ? (
            challenge.questions.map((q, idx) => (
              <div
                key={q.id || idx}
                className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-5 space-y-3 shadow-inner"
              >
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-sky-950 text-sky-400 border border-sky-800/50 text-xs font-bold flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <label className="text-sm font-semibold text-slate-200 leading-snug">{q.prompt}</label>
                </div>
                <div>
                  <input
                    type="text"
                    value={answers[q.id] || ''}
                    placeholder="Type your answer here..."
                    onChange={(e) => onChange(q.id, e.target.value)}
                    className="w-full px-4 py-3 bg-slate-900/90 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-400/20 text-sm transition-all"
                  />
                </div>
              </div>
            ))
          ) : (
            <p className="text-slate-500 text-sm italic">No specific questions found for this challenge.</p>
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

        {result && (
          <section className="mt-8 pt-6 border-t border-slate-800/80 space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-emerald-400 text-lg">🎉</span>
              <h2 className="text-lg font-bold text-white">Submission Result</h2>
            </div>
            <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 overflow-x-auto text-xs font-mono text-emerald-400 leading-relaxed shadow-inner">
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          </section>
        )}
      </section>
    </div>
  )
}

