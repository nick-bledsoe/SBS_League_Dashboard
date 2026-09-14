import type { RosterPlayer } from '../api/types'
import { headshotUrl } from '../lib/format'
import { EmptyState } from './ui/States'

export function RosterList({ players }: { players: RosterPlayer[] }) {
  if (players.length === 0) {
    return <EmptyState label="No players" />
  }

  return (
    <div className="space-y-1.5">
      {players.map((p) => (
        <div
          key={p.player_id || p.name}
          className="flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg bg-surface-raised border border-line"
        >
          <div className="flex items-center gap-3 min-w-0">
            {p.player_id ? (
              <img
                src={headshotUrl(p.player_id)}
                alt=""
                className="w-10 h-7 rounded object-cover shrink-0 bg-white/5"
                onError={(e) => {
                  e.currentTarget.style.display = 'none'
                }}
              />
            ) : (
              <div className="w-10 h-7 rounded bg-white/5 shrink-0" />
            )}
            <div className="min-w-0">
              <div className="text-sm font-medium text-ink-100 truncate">{p.name}</div>
              <div className="text-[11px] text-ink-500">Pos Rank: {p.positional_rank}</div>
            </div>
          </div>
          {p.nfl_logo ? (
            <img
              src={p.nfl_logo}
              alt={p.nfl_team}
              className="w-7 h-7 shrink-0"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          ) : null}
        </div>
      ))}
    </div>
  )
}
