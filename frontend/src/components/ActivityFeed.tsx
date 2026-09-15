import { ArrowDownCircle, ArrowUpCircle } from 'lucide-react'
import { Link } from 'react-router-dom'

import type { TransactionEvent } from '../api/types'
import { Card } from './ui/Section'
import { EmptyState } from './ui/States'

const TYPE_LABELS: Record<string, string> = {
  WAIVER: 'Waiver',
  FREEAGENT: 'Free Agent',
  TRADE_ACCEPT: 'Trade',
}

function formatDate(ms: number): string {
  if (!ms) return ''
  return new Date(ms).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

export function ActivityFeed({
  events,
  emptyLabel = 'No roster moves this week',
}: {
  events: TransactionEvent[]
  emptyLabel?: string
}) {
  if (events.length === 0) return <EmptyState label={emptyLabel} />

  return (
    <div className="space-y-2">
      {events.map((event) => (
        <Card key={event.id} className="p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] font-semibold uppercase tracking-wide text-brand-400">
              {TYPE_LABELS[event.type] ?? event.type}
            </span>
            <span className="text-[11px] text-ink-500">{formatDate(event.date)}</span>
          </div>
          <div className="space-y-1.5">
            {event.items.map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-sm min-w-0">
                {item.action === 'ADD' ? (
                  <ArrowUpCircle className="w-3.5 h-3.5 text-good shrink-0" />
                ) : (
                  <ArrowDownCircle className="w-3.5 h-3.5 text-bad shrink-0" />
                )}
                <Link
                  to={`/teams/${item.team.league_id}/${item.team.team_id}`}
                  className="font-medium text-ink-100 hover:text-brand-400 shrink-0"
                >
                  {item.team.owner || item.team.team_name}
                </Link>
                <span className="text-ink-500 shrink-0">{item.action === 'ADD' ? 'added' : 'dropped'}</span>
                <span className="text-ink-200 truncate">{item.player.name}</span>
                <span className="text-[11px] text-ink-600 shrink-0 hidden sm:inline">
                  ({item.player.position} · {item.player.nfl_team})
                </span>
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  )
}
