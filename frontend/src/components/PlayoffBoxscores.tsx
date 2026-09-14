import { useBoxscore } from '../api/queries'
import { BoxscoreRoster } from './BoxscoreRoster'
import { LoadingState } from './ui/States'

interface PlayoffBoxscoresProps {
  homeLeagueId: string
  awayLeagueId: string
  homeTeamId: number
  awayTeamId: number
  homeName: string
  awayName: string
  week: number
  /** Show only the top N players per side (Home page preview) instead of the full roster (Scoreboard). */
  limit?: number
}

/** Playoff matchups can pit teams from different leagues against each other, so each
 * side's roster has to be fetched from its own league's boxscore. Shared by the Home
 * page's "Top Scorers" preview and the Scoreboard's "Full Box Score" view. */
export function PlayoffBoxscores({
  homeLeagueId,
  awayLeagueId,
  homeTeamId,
  awayTeamId,
  homeName,
  awayName,
  week,
  limit,
}: PlayoffBoxscoresProps) {
  const { data: homeBox } = useBoxscore(homeLeagueId, week)
  const { data: awayBox } = useBoxscore(awayLeagueId, week)

  const homeRoster = homeBox?.flatMap((m) => [m.home, m.away]).find((t) => t.team.team_id === homeTeamId)?.roster
  const awayRoster = awayBox?.flatMap((m) => [m.home, m.away]).find((t) => t.team.team_id === awayTeamId)?.roster

  if (!homeRoster || !awayRoster) return <LoadingState label="Loading rosters…" />

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <p className="text-xs font-semibold text-ink-400 mb-1.5">{homeName}</p>
        <BoxscoreRoster roster={homeRoster} limit={limit} />
      </div>
      <div>
        <p className="text-xs font-semibold text-ink-400 mb-1.5">{awayName}</p>
        <BoxscoreRoster roster={awayRoster} limit={limit} />
      </div>
    </div>
  )
}
