import { BarChart3, Flame, Swords, Trophy } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { useAllMatchups, useBoxscore, useCurrentWeek, usePlayoffMatchups, usePlayoffStandings, useSeasons, useStandings } from '../api/queries'
import type { RegularMatchup } from '../api/types'
import { BoxscoreRoster } from '../components/BoxscoreRoster'
import { MatchupCard } from '../components/MatchupCard'
import { PlayoffBoxscores } from '../components/PlayoffBoxscores'
import { DivisionStandingsTable, PlayoffStandingsTable } from '../components/StandingsTable'
import { Card, Section } from '../components/ui/Section'
import { RefreshButton } from '../components/ui/RefreshButton'
import { Select } from '../components/ui/Select'
import { EmptyState, LoadingState } from '../components/ui/States'
import { MATCHUP_TYPE_COLORS } from '../lib/constants'

export function HomePage() {
  const { data: standings } = useStandings()
  const { data: playoffStandings } = usePlayoffStandings()
  const { data: allMatchups } = useAllMatchups()
  const { data: currentWeekData } = useCurrentWeek()
  const { data: seasonsData } = useSeasons()

  const [matchupType, setMatchupType] = useState<'Regular Season' | 'Playoffs'>('Regular Season')
  const [selectedWeek, setSelectedWeek] = useState<number | null>(null)

  const currentWeek = currentWeekData?.week
  const currentSeason = seasonsData?.current_season

  const { data: playoffMatchups } = usePlayoffMatchups(currentSeason)

  useEffect(() => {
    if (currentWeek !== undefined && selectedWeek === null) setSelectedWeek(currentWeek)
  }, [currentWeek, selectedWeek])

  const leagueGroups = useMemo(() => {
    if (!standings) return []
    const byLeague = new Map<string, typeof standings>()
    for (const row of standings) {
      const list = byLeague.get(row.team.league_name) ?? []
      list.push(row)
      byLeague.set(row.team.league_name, list)
    }
    return Array.from(byLeague.entries())
  }, [standings])

  const weeklyHighScores = useMemo(() => {
    if (!allMatchups) return []
    const weeks = Array.from(new Set(allMatchups.map((m) => m.week))).sort((a, b) => b - a)
    return weeks
      .map((week) => {
        const weekMatchups = allMatchups.filter((m) => m.week === week)
        const performances: {
          week: number
          team: string
          owner: string
          league: string
          score: number
          opponent: string
          leagueId: string
          teamId: number
          opponentLeagueId: string
          opponentTeamId: number
        }[] = []
        for (const m of weekMatchups) {
          if (m.home_score > 0 || m.away_score > 0) {
            performances.push({
              week,
              team: m.home.team_name,
              owner: m.home.owner,
              league: m.league_name,
              score: m.home_score,
              opponent: m.away.team_name,
              leagueId: m.home.league_id,
              teamId: m.home.team_id,
              opponentLeagueId: m.away.league_id,
              opponentTeamId: m.away.team_id,
            })
            performances.push({
              week,
              team: m.away.team_name,
              owner: m.away.owner,
              league: m.league_name,
              score: m.away_score,
              opponent: m.home.team_name,
              leagueId: m.away.league_id,
              teamId: m.away.team_id,
              opponentLeagueId: m.home.league_id,
              opponentTeamId: m.home.team_id,
            })
          }
        }
        if (performances.length === 0) return null
        return performances.reduce((a, b) => (a.score > b.score ? a : b))
      })
      .filter((x): x is NonNullable<typeof x> => x !== null)
  }, [allMatchups])

  const availableWeeks = useMemo(
    () => (allMatchups ? Array.from(new Set(allMatchups.map((m) => m.week))).sort((a, b) => a - b) : []),
    [allMatchups],
  )

  const playoffWeeks = useMemo(
    () => (playoffMatchups ? Array.from(new Set(playoffMatchups.map((m) => m.week))).sort((a, b) => a - b) : []),
    [playoffMatchups],
  )

  const playoffTeamCounts = useMemo(() => {
    if (!playoffStandings) return new Map<string, number>()
    const counts = new Map<string, number>()
    for (const row of playoffStandings.slice(0, 8)) {
      counts.set(row.team.league_name, (counts.get(row.team.league_name) ?? 0) + 1)
    }
    return counts
  }, [playoffStandings])

  return (
    <div className="space-y-12">
      <div className="flex justify-end">
        <RefreshButton label="Refresh Data" />
      </div>

      <Section
        title="Standings"
        icon={Trophy}
        subtitle="Top team from each div automatically qualifies · Min 2 teams per div · +0.5 win bonus for highest single week score"
      >
        {playoffStandings ? <PlayoffStandingsTable rows={playoffStandings} /> : <LoadingState />}

        {playoffStandings ? (
          <div className="grid grid-cols-3 gap-3 mt-4">
            {Array.from(new Set(playoffStandings.map((r) => r.team.league_name))).map((league) => (
              <Card key={league} className="p-3.5 text-center">
                <div className="text-xs text-ink-500">{league} Teams</div>
                <div className="text-2xl font-display font-bold text-ink-100">{playoffTeamCounts.get(league) ?? 0}</div>
              </Card>
            ))}
          </div>
        ) : null}
      </Section>

      <Section title="Division Breakdown" icon={BarChart3}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {leagueGroups.map(([league, rows]) => (
            <div key={league}>
              <h3 className="text-brand-400 font-semibold text-sm uppercase tracking-wide mb-2">{league}</h3>
              <DivisionStandingsTable rows={rows} />
            </div>
          ))}
        </div>
      </Section>

      <Section title="Weekly High Scores" subtitle="Highest scoring team each week across all divisions" icon={Flame}>
        {weeklyHighScores.length === 0 ? (
          <EmptyState label="No matchup data available for weekly high scores" />
        ) : (
          <>
            <Card className="overflow-x-auto mb-4">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[11px] uppercase tracking-wide text-ink-500 border-b border-line">
                    <th className="py-3 pl-4 pr-2 font-semibold">Week</th>
                    <th className="py-3 pr-2 font-semibold">Team</th>
                    <th className="py-3 pr-2 font-semibold hidden sm:table-cell">Division</th>
                    <th className="py-3 pr-2 font-semibold text-right">Score</th>
                    <th className="py-3 pr-4 font-semibold">Opponent</th>
                  </tr>
                </thead>
                <tbody>
                  {weeklyHighScores.map((h) => (
                    <tr key={h.week} className="border-b border-line/60 last:border-0 hover:bg-white/[0.02]">
                      <td className="py-2 pl-4 pr-2 tabular-nums">{h.week}</td>
                      <td className="py-2 pr-2 font-medium text-ink-100">
                        <Link to={`/teams/${h.leagueId}/${h.teamId}`} className="hover:text-brand-400">
                          {h.team}
                        </Link>
                        {h.owner ? <span className="ml-2 text-xs font-normal text-ink-500">({h.owner})</span> : null}
                      </td>
                      <td className="py-2 pr-2 text-ink-400 hidden sm:table-cell">{h.league}</td>
                      <td className="py-2 pr-2 text-right font-semibold tabular-nums text-good">{h.score.toFixed(1)}</td>
                      <td className="py-2 pr-4 text-ink-400">
                        <Link to={`/teams/${h.opponentLeagueId}/${h.opponentTeamId}`} className="hover:text-brand-400">
                          {h.opponent}
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Metric label="Highest Score" value={Math.max(...weeklyHighScores.map((h) => h.score)).toFixed(1)} />
              <Metric
                label="Average Weekly High"
                value={(weeklyHighScores.reduce((s, h) => s + h.score, 0) / weeklyHighScores.length).toFixed(1)}
              />
            </div>
          </>
        )}
      </Section>

      <Section
        title="Matchups"
        icon={Swords}
        action={
          <div className="flex gap-2">
            <Select value={matchupType} onChange={(e) => setMatchupType(e.target.value as 'Regular Season' | 'Playoffs')}>
              <option>Regular Season</option>
              <option>Playoffs</option>
            </Select>
            <Select value={selectedWeek ?? ''} onChange={(e) => setSelectedWeek(Number(e.target.value))}>
              {(matchupType === 'Regular Season' ? availableWeeks : playoffWeeks).map((w) => (
                <option key={w} value={w}>
                  {w === currentWeek ? `Week ${w} (current)` : `Week ${w}`}
                </option>
              ))}
            </Select>
          </div>
        }
      >
        {matchupType === 'Regular Season' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {leagueGroups.map(([league, rows]) => (
              <LiveMatchupColumn
                key={league}
                leagueName={league}
                leagueId={rows[0].team.league_id}
                week={selectedWeek}
                matchups={(allMatchups ?? []).filter((m) => m.league_name === league && m.week === selectedWeek)}
              />
            ))}
          </div>
        ) : playoffWeeks.length === 0 ? (
          <EmptyState icon={Trophy} label="No playoff matchups created yet. Go to the Admin tab to create matchups." />
        ) : (
          <div>
            <h3 className="text-brand-400 font-semibold text-sm uppercase tracking-wide mb-3">Coach Smith Cup Playoffs</h3>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {(playoffMatchups ?? [])
                .filter((m) => m.week === selectedWeek)
                .map((m) => (
                  <MatchupCard
                    key={m.id}
                    badge={{ label: m.round_type, color: MATCHUP_TYPE_COLORS[m.round_type] ?? '#a78bfa' }}
                    home={{
                      name: m.home.team.team_name,
                      owner: m.home.team.owner,
                      logo: m.home.logo,
                      score: m.home.score,
                      winning: m.home.winning,
                      subtitle: `(${m.home.team.league_name}, ${m.home.wins}-${m.home.losses}, seed ${m.home.seed})`,
                      leagueId: m.home.team.league_id,
                      teamId: m.home.team.team_id,
                    }}
                    away={{
                      name: m.away.team.team_name,
                      owner: m.away.team.owner,
                      logo: m.away.logo,
                      score: m.away.score,
                      winning: m.away.winning,
                      subtitle: `(${m.away.team.league_name}, ${m.away.wins}-${m.away.losses}, seed ${m.away.seed})`,
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
                      limit={3}
                    />
                  </MatchupCard>
                ))}
            </div>
          </div>
        )}
      </Section>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-3.5 text-center">
      <div className="text-xs text-ink-500">{label}</div>
      <div className="text-2xl font-display font-bold text-ink-100">{value}</div>
    </Card>
  )
}

/** Home page's regular-season matchup column. Unlike the Scoreboard's RegularSeasonColumn,
 * scores here come from the schedule endpoint (totalPointsLive — accurate mid-week), not the
 * boxscore endpoint (totalPoints — only final). The boxscore is still fetched, but only to
 * power the "Top Scorers" preview of each side's best 3 players. */
function LiveMatchupColumn({
  leagueName,
  leagueId,
  week,
  matchups,
}: {
  leagueName: string
  leagueId: string
  week: number | null
  matchups: RegularMatchup[]
}) {
  const { data: boxscores } = useBoxscore(leagueId, week ?? undefined)

  return (
    <div>
      <h3 className="text-brand-400 font-semibold text-sm uppercase tracking-wide mb-3">{leagueName}</h3>
      {matchups.length === 0 ? (
        <EmptyState label={`No matchups for week ${week}`} />
      ) : (
        matchups.map((m) => {
          const box = boxscores?.find(
            (b) => b.home.team.team_id === m.home.team_id && b.away.team.team_id === m.away.team_id,
          )
          return (
            <MatchupCard
              key={`${m.home.team_id}-${m.away.team_id}`}
              home={{
                name: m.home.team_name,
                owner: m.home.owner,
                logo: m.home_logo,
                score: m.home_score,
                winning: m.home_score > m.away_score,
                leagueId: m.home.league_id,
                teamId: m.home.team_id,
              }}
              away={{
                name: m.away.team_name,
                owner: m.away.owner,
                logo: m.away_logo,
                score: m.away_score,
                winning: m.away_score > m.home_score,
                leagueId: m.away.league_id,
                teamId: m.away.team_id,
              }}
            >
              {box ? (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs font-semibold text-ink-400 mb-1.5">{m.home.team_name}</p>
                    <BoxscoreRoster roster={box.home.roster} limit={3} />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-ink-400 mb-1.5">{m.away.team_name}</p>
                    <BoxscoreRoster roster={box.away.roster} limit={3} />
                  </div>
                </div>
              ) : (
                <LoadingState label="Loading rosters…" />
              )}
            </MatchupCard>
          )
        })
      )}
    </div>
  )
}
