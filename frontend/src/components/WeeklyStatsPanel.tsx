import { Flame, Swords, TrendingDown, Zap } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { WeeklyStats } from '../api/types'
import { headshotUrl } from '../lib/format'
import { Section, Card } from './ui/Section'
import { EmptyState } from './ui/States'

export function WeeklyStatsPanel({ stats }: { stats: WeeklyStats }) {
  return (
    <div className="space-y-10">
      <Section title="Top Performers of the Week" icon={Flame}>
        <div className="space-y-2">
          {stats.top_performers.map((p, idx) => (
            <Card key={p.player_id || p.name} className="flex items-center gap-4 p-3">
              <div className="font-display text-2xl font-extrabold text-brand-400 w-8 text-center tabular-nums">
                {idx + 1}
              </div>
              {p.player_id ? (
                <img src={headshotUrl(p.player_id)} alt="" className="w-12 h-9 rounded-lg object-cover bg-white/5" />
              ) : null}
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-ink-100">{p.name}</div>
                <div className="text-xs text-ink-500">
                  {p.nfl_team} - {p.position} • {p.teams.join(', ')}
                </div>
              </div>
              <div className="flex -space-x-2">
                {p.team_logos.map((logo, i) => (
                  <img key={i} src={logo} alt="" className="w-7 h-7 rounded-full ring-2 ring-surface" />
                ))}
              </div>
              <div className="text-right w-16">
                <div className="text-xl font-display font-bold text-good tabular-nums">{p.points}</div>
                <div className="text-[10px] text-ink-500 uppercase tracking-wide">Pts</div>
              </div>
            </Card>
          ))}
        </div>
      </Section>

      <Section title="Weekly League Leaders" subtitle="Highest scoring team from each league this week" icon={Zap}>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {stats.league_leaders.map((l) => (
            <Card key={l.league_name} className="p-4 text-center">
              <div className="text-brand-400 font-semibold text-sm mb-2">{l.league_name}</div>
              {l.logo ? <img src={l.logo} alt="" className="w-14 h-14 rounded-full mx-auto mb-2 ring-1 ring-white/10" /> : null}
              <Link to={`/teams/${l.team.league_id}/${l.team.team_id}`} className="font-semibold text-ink-100 hover:text-brand-400">
                {l.team.team_name}
              </Link>
              <div className="text-xs text-ink-500 mb-1">{l.team.owner}</div>
              <div className="text-2xl font-display font-bold text-good tabular-nums">{l.score.toFixed(1)}</div>
            </Card>
          ))}
        </div>
      </Section>

      <Section title="Close Games" subtitle="Games decided by 3 points or less" icon={Swords}>
        {stats.close_games.length === 0 ? (
          <EmptyState label="No close games this week" />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {stats.close_games.map((g, i) => (
              <Card key={i} className="p-3 text-center">
                <div className="text-xs font-semibold text-ink-400 mb-1">{g.league_name}</div>
                <div className="text-sm text-ink-200 mb-1">
                  <Link to={`/teams/${g.team_a_ref.league_id}/${g.team_a_ref.team_id}`} className="hover:text-brand-400">
                    {g.team_a}
                  </Link>{' '}
                  vs{' '}
                  <Link to={`/teams/${g.team_b_ref.league_id}/${g.team_b_ref.team_id}`} className="hover:text-brand-400">
                    {g.team_b}
                  </Link>
                </div>
                <div className="text-xl font-display font-bold text-bad my-1 tabular-nums">
                  {g.score_a.toFixed(1)} - {g.score_b.toFixed(1)}
                </div>
                <div className="text-xs text-ink-500">Margin: {g.margin.toFixed(1)} pts</div>
              </Card>
            ))}
          </div>
        )}
      </Section>

      <Section title="Biggest Blowouts" subtitle="Largest margins of victory" icon={TrendingDown}>
        {stats.blowouts.length === 0 ? (
          <EmptyState label="No blowouts this week" />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {stats.blowouts.map((b, i) => (
              <Card key={i} className="p-3 text-center">
                <div className="text-xs font-semibold text-ink-400 mb-1">{b.league_name}</div>
                <Link
                  to={`/teams/${b.winner_ref.league_id}/${b.winner_ref.team_id}`}
                  className="block text-sm text-good font-semibold hover:opacity-80"
                >
                  {b.winner}
                </Link>
                <div className="text-xl font-display font-bold text-ink-100 my-1 tabular-nums">
                  {b.winner_score.toFixed(1)} - {b.loser_score.toFixed(1)}
                </div>
                <Link to={`/teams/${b.loser_ref.league_id}/${b.loser_ref.team_id}`} className="block text-sm text-bad hover:opacity-80">
                  {b.loser}
                </Link>
                <div className="text-xs text-ink-500 mt-1">Margin: {b.margin.toFixed(1)} pts</div>
              </Card>
            ))}
          </div>
        )}
      </Section>

      <Section title="Week Summary">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Metric label="Total Points" value={stats.summary.total_points.toFixed(1)} />
          <Metric label="Average / Team" value={stats.summary.average_points.toFixed(1)} />
          {stats.summary.highest_scoring_league ? (
            <Metric
              label="Highest Scoring League"
              value={stats.summary.highest_scoring_league}
              sub={`${stats.summary.highest_scoring_league_points.toFixed(1)} pts`}
            />
          ) : null}
          {stats.summary.lowest_scoring_league ? (
            <Metric
              label="Lowest Scoring League"
              value={stats.summary.lowest_scoring_league}
              sub={`${stats.summary.lowest_scoring_league_points.toFixed(1)} pts`}
            />
          ) : null}
        </div>
      </Section>
    </div>
  )
}

function Metric({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <Card className="p-3.5">
      <div className="text-xs text-ink-500">{label}</div>
      <div className="text-xl font-display font-bold text-ink-100">{value}</div>
      {sub ? <div className="text-xs text-ink-500">{sub}</div> : null}
    </Card>
  )
}
