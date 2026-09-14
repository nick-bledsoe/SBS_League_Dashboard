import { headshotUrl, pointsColor } from '../lib/format'

interface PlayerRowProps {
  playerId: string
  name: string
  subtitle?: string
  trailing?: string
  points?: number
}

export function PlayerRow({ playerId, name, subtitle, trailing, points }: PlayerRowProps) {
  return (
    <div className="flex items-center justify-between gap-2 px-2.5 py-2 rounded-lg hover:bg-white/[0.03] transition-colors">
      <div className="flex items-center gap-2.5 min-w-0">
        {playerId ? (
          <img
            src={headshotUrl(playerId)}
            alt=""
            className="w-8 h-6 rounded object-cover shrink-0 bg-white/5"
            onError={(e) => {
              e.currentTarget.style.display = 'none'
            }}
          />
        ) : (
          <div className="w-8 h-6 rounded bg-white/5 shrink-0" />
        )}
        <div className="min-w-0">
          <div className="text-sm font-medium text-ink-200 truncate">{name}</div>
          {subtitle ? <div className="text-[11px] text-ink-500">{subtitle}</div> : null}
        </div>
      </div>
      <div className={`text-sm font-bold tabular-nums shrink-0 ${points !== undefined ? pointsColor(points) : 'text-ink-400'}`}>
        {trailing}
      </div>
    </div>
  )
}
