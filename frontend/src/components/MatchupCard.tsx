import { ChevronDown, Trophy } from 'lucide-react'
import type { ReactNode } from 'react'

import { formatScore } from '../lib/format'
import { TeamBadge } from './TeamBadge'
import { Badge } from './ui/Badge'
import { Card } from './ui/Section'

export interface MatchupCardSide {
  name: string
  owner?: string
  logo?: string
  score: number | string | null
  winning: boolean
  subtitle?: string
  leagueId?: string
  teamId?: number
}

interface MatchupCardProps {
  home: MatchupCardSide
  away: MatchupCardSide
  badge?: { label: string; color: string }
  expandLabel?: string
  children?: ReactNode
}

function ScoreRow({ side }: { side: MatchupCardSide }) {
  return (
    <div className={`flex items-center justify-between gap-3 px-4 py-3 ${side.winning ? 'bg-brand-500/[0.06]' : ''}`}>
      <TeamBadge
        name={side.name}
        owner={side.owner}
        logo={side.logo}
        bold={side.winning}
        subtitle={side.subtitle}
        leagueId={side.leagueId}
        teamId={side.teamId}
      />
      <div className={`text-2xl font-display font-bold tabular-nums shrink-0 ${side.winning ? 'text-good' : 'text-ink-500'}`}>
        {formatScore(side.score)}
      </div>
    </div>
  )
}

/** Shared team-vs-team card used on Home, Scoreboard, and Admin — the single place
 * this markup lives, instead of being copy-pasted across three pages. */
export function MatchupCard({ home, away, badge, expandLabel = 'Top Scorers', children }: MatchupCardProps) {
  return (
    <Card className="mb-3 overflow-hidden transition-colors hover:border-line-strong">
      {badge ? (
        <div className="flex justify-center pt-3">
          <Badge label={badge.label} color={badge.color} />
        </div>
      ) : null}

      <div className="divide-y divide-line/60">
        <ScoreRow side={home} />
        <ScoreRow side={away} />
      </div>

      {children ? (
        <details className="group border-t border-line">
          <summary className="cursor-pointer select-none flex items-center justify-between px-4 py-2.5 text-xs font-semibold text-brand-400 hover:bg-white/[0.02]">
            <span className="flex items-center gap-1.5">
              <Trophy className="w-3.5 h-3.5" />
              {expandLabel}
            </span>
            <ChevronDown className="w-3.5 h-3.5 transition-transform group-open:rotate-180" />
          </summary>
          <div className="px-4 pb-4 pt-1">{children}</div>
        </details>
      ) : null}
    </Card>
  )
}
