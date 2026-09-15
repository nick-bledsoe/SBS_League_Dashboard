import { ChevronLeft, ChevronRight, Star } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { usePlayerRankings } from '../api/queries'
import type { TeamRef } from '../api/types'
import { PlayerModal } from '../components/PlayerModal'
import { Card, Section } from '../components/ui/Section'
import { EmptyState, LoadingState } from '../components/ui/States'
import { headshotUrl } from '../lib/format'

const POSITION_TABS = ['Overall', 'QB', 'K', 'P'] as const
type PositionTab = (typeof POSITION_TABS)[number]

const PAGE_SIZE = 50

export function PlayersPage() {
  const { data: rankings, isLoading } = usePlayerRankings()
  const [tab, setTab] = useState<PositionTab>('Overall')
  const [page, setPage] = useState(1)
  const [selected, setSelected] = useState<{ leagueId: string; playerId: string } | null>(null)

  const filtered = useMemo(() => {
    if (!rankings) return []
    return tab === 'Overall' ? rankings : rankings.filter((r) => r.position === tab)
  }, [rankings, tab])

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE))
  useEffect(() => setPage(1), [tab])
  useEffect(() => {
    if (page > totalPages) setPage(totalPages)
  }, [page, totalPages])

  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  return (
    <div className="space-y-6">
      <Section
        title="Player Rankings"
        icon={Star}
        subtitle="Season-long fantasy points, deduplicated across every league"
      >
        <div className="flex gap-1.5 mb-4">
          {POSITION_TABS.map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                tab === t ? 'bg-brand-500/15 text-brand-400' : 'text-ink-400 hover:text-ink-100 hover:bg-white/5'
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        {isLoading ? (
          <LoadingState label="Crunching every league's boxscores…" />
        ) : filtered.length === 0 ? (
          <EmptyState label="No player data available yet" />
        ) : (
          <Card className="overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[11px] uppercase tracking-wide text-ink-500 border-b border-line">
                  <th className="py-3 pl-4 pr-2 font-semibold w-10">#</th>
                  <th className="py-3 pr-2 font-semibold">Player</th>
                  <th className="py-3 pr-2 font-semibold hidden sm:table-cell">Pos</th>
                  <th className="py-3 pr-2 font-semibold hidden md:table-cell">Owned By</th>
                  <th className="py-3 pr-2 font-semibold text-right">Total</th>
                  <th className="py-3 pr-2 font-semibold text-right hidden sm:table-cell">GP</th>
                  <th className="py-3 pr-4 font-semibold text-right">Avg</th>
                </tr>
              </thead>
              <tbody>
                {paged.map((r, idx) => (
                  <tr
                    key={r.player_id}
                    onClick={() => setSelected({ leagueId: r.league_id, playerId: r.player_id })}
                    className="border-b border-line/60 last:border-0 hover:bg-white/[0.03] cursor-pointer transition-colors"
                  >
                    <td className="py-2 pl-4 pr-2 text-ink-500 tabular-nums">
                      {(page - 1) * PAGE_SIZE + idx + 1}
                    </td>
                    <td className="py-2 pr-2">
                      <div className="flex items-center gap-2.5 min-w-0">
                        <img
                          src={headshotUrl(r.player_id)}
                          alt=""
                          className="w-9 h-7 rounded object-cover bg-white/5 shrink-0"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none'
                          }}
                        />
                        <div className="min-w-0">
                          <div className="font-medium text-ink-100 truncate">{r.name}</div>
                          <div className="text-[11px] text-ink-500 sm:hidden">
                            {r.position} · {r.nfl_team}
                          </div>
                          <div className="text-[11px] text-ink-500 hidden sm:block">{r.nfl_team}</div>
                          <div className="md:hidden">
                            <OwnedByCell owners={r.owners} />
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="py-2 pr-2 text-ink-400 hidden sm:table-cell">{r.position}</td>
                    <td className="py-2 pr-2 hidden md:table-cell">
                      <OwnedByCell owners={r.owners} />
                    </td>
                    <td className="py-2 pr-2 text-right font-semibold tabular-nums text-good">
                      {r.total_points.toFixed(1)}
                    </td>
                    <td className="py-2 pr-2 text-right tabular-nums text-ink-400 hidden sm:table-cell">
                      {r.games_played}
                    </td>
                    <td className="py-2 pr-4 text-right tabular-nums text-ink-400">{r.avg_points.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        )}

        {!isLoading && totalPages > 1 ? (
          <div className="flex items-center justify-between mt-4 text-sm">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-ink-400 hover:text-ink-100 hover:bg-white/5 transition-colors disabled:opacity-30 disabled:pointer-events-none"
            >
              <ChevronLeft className="w-4 h-4" />
              Prev
            </button>
            <span className="text-ink-500">
              Page {page} of {totalPages} · {filtered.length} players
            </span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-ink-400 hover:text-ink-100 hover:bg-white/5 transition-colors disabled:opacity-30 disabled:pointer-events-none"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        ) : null}
      </Section>

      {selected ? (
        <PlayerModal leagueId={selected.leagueId} playerId={selected.playerId} onClose={() => setSelected(null)} />
      ) : null}
    </div>
  )
}

function OwnedByCell({ owners }: { owners: TeamRef[] }) {
  if (owners.length === 0) return <span className="text-[11px] text-ink-600">Unrostered</span>

  return (
    <div className="text-[11px] text-ink-500">
      {owners.map((o, i) => (
        <span key={`${o.league_id}-${o.team_id}`}>
          <Link
            to={`/teams/${o.league_id}/${o.team_id}`}
            onClick={(e) => e.stopPropagation()}
            className="hover:text-brand-400"
            title={`${o.team_name} (${o.league_name})`}
          >
            {o.owner || o.team_name}
          </Link>
          {i < owners.length - 1 ? ', ' : ''}
        </span>
      ))}
    </div>
  )
}
