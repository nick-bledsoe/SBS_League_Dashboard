import { Trophy } from 'lucide-react'
import { useEffect, useState } from 'react'

import { useCurrentWeek, useLeagues, usePlayoffMatchups, useSeasons, useWeeklyStats } from '../api/queries'
import { MatchupCard } from '../components/MatchupCard'
import { PlayoffBoxscores } from '../components/PlayoffBoxscores'
import { RegularSeasonColumn } from '../components/RegularSeasonColumn'
import { RefreshButton } from '../components/ui/RefreshButton'
import { Select } from '../components/ui/Select'
import { EmptyState } from '../components/ui/States'
import { WeeklyStatsPanel } from '../components/WeeklyStatsPanel'
import { MATCHUP_TYPE_COLORS } from '../lib/constants'

export function ScoreboardPage() {
  const { data: currentWeekData } = useCurrentWeek()
  const { data: leagues } = useLeagues()
  const { data: seasonsData } = useSeasons()

  const [week, setWeek] = useState<number | null>(null)
  const [phase, setPhase] = useState<'regular' | 'playoff'>('regular')

  const currentSeason = seasonsData?.current_season
  const currentWeek = currentWeekData?.week

  useEffect(() => {
    if (currentWeek !== undefined && week === null) setWeek(currentWeek)
  }, [currentWeek, week])

  const { data: playoffMatchups } = usePlayoffMatchups(currentSeason, week ?? undefined)
  const { data: weeklyStats } = useWeeklyStats(week ?? undefined, phase, currentSeason)

  return (
    <div className="space-y-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-bold">League Scoreboard</h1>
          <p className="text-sm text-ink-500 mt-1">View detailed player-by-player scoring breakdowns</p>
        </div>
        <div className="flex flex-wrap gap-2 items-center">
          <Select value={week ?? ''} onChange={(e) => setWeek(Number(e.target.value))}>
            {Array.from({ length: 18 }, (_, i) => i + 1).map((w) => (
              <option key={w} value={w}>
                {w === currentWeek ? `Week ${w} (current)` : `Week ${w}`}
              </option>
            ))}
          </Select>
          <Select value={phase} onChange={(e) => setPhase(e.target.value as 'regular' | 'playoff')}>
            <option value="regular">Regular Season</option>
            <option value="playoff">Playoffs</option>
          </Select>
          <RefreshButton label="Refresh Scores" />
        </div>
      </div>

      {phase === 'playoff' ? (
        !playoffMatchups || playoffMatchups.length === 0 ? (
          <EmptyState icon={Trophy} label="No playoff matchups for this week. Go to Admin tab to create them." />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {playoffMatchups.map((m) => (
              <MatchupCard
                key={m.id}
                expandLabel="Full Box Score"
                badge={{ label: m.round_type, color: MATCHUP_TYPE_COLORS[m.round_type] ?? '#a78bfa' }}
                home={{
                  name: m.home.team.team_name,
                  owner: m.home.team.owner,
                  logo: m.home.logo,
                  score: m.home.score,
                  winning: m.home.winning,
                  subtitle: `(${m.home.team.league_name}, ${m.home.wins}-${m.home.losses})`,
                  leagueId: m.home.team.league_id,
                  teamId: m.home.team.team_id,
                }}
                away={{
                  name: m.away.team.team_name,
                  owner: m.away.team.owner,
                  logo: m.away.logo,
                  score: m.away.score,
                  winning: m.away.winning,
                  subtitle: `(${m.away.team.league_name}, ${m.away.wins}-${m.away.losses})`,
                  leagueId: m.away.team.league_id,
                  teamId: m.away.team.team_id,
                }}
              >
                <PlayoffBoxscores
                  homeLeagueId={m.home.team.league_id}
                  awayLeagueId={m.away.team.league_id}
                  homeTeamId={m.home.team.team_id}
                  awayTeamId={m.away.team.team_id}
                  homeName={m.home.team.team_name}
                  awayName={m.away.team.team_name}
                  week={m.week}
                />
              </MatchupCard>
            ))}
          </div>
        )
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {(leagues ?? []).map((league) => (
            <RegularSeasonColumn key={league.id} leagueName={league.name} leagueId={league.id} week={week} />
          ))}
        </div>
      )}

      {weeklyStats ? (
        <div className="pt-8 border-t border-line">
          <h2 className="font-display text-xl font-bold mb-6">Week {week} Stats</h2>
          <WeeklyStatsPanel stats={weeklyStats} />
        </div>
      ) : null}
    </div>
  )
}
