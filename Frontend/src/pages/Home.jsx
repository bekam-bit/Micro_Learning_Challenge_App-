import { Link } from 'react-router'

export default function Home() {
  return (
    <section className="relative overflow-hidden bg-slate-900/70 border border-slate-800/80 backdrop-blur-2xl rounded-3xl p-8 sm:p-12 shadow-2xl max-w-3xl mx-auto my-auto text-center md:text-left">
      <div className="absolute -top-24 -right-24 w-60 h-60 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-60 h-60 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <span className="inline-block text-xs font-bold tracking-widest text-sky-400 uppercase bg-sky-950/80 border border-sky-800/50 px-3 py-1 rounded-full mb-4">
        Micro Learning Platform
      </span>
      <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight mb-4">
        Practice with interactive challenges & track your real-time progress.
      </h2>
      <p className="text-slate-400 text-base sm:text-lg leading-relaxed max-w-2xl mb-8">
        Create an account or login to unlock micro-challenges, test your knowledge, and boost your skills with rapid feedback loops.
      </p>

      <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 mb-8">
        <Link
          to="/login"
          className="px-6 py-3 text-sm font-bold text-slate-950 bg-gradient-to-r from-sky-400 to-cyan-400 hover:from-sky-300 hover:to-cyan-300 rounded-xl shadow-lg shadow-sky-500/20 hover:shadow-sky-500/35 hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200"
        >
          Login to Account
        </Link>
        <Link
          to="/register"
          className="px-6 py-3 text-sm font-semibold text-slate-200 bg-slate-800/90 hover:bg-slate-800 border border-slate-700/80 rounded-xl hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200"
        >
          Create New Account
        </Link>
        <Link
          to="/challenges"
          className="px-6 py-3 text-sm font-semibold text-sky-400 hover:text-sky-300 bg-sky-950/40 hover:bg-sky-950/60 border border-sky-800/40 rounded-xl transition-all duration-200"
        >
          View Challenges →
        </Link>
      </div>

      <div className="pt-6 border-t border-slate-800/80 flex items-center justify-between flex-wrap gap-2 text-xs text-slate-500">
        <span>Backend API connected:</span>
        <code className="px-2.5 py-1 bg-slate-950/80 rounded-md border border-slate-800 text-sky-400 font-mono">
          https://learning-challenge.onrender.com
        </code>
      </div>
    </section>
  )
}

