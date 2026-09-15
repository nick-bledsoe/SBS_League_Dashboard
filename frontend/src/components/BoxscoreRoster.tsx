import type { BoxscorePlayer } from '../api/types'
import { lastName } from '../lib/format'
import { PlayerRow } from './PlayerRow'

export function BoxscoreRoster({ roster, limit }: { roster: BoxscorePlayer[]; limit?: number }) {
  const sorted = [...roster].sort((a, b) => b.points - a.points)
  const shown = limit ? sorted.slice(0, limit) : sorted
  const total = roster.reduce((sum, p) => sum + p.points, 0)

  return (
    <div>
      {shown.map((p) => (
        <PlayerRow
          key={p.player_id || p.name}
          playerId={p.player_id}
          name={limit ? lastName(p.name) : p.name}
          subtitle={limit ? undefined : `${p.nfl_team} - ${p.position}`}
          trailing={p.points.toString()}
          points={p.points}
        />
      ))}
      {!limit ? (
        <div className="flex justify-between text-sm font-bold pt-2 mt-1 border-t border-line text-ink-100">
          <span>Total</span>
          <span className="tabular-nums">{total.toFixed(2)}</span>
        </div>
      ) : null}
    </div>
  )
}
