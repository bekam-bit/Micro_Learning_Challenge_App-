import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import api, { formatApiError } from '../api/axios'
import { useAuth } from '../auth/AuthContext'

export default function Register() {
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const updateField = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSubmitting(true)

    const payload = {
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password,
    }

    try {
      await api.post('/auth/register/', payload)
      await login(payload.username, payload.password)
      navigate('/challenges')
    } catch (err) {
      setError(formatApiError(err, 'Registration failed.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="bg-slate-900/80 border border-slate-800/80 backdrop-blur-2xl rounded-3xl p-8 sm:p-10 shadow-2xl shadow-slate-950 max-w-md mx-auto my-auto w-full">
      <div className="text-center mb-6">
        <span className="text-xs font-bold tracking-widest text-sky-400 uppercase bg-sky-950/60 border border-sky-800/50 px-2.5 py-0.5 rounded-full inline-block mb-2">
          Join Platform
        </span>
        <h2 className="text-2xl font-bold text-white">Create Account</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Username
          </label>
          <input
            value={form.username}
            onChange={updateField('username')}
            placeholder="Choose username"
            required
            className="w-full px-4 py-3 bg-slate-950/80 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-400/20 text-sm transition-all"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Email Address
          </label>
          <input
            type="email"
            value={form.email}
            onChange={updateField('email')}
            placeholder="you@example.com"
            required
            className="w-full px-4 py-3 bg-slate-950/80 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-400/20 text-sm transition-all"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-400 mb-1.5 uppercase tracking-wider">
            Password
          </label>
          <input
            type="password"
            value={form.password}
            onChange={updateField('password')}
            placeholder="Min 8 characters"
            required
            minLength={8}
            className="w-full px-4 py-3 bg-slate-950/80 border border-slate-800 rounded-xl text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-400 focus:ring-2 focus:ring-sky-400/20 text-sm transition-all"
          />
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-950/50 border border-rose-800/60 text-rose-300 text-xs flex items-start gap-2 whitespace-pre-line">
            <span className="text-sm">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <button
          disabled={submitting}
          type="submit"
          className="w-full py-3.5 px-4 bg-gradient-to-r from-sky-400 to-cyan-400 hover:from-sky-300 hover:to-cyan-300 text-slate-950 font-bold rounded-xl shadow-lg shadow-sky-500/20 hover:shadow-sky-500/35 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 transition-all duration-200 cursor-pointer flex items-center justify-center gap-2 text-sm mt-2"
        >
          {submitting ? (
            <>
              <svg className="animate-spin h-4 w-4 text-slate-950" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
              </svg>
              Creating Account...
            </>
          ) : (
            'Register Account →'
          )}
        </button>
      </form>

      <p className="text-slate-400 text-xs text-center mt-6 pt-4 border-t border-slate-800/80">
        Already have an account?{' '}
        <Link to="/login" className="text-sky-400 hover:text-sky-300 font-semibold hover:underline">
          Login here
        </Link>
      </p>
    </section>
  )
}

