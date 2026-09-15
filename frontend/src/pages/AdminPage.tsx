import { Plus, Trash2 } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import {
  useCreatePlayoffMatchup,
  useCurrentWeek,
  useDeletePlayoffMatchup,
  usePlayoffMatchups,
  usePlayoffStandings,
  useSeasons,
  useTeams,
  useUpdatePlayoffMatchup,
} from '../api/queries'
import { MATCHUP_TYPES, type MatchupType, type TeamSummary } from '../api/types'
import { Badge } from '../components/ui/Badge'
import { Card, Section } from '../components/ui/Section'
import { Select } from '../components/ui/Select'
import { EmptyState } from '../components/ui/States'
import { MATCHUP_TYPE_COLORS } from '../lib/constants'

function teamKey(t: TeamSummary): string {
  return `${t.team.league_id}:${t.team.team_id}`
}

export function AdminPage() {
  const { data: seasonsData } = useSeasons()
  const { data: teams } = useTeams()
  const { data: playoffStandings } = usePlayoffStandings()
  const { data: currentWeekData } = useCurrentWeek()

  const [season, setSeason] = useState<number | null>(null)
  useEffect(() => {
    if (seasonsData && season === null) setSeason(seasonsData.current_season)
  }, [seasonsData, season])

  const seedFor = (teamName: string) => {
    const row = playoffStandings?.find((r) => r.team.team_name === teamName)
    return row ? String(row.rank) : 'N/A'
  }

  const [team1Key, setTeam1Key] = useState('')
  const [team2Key, setTeam2Key] = useState('')
  const [roundType, setRoundType] = useState<MatchupType>('Quarterfinal')
  const [createWeek, setCreateWeek] = useState(currentWeekData?.week ?? 1)
  const [formError, setFormError] = useState<string | null>(null)

  useEffect(() => {
    if (teams && teams.length > 0 && !team1Key) setTeam1Key(teamKey(teams[0]))
    if (teams && teams.length > 1 && !team2Key) setTeam2Key(teamKey(teams[1]))
  }, [teams, team1Key, team2Key])
  useEffect(() => {
    if (currentWeekData) setCreateWeek(currentWeekData.week)
  }, [currentWeekData])

  const createMutation = useCreatePlayoffMatchup()

  const handleCreate = () => {
    setFormError(null)
    const team1 = teams?.find((t) => teamKey(t) === team1Key)
    const team2 = teams?.find((t) => teamKey(t) === team2Key)
    if (!team1 || !team2 || !season) return
    if (team1.team.team_name === team2.team.team_name && team1.team.league_name === team2.team.league_name) {
      setFormError('Cannot create a matchup with the same team!')
      return
    }
    createMutation.mutate(
      { season, week: createWeek, round_type: roundType, home: team1.team, away: team2.team },
      { onError: (err) => setFormError(err instanceof Error ? err.message : 'Failed to create matchup') },
    )
  }

  const [viewWeek, setViewWeek] = useState<number | null>(null)
  useEffect(() => {
    if (currentWeekData && viewWeek === null) setViewWeek(currentWeekData.week)
  }, [currentWeekData, viewWeek])

  const { data: allSeasonMatchups } = usePlayoffMatchups(season ?? undefined)
  const weeksWithMatchups = useMemo(
    () => Array.from(new Set((allSeasonMatchups ?? []).map((m) => m.week))).sort((a, b) => a - b),
    [allSeasonMatchups],
  )
  const { data: weekMatchups } = usePlayoffMatchups(season ?? undefined, viewWeek ?? undefined)

  const updateMutation = useUpdatePlayoffMatchup()
  const deleteMutation = useDeletePlayoffMatchup()

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-display text-2xl font-bold">Admin Panel</h1>
        <p className="text-sm text-ink-500 mt-1">Manage playoff matchups and league settings</p>
      </div>

      <Select label="Select Season" value={season ?? ''} onChange={(e) => setSeason(Number(e.target.value))}>
        {(seasonsData?.seasons ?? []).map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </Select>

      <Card className="p-5">
        <h3 className="font-display font-bold mb-4">Create Playoff Matchup</h3>
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
          <div className="sm:col-span-2">
            <Select label="Team 1" value={team1Key} onChange={(e) => setTeam1Key(e.target.value)} className="w-full">
              {(teams ?? []).map((t) => (
                <option key={teamKey(t)} value={teamKey(t)}>
                  {t.team.team_name} (seed {seedFor(t.team.team_name)})
                </option>
              ))}
            </Select>
          </div>
          <div className="sm:col-span-2">
            <Select label="Team 2" value={team2Key} onChange={(e) => setTeam2Key(e.target.value)} className="w-full">
              {(teams ?? []).map((t) => (
                <option key={teamKey(t)} value={teamKey(t)}>
                  {t.team.team_name} (seed {seedFor(t.team.team_name)})
                </option>
              ))}
            </Select>
          </div>
          <Select label="Round" value={roundType} onChange={(e) => setRoundType(e.target.value as MatchupType)} className="w-full">
            {MATCHUP_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </Select>
          <Select label="Week" value={createWeek} onChange={(e) => setCreateWeek(Number(e.target.value))} className="w-full">
            {Array.from({ length: 18 }, (_, i) => i + 1).map((w) => (
              <option key={w} value={w}>
                {w === currentWeekData?.week ? `${w} (current)` : w}
              </option>
            ))}
          </Select>
        </div>
        <button
          onClick={handleCreate}
          disabled={createMutation.isPending}
          className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 text-sm font-semibold rounded-lg bg-brand-500 text-black hover:bg-brand-400 transition-colors disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          Create Matchup
        </button>
        {formError ? <p className="text-bad text-sm mt-2">{formError}</p> : null}
      </Card>

      <Section title="Playoff Matchups" icon={Plus}>
        {weeksWithMatchups.length === 0 ? (
          <EmptyState label="No playoff matchups created yet. Create one above to get started!" />
        ) : (
          <>
            <Select
              value={viewWeek ?? ''}
              onChange={(e) => setViewWeek(Number(e.target.value))}
              className="mb-4"
            >
              {weeksWithMatchups.map((w) => (
                <option key={w} value={w}>
                  {w === currentWeekData?.week ? `Week ${w} (current)` : `Week ${w}`}
                </option>
              ))}
            </Select>

            <div className="space-y-3">
              {(weekMatchups ?? []).map((m) => (
                <Card key={m.id} className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <Badge label={m.round_type} color={MATCHUP_TYPE_COLORS[m.round_type] ?? '#a78bfa'} />
                    <div className="flex gap-2">
                      <Select
                        value={m.round_type}
                        onChange={(e) => updateMutation.mutate({ id: m.id, payload: { round_type: e.target.value as MatchupType } })}
                        className="py-1 text-xs"
                      >
                        {MATCHUP_TYPES.map((t) => (
                          <option key={t} value={t}>
                            {t}
                          </option>
                        ))}
                      </Select>
                      <button
                        onClick={() => deleteMutation.mutate(m.id)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-xs rounded-lg border border-bad/30 text-bad hover:bg-bad/10 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        Delete
                      </button>
                    </div>
                  </div>

                  <div className="divide-y divide-line/60">
                    {[m.home, m.away].map((side) => (
                      <div key={side.team.team_id} className="flex items-center justify-between py-2.5">
                        <div className="flex items-center gap-3">
                          {side.logo ? (
                            <img src={side.logo} alt="" className="w-10 h-10 rounded-full ring-1 ring-white/10" />
                          ) : (
                            <div className="w-10 h-10 rounded-full bg-white/5" />
                          )}
                          <div>
                            <div className={side.winning ? 'font-bold text-ink-100' : 'text-ink-200'}>
                              <Link to={`/teams/${side.team.league_id}/${side.team.team_id}`} className="hover:text-brand-400">
                                {side.team.team_name}
                              </Link>
                              <span className="ml-2 text-xs text-ink-500 font-normal">{side.team.owner}</span>
                            </div>
                            <div className="text-xs text-ink-500">
                              {side.team.league_name} · {side.wins}-{side.losses} · seed {side.seed}
                            </div>
                          </div>
                        </div>
                        <div className={`text-2xl font-display font-bold tabular-nums ${side.winning ? 'text-good' : 'text-ink-500'}`}>
                          {side.score ?? '---'}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              ))}
            </div>
          </>
        )}
      </Section>
    </div>
  )
}
