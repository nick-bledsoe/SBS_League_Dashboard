import { LayoutDashboard, Shield, Trophy, Users } from 'lucide-react'
import { NavLink, Route, Routes } from 'react-router-dom'

import { useCurrentWeek, useSeasons } from './api/queries'
import { BottomNav } from './components/BottomNav'
import { AdminPage } from './pages/AdminPage'
import { HomePage } from './pages/HomePage'
import { ScoreboardPage } from './pages/ScoreboardPage'
import { TeamsPage } from './pages/TeamsPage'

const navItems = [
  { to: '/', label: 'Home', icon: LayoutDashboard, end: true },
  { to: '/teams', label: 'Teams', icon: Users, end: false },
  { to: '/scoreboard', label: 'Scoreboard', icon: Trophy, end: false },
  { to: '/admin', label: 'Admin', icon: Shield, end: false },
]

export default function App() {
  const { data: currentWeekData } = useCurrentWeek()
  const { data: seasonsData } = useSeasons()

  return (
    <div className="min-h-dvh">
      <header className="sticky top-0 z-10 border-b border-line bg-base/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center gap-4">
          <div className="flex items-center gap-2.5 min-w-0 shrink-0">
            <img
              src={`${import.meta.env.BASE_URL}coachSmith.png`}
              alt=""
              className="w-8 h-8 shrink-0 drop-shadow-[0_0_10px_rgba(237,160,31,0.4)]"
            />
            <div className="min-w-0 leading-tight">
              <h1 className="font-display text-[15px] font-bold truncate">SBS League Dashboard</h1>
              <p className="text-[10px] text-brand-400 font-semibold uppercase tracking-wider">Coach Smith Cup</p>
            </div>
          </div>

          <div className="h-6 w-px bg-line shrink-0 hidden sm:block" />

          <nav className="hidden sm:flex items-center gap-0.5 flex-1 min-w-0 overflow-x-auto">
            {navItems.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `relative flex items-center gap-1.5 px-3 py-2 text-sm font-medium whitespace-nowrap transition-colors ${
                    isActive ? 'text-brand-400' : 'text-ink-400 hover:text-ink-100'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon className="w-4 h-4 shrink-0" />
                    <span>{label}</span>
                    <span
                      className={`absolute left-2 right-2 -bottom-px h-0.5 rounded-full bg-brand-400 transition-opacity ${
                        isActive ? 'opacity-100' : 'opacity-0'
                      }`}
                    />
                  </>
                )}
              </NavLink>
            ))}
          </nav>

          <div className="flex-1 sm:hidden" />

          {seasonsData && currentWeekData ? (
            <div className="flex items-center text-xs text-ink-500 font-medium shrink-0 pl-2">
              {seasonsData.current_season} · Week {currentWeekData.week}
            </div>
          ) : null}
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 pb-24 sm:pb-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/teams" element={<TeamsPage />} />
          <Route path="/scoreboard" element={<ScoreboardPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </main>

      <footer className="hidden sm:block text-center text-xs text-ink-600 py-8">
        Data sourced from ESPN Fantasy Football API — Created by Nick Bledsoe (2025)
      </footer>

      <BottomNav items={navItems} />
    </div>
  )
}
