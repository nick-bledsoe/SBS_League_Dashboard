import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import type { PlayoffStandingsRow, StandingsRow } from '../api/types'
import { SeedBadge } from './ui/Badge'
import { Card } from './ui/Section'
import { SortableHeader, type SortDirection } from './ui/SortableHeader'

type PlayoffSortKey = 'team' | 'division' | 'wins' | 'gb' | 'points_for'

// Ascending always means "natural numeric/alphabetical order" — the direction map below
// just decides which end looks best sitting at the top on the very first click.
const PLAYOFF_COMPARATORS: Record<PlayoffSortKey, (a: PlayoffStandingsRow, b: PlayoffStandingsRow) => number> = {
  team: (a, b) => a.team.team_name.localeCompare(b.team.team_name),
  division: (a, b) => a.team.league_name.localeCompare(b.team.league_name),
  wins: (a, b) => a.wins - b.wins,
  gb: (a, b) => a.gb - b.gb,
  points_for: (a, b) => a.points_for - b.points_for,
}

const PLAYOFF_DEFAULT_DIRECTION: Record<PlayoffSortKey, SortDirection> = {
  team: 'asc',
  division: 'asc',
  wins: 'desc',
  gb: 'asc',
  points_for: 'desc',
}

export function PlayoffStandingsTable({ rows }: { rows: PlayoffStandingsRow[] }) {
  // null = no column sort applied yet — show the incoming seed order the backend already
  // computed (division winners first, tiebreakers applied, etc.), not a simplistic re-sort.
  const [sort, setSort] = useState<{ key: PlayoffSortKey; direction: SortDirection } | null>(null)

  const handleSort = (key: PlayoffSortKey) => {
    setSort((prev) =>
      prev && prev.key === key
        ? { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: PLAYOFF_DEFAULT_DIRECTION[key] },
    )
  }

  const sorted = useMemo(() => {
    if (!sort) return rows
    const result = [...rows].sort(PLAYOFF_COMPARATORS[sort.key])
    if (sort.direction === 'desc') result.reverse()
    return result
  }, [rows, sort])

  return (
    <Card className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-[11px] uppercase tracking-wide text-ink-500 border-b border-line">
            <th className="py-3 pl-4 pr-2 font-semibold text-center">Seed</th>
            <SortableHeader
              label="Team"
              sortKey="team"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              className="py-3 pr-2"
            />
            <SortableHeader
              label="Division"
              sortKey="division"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              align="center"
              className="py-3 pr-2 hidden sm:table-cell"
            />
            <SortableHeader
              label="W"
              sortKey="wins"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              align="center"
              className="py-3 pr-2"
            />
            <SortableHeader
              label="GB"
              sortKey="gb"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              align="center"
              className="py-3 pr-2 hidden sm:table-cell"
            />
            <SortableHeader
              label="PF"
              sortKey="points_for"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              align="center"
              className="py-3 pr-2"
            />
            <th className="py-3 pr-4 font-semibold text-center hidden md:table-cell">Streak</th>
          </tr>
        </thead>
        <tbody>
          {sorted.slice(0, 18).map((row) => (
            <tr
              key={`${row.team.league_name}-${row.team.team_name}`}
              className="border-b border-line/60 last:border-0 hover:bg-white/[0.02] transition-colors"
            >
              <td className="py-2.5 pl-4 pr-2 text-center">
                <SeedBadge seed={row.rank} />
              </td>
              <td className="py-2.5 pr-2 font-medium text-ink-100">
                <Link to={`/teams/${row.team.league_id}/${row.team.team_id}`} className="hover:text-brand-400">
                  {row.team.team_name}
                </Link>
                {row.team.owner ? <span className="ml-2 text-xs font-normal text-ink-500">({row.team.owner})</span> : null}
              </td>
              <td className="py-2.5 pr-2 text-center text-ink-400 hidden sm:table-cell">{row.team.league_name}</td>
              <td className="py-2.5 pr-2 text-center tabular-nums">{row.wins.toFixed(1)}</td>
              <td className="py-2.5 pr-2 text-center tabular-nums text-ink-400 hidden sm:table-cell">{row.gb.toFixed(1)}</td>
              <td className="py-2.5 pr-2 text-center tabular-nums">{row.points_for.toFixed(1)}</td>
              <td className="py-2.5 pr-4 text-center text-ink-400 hidden md:table-cell">{row.streak}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  )
}

type DivisionSortKey = 'team' | 'record' | 'points_for' | 'points_against' | 'transactions'

const DIVISION_COMPARATORS: Record<DivisionSortKey, (a: StandingsRow, b: StandingsRow) => number> = {
  team: (a, b) => a.team.team_name.localeCompare(b.team.team_name),
  // Ascending = worst record first: fewer wins first, and among equal wins, more losses first.
  record: (a, b) => a.wins - b.wins || b.losses - a.losses,
  points_for: (a, b) => a.points_for - b.points_for,
  points_against: (a, b) => a.points_against - b.points_against,
  transactions: (a, b) => a.transactions - b.transactions,
}

const DIVISION_DEFAULT_DIRECTION: Record<DivisionSortKey, SortDirection> = {
  team: 'asc',
  record: 'desc',
  points_for: 'desc',
  points_against: 'desc',
  transactions: 'desc',
}

export function DivisionStandingsTable({ rows }: { rows: StandingsRow[] }) {
  // null = no column sort applied yet — show the incoming rank order the backend already
  // computed, not a simplistic re-sort (which can disagree on tiebreakers).
  const [sort, setSort] = useState<{ key: DivisionSortKey; direction: SortDirection } | null>(null)

  const handleSort = (key: DivisionSortKey) => {
    setSort((prev) =>
      prev && prev.key === key
        ? { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: DIVISION_DEFAULT_DIRECTION[key] },
    )
  }

  const sorted = useMemo(() => {
    if (!sort) return rows
    const result = [...rows].sort(DIVISION_COMPARATORS[sort.key])
    if (sort.direction === 'desc') result.reverse()
    return result
  }, [rows, sort])

  return (
    <Card className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-[11px] uppercase tracking-wide text-ink-500 border-b border-line">
            <th className="py-2.5 pl-4 pr-2 font-semibold text-center">#</th>
            <SortableHeader
              label="Team"
              sortKey="team"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              className="py-2.5 pr-2"
            />
            <SortableHeader
              label="Record"
              sortKey="record"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              align="center"
              className="py-2.5 pr-2"
            />
            <SortableHeader
              label="PF"
              sortKey="points_for"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              align="center"
              className="py-2.5 pr-2"
            />
            <SortableHeader
              label="PA"
              sortKey="points_against"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              align="center"
              className="py-2.5 pr-2"
            />
            <SortableHeader
              label="Moves"
              sortKey="transactions"
              activeKey={sort?.key ?? null}
              direction={sort?.direction ?? 'asc'}
              onSort={handleSort}
              align="center"
              className="py-2.5 pr-4"
            />
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => (
            <tr key={row.team.team_name} className="border-b border-line/60 last:border-0 hover:bg-white/[0.02] transition-colors">
              <td className="py-2 pl-4 pr-2 text-center text-ink-500 tabular-nums">{row.league_rank}</td>
              <td className="py-2 pr-2 font-medium text-ink-100">
                <Link to={`/teams/${row.team.league_id}/${row.team.team_id}`} className="hover:text-brand-400">
                  {row.team.team_name}
                </Link>
                {row.team.owner ? <span className="ml-2 text-xs font-normal text-ink-500">({row.team.owner})</span> : null}
              </td>
              <td className="py-2 pr-2 text-center text-ink-400 tabular-nums">
                {row.wins}-{row.losses}
              </td>
              <td className="py-2 pr-2 text-center tabular-nums">{row.points_for.toFixed(1)}</td>
              <td className="py-2 pr-2 text-center tabular-nums">{row.points_against.toFixed(1)}</td>
              <td className="py-2 pr-4 text-center tabular-nums">{row.transactions}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  )
}
