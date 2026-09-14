import { useBoxscore } from '../api/queries'
import { BoxscoreRoster } from './BoxscoreRoster'
import { MatchupCard } from './MatchupCard'
import { LoadingState, EmptyState } from './ui/States'

interface RegularSeasonColumnProps {
  leagueName: string
  leagueId: string
  week: number | null
  /** Preview mode (Home page): show only the top N scorers. Omit for the full box score (Scoreboard). */
  limit?: number
}

/** One league's regular-season matchups + expandable box scores for a given week.
 * Shared by the Home page (compact preview) and the Scoreboard page (full box score). */
export function RegularSeasonColumn({ leagueName, leagueId, week, limit }: RegularSeasonColumnProps) {
  const { data: boxscores, isLoading } = useBoxscore(leagueId, week ?? undefined)

  return (
    <div>
      <h3 className="text-brand-400 font-semibold text-sm uppercase tracking-wide mb-3">{leagueName}</h3>
      {isLoading ? (
        <LoadingState />
      ) : !boxscores || boxscores.length === 0 ? (
        <EmptyState label={`No matchups for week ${week}`} />
      ) : (
        boxscores.map((m) => (
          <MatchupCard
            key={`${m.home.team.team_id}-${m.away.team.team_id}`}
            expandLabel={limit ? 'Top Scorers' : 'Full Box Score'}
            home={{
              name: m.home.team.team_name,
              owner: m.home.team.owner,
              logo: m.home.logo,
              score: m.home.total_points,
              winning: m.home.total_points > m.away.total_points,
            }}
            away={{
              name: m.away.team.team_name,
              owner: m.away.team.owner,
              logo: m.away.logo,
              score: m.away.total_points,
              winning: m.away.total_points > m.home.total_points,
            }}
          >
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-semibold text-ink-400 mb-1.5">{m.home.team.team_name}</p>
                <BoxscoreRoster roster={m.home.roster} limit={limit} />
              </div>
              <div>
                <p className="text-xs font-semibold text-ink-400 mb-1.5">{m.away.team.team_name}</p>
                <BoxscoreRoster roster={m.away.roster} limit={limit} />
              </div>
            </div>
          </MatchupCard>
        ))
      )}
    </div>
  )
}
