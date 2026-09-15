import { ChevronDown } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { useBoxscore, useTeam, useTeamSchedule, useTeams, useTeamTransactions } from '../api/queries'
import type { ScheduleGame, TeamRef } from '../api/types'
import { ActivityFeed } from '../components/ActivityFeed'
import { BoxscoreRoster } from '../components/BoxscoreRoster'
import { PlayerModal } from '../components/PlayerModal'
import { RosterList } from '../components/RosterList'
import { TeamBadge } from '../components/TeamBadge'
import { Card } from '../components/ui/Section'
import { Select } from '../components/ui/Select'
import { EmptyState, LoadingState } from '../components/ui/States'

export function TeamsPage() {
  const { data: teams } = useTeams()
  const { leagueId: urlLeagueId, teamId: urlTeamId } = useParams()
  const navigate = useNavigate()
  const [selected, setSelected] = useState<{ leagueId: string; teamId: number } | null>(
    urlLeagueId && urlTeamId ? { leagueId: urlLeagueId, teamId: Number(urlTeamId) } : null,
  )
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | null>(null)

  // The URL is the source of truth — a team link clicked anywhere in the app lands
  // here and this picks it up, even if TeamsPage is already mounted on another team.
  useEffect(() => {
    if (urlLeagueId && urlTeamId) {
      setSelected({ leagueId: urlLeagueId, teamId: Number(urlTeamId) })
    }
  }, [urlLeagueId, urlTeamId])

  // Bare /teams with no team specified yet: redirect to the first team's own URL.
  useEffect(() => {
    if (!urlLeagueId && !selected && teams && teams.length > 0) {
      const first = teams[0].team
      navigate(`/teams/${first.league_id}/${first.team_id}`, { replace: true })
    }
  }, [teams, selected, urlLeagueId, navigate])

  const selectTeam = (leagueId: string, teamId: number) => navigate(`/teams/${leagueId}/${teamId}`)

  const { data: detail } = useTeam(selected?.leagueId, selected?.teamId)
  const { data: schedule } = useTeamSchedule(selected?.leagueId, selected?.teamId)
  const { data: transactions } = useTeamTransactions(selected?.leagueId, selected?.teamId)

  const transactionsByWeek = useMemo(() => {
    if (!transactions) return []
    const byWeek = new Map<number, typeof transactions>()
    for (const t of transactions) {
      const list = byWeek.get(t.week) ?? []
      list.push(t)
      byWeek.set(t.week, list)
    }
    return Array.from(byWeek.entries()).sort((a, b) => b[0] - a[0])
  }, [transactions])

  if (!teams) return <LoadingState label="Loading teams…" />

  const qbs = detail?.roster.filter((p) => p.position === 'QB') ?? []
  const kickers = detail?.roster.filter((p) => p.position === 'K') ?? []
  const punters = detail?.roster.filter((p) => p.position === 'P') ?? []

  return (
    <div className="space-y-10">
      <Select
        label="Select a team to view roster"
        value={selected ? `${selected.leagueId}:${selected.teamId}` : ''}
        onChange={(e) => {
          const [leagueId, teamId] = e.target.value.split(':')
          selectTeam(leagueId, Number(teamId))
        }}
        className="w-full max-w-md"
      >
        {teams.map((t) => (
          <option key={`${t.team.league_id}:${t.team.team_id}`} value={`${t.team.league_id}:${t.team.team_id}`}>
            {t.team.team_name} ({t.team.league_name})
          </option>
        ))}
      </Select>

      {detail ? (
        <>
          <Card className="p-5 grid grid-cols-2 sm:grid-cols-5 gap-5">
            <div className="col-span-2 sm:col-span-1">
              <div className="text-xs text-ink-500 font-semibold uppercase tracking-wide mb-2">Team</div>
              <TeamBadge name={detail.team.team_name} logo={detail.logo} size={36} />
            </div>
            <Stat label="Division" value={detail.team.league_name} />
            <Stat label="Record" value={`${detail.wins}-${detail.losses}`} />
            <Stat label="Seed" value={detail.seed} />
            <Stat label="Owner" value={detail.team.owner || '—'} />
          </Card>

          <div>
            <h2 className="font-display text-xl font-bold mb-4">Roster</h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div>
                <h3 className="text-brand-400 font-semibold text-sm uppercase tracking-wide mb-2">Quarterback</h3>
                <RosterList players={qbs} onSelectPlayer={setSelectedPlayerId} />
              </div>
              <div>
                <h3 className="text-brand-400 font-semibold text-sm uppercase tracking-wide mb-2">Kickers</h3>
                <RosterList players={kickers} onSelectPlayer={setSelectedPlayerId} />
              </div>
              <div>
                <h3 className="text-brand-400 font-semibold text-sm uppercase tracking-wide mb-2">Punters</h3>
                <RosterList players={punters} onSelectPlayer={setSelectedPlayerId} />
              </div>
            </div>
          </div>

          <div>
            <h2 className="font-display text-xl font-bold mb-4">Results</h2>
            {schedule && schedule.length > 0 ? (
              <div className="space-y-2">
                {schedule.map((game) => (
                  <ScheduleRow
                    key={`${game.week}-${game.game_type}`}
                    game={game}
                    leagueId={selected!.leagueId}
                    teamId={selected!.teamId}
                    teamName={detail.team.team_name}
                  />
                ))}
              </div>
            ) : (
              <EmptyState label="No schedule available for this team" />
            )}
          </div>

          <div>
            <h2 className="font-display text-xl font-bold mb-4">Transactions</h2>
            {transactionsByWeek.length === 0 ? (
              <EmptyState label="No roster moves yet this season" />
            ) : (
              <div className="space-y-5">
                {transactionsByWeek.map(([week, events]) => (
                  <div key={week}>
                    <h3 className="text-brand-400 font-semibold text-sm uppercase tracking-wide mb-2">Week {week}</h3>
                    <ActivityFeed events={events} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      ) : (
        <LoadingState label="Loading team…" />
      )}

      {selectedPlayerId && selected ? (
        <PlayerModal
          leagueId={selected.leagueId}
          playerId={selectedPlayerId}
          onClose={() => setSelectedPlayerId(null)}
        />
      ) : null}
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-ink-500 font-semibold uppercase tracking-wide mb-1">{label}</div>
      <div className="text-xl font-display font-bold text-ink-100">{value}</div>
    </div>
  )
}

const GAME_TYPE_COLORS: Record<string, string> = {
  Quarterfinal: '#f6b93d',
  Semifinal: '#fb7185',
  '3rd Place': '#2dd4bf',
  Championship: '#a78bfa',
}

function ScheduleRow({
  game,
  leagueId,
  teamId,
  teamName,
}: {
  game: ScheduleGame
  leagueId: string
  teamId: number
  teamName: string
}) {
  const isPlayed = game.result !== '-'
  // Playoff games can be cross-league; the opponent's roster lives in their own league's
  // boxscore, so this only resolves both sides for a regular-season (same-league) game.
  const isCrossLeague = game.game_type !== 'Regular Season' && game.opponent.league_id !== leagueId
  const { data: box } = useBoxscore(leagueId, isPlayed && !isCrossLeague ? game.week : undefined)

  const mine = box?.flatMap((m) => [m.home, m.away]).find((t) => t.team.team_id === teamId)
  const theirs = box?.flatMap((m) => [m.home, m.away]).find((t) => t.team.team_name === game.opponent.team_name)

  const resultStyles: Record<string, string> = {
    W: 'text-good',
    L: 'text-bad',
    T: 'text-ink-400',
    '-': 'text-ink-600',
  }

  return (
    <details className="group rounded-xl border border-line bg-surface/70 backdrop-blur-sm overflow-hidden">
      <summary className="cursor-pointer list-none px-4 py-3 hover:bg-white/[0.02]">
        <div className="flex items-center gap-4">
          <div className="text-center w-14 shrink-0">
            <div className="text-[10px] text-ink-500 font-semibold uppercase tracking-wide">Week</div>
            <div className="text-xl font-display font-bold tabular-nums">{game.week}</div>
            {game.is_current ? <div className="text-[9px] text-bad font-semibold mt-0.5">CURRENT</div> : null}
            {game.game_type !== 'Regular Season' ? (
              <span
                className="inline-block text-[9px] font-bold text-black/80 rounded px-1.5 py-0.5 mt-1"
                style={{ backgroundColor: GAME_TYPE_COLORS[game.game_type] ?? '#a78bfa' }}
              >
                {game.game_type}
              </span>
            ) : null}
          </div>
          <div className="flex-1 flex items-center gap-3 min-w-0">
            <span className="text-ink-500 font-semibold w-5 text-sm">{game.location}</span>
            {game.opponent_logo ? (
              <img src={game.opponent_logo} alt="" className="w-9 h-9 rounded-full ring-1 ring-white/10" />
            ) : (
              <div className="w-9 h-9 rounded-full bg-white/5" />
            )}
            <OpponentLink opponent={game.opponent} />
          </div>
          <div className="text-right shrink-0">
            {isPlayed ? (
              <div className="font-semibold text-ink-300 tabular-nums">
                {game.team_score} - {game.opp_score}
              </div>
            ) : (
              <div className="text-xs text-ink-500">Not played</div>
            )}
          </div>
          <div className={`w-9 text-center text-2xl font-display font-bold shrink-0 ${resultStyles[game.result]}`}>
            {game.result}
          </div>
          {isPlayed ? (
            <ChevronDown className="w-4 h-4 text-ink-500 transition-transform group-open:rotate-180 shrink-0" />
          ) : null}
        </div>
      </summary>

      {isPlayed ? (
        <div className="px-4 pb-4 pt-1 border-t border-line">
          {isCrossLeague ? (
            <p className="text-xs text-ink-500 pt-3">Scoring details aren't available for cross-division playoff games yet.</p>
          ) : mine && theirs ? (
            <div className="grid grid-cols-2 gap-4 pt-3">
              <div>
                <p className="text-xs font-semibold text-ink-400 mb-1.5">{teamName}</p>
                <BoxscoreRoster roster={mine.roster} />
              </div>
              <div>
                <p className="text-xs font-semibold text-ink-400 mb-1.5">{game.opponent.team_name}</p>
                <BoxscoreRoster roster={theirs.roster} />
              </div>
            </div>
          ) : (
            <LoadingState />
          )}
        </div>
      ) : null}
    </details>
  )
}

function OpponentLink({ opponent }: { opponent: TeamRef }) {
  const navigate = useNavigate()

  return (
    <button
      type="button"
      onClick={(e) => {
        // Prevent the click from also toggling the parent <details> disclosure.
        e.preventDefault()
        e.stopPropagation()
        navigate(`/teams/${opponent.league_id}/${opponent.team_id}`)
      }}
      className="min-w-0 text-left hover:text-brand-400"
    >
      <div className="font-semibold text-ink-100 truncate">{opponent.team_name}</div>
      <div className="text-xs text-ink-500">{opponent.owner}</div>
    </button>
  )
}
