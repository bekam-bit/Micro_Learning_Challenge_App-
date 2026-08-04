import { NavLink } from 'react-router'
import { useAuth } from '../auth/useAuth'

export default function Layout({ children }) {
  const { user, loading, logout } = useAuth()

  return (
    <div className="min-h-screen max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex flex-col font-sans">
      <header className="bg-slate-900/70 border border-slate-800/80 backdrop-blur-xl rounded-2xl p-4 sm:p-6 mb-8 shadow-xl shadow-slate-950/50 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 text-center md:text-left">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-400 to-cyan-500 flex items-center justify-center text-slate-950 font-black text-xl shadow-lg shadow-sky-500/20">
            ⚡
          </div>
          <div>
            <p className="text-[11px] font-bold tracking-widest text-sky-400 uppercase bg-sky-950/60 border border-sky-800/50 px-2.5 py-0.5 rounded-full w-fit mx-auto md:mx-0">
              Micro Learning Challenge
            </p>
            <h1 className="text-lg sm:text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              Learn, practice, and track progress
            </h1>
          </div>
        </div>

        <nav className="flex flex-wrap items-center justify-center gap-1.5 bg-slate-950/60 p-1.5 rounded-xl border border-slate-800/80">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30 shadow-sm shadow-sky-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`
            }
          >
            Home
          </NavLink>
          {user && (
            <NavLink
              to="/dashboard"
              className={({ isActive }) =>
                `px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30 shadow-sm shadow-sky-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
                }`
              }
            >
              Dashboard
            </NavLink>
          )}
          <NavLink
            to="/challenges"
            className={({ isActive }) =>
              `px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30 shadow-sm shadow-sky-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`
            }
          >
            Challenges
          </NavLink>
          {user && (
            <NavLink
              to="/submissions"
              className={({ isActive }) =>
                `px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30 shadow-sm shadow-sky-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
                }`
              }
            >
              My Submissions
            </NavLink>
          )}
          <NavLink
            to="/login"
            className={({ isActive }) =>
              `px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30 shadow-sm shadow-sky-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`
            }
          >
            Login
          </NavLink>
          <NavLink
            to="/register"
            className={({ isActive }) =>
              `px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-sky-500/15 text-sky-300 border border-sky-500/30 shadow-sm shadow-sky-500/10'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'
              }`
            }
          >
            Register
          </NavLink>
        </nav>

        <div className="flex items-center gap-3 text-sm text-slate-300 bg-slate-950/40 px-3.5 py-1.5 rounded-xl border border-slate-800/60">
          {loading ? (
            <span className="text-slate-500 animate-pulse text-xs">Checking session...</span>
          ) : user ? (
            <>
              <span className="text-xs text-slate-300">
                Signed in as <strong className="text-sky-300 font-semibold">{user.username}</strong>
              </span>
              <button
                className="px-3 py-1 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60 transition-all active:scale-95 cursor-pointer"
                onClick={logout}
              >
                Logout
              </button>
            </>
          ) : (
            <span className="text-xs text-slate-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-slate-500"></span>
              Guest Mode
            </span>
          )}
        </div>
      </header>

      <main className="flex-1 flex flex-col">{children}</main>
    </div>
  )
}
