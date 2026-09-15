import { Link } from 'react-router-dom'

import type { PlayoffStandingsRow, StandingsRow } from '../api/types'
import { SeedBadge } from './ui/Badge'
import { Card } from './ui/Section'

export function PlayoffStandingsTable({ rows }: { rows: PlayoffStandingsRow[] }) {
  return (
    <Card className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-[11px] uppercase tracking-wide text-ink-500 border-b border-line">
            <th className="py-3 pl-4 pr-2 font-semibold text-center">Seed</th>
            <th className="py-3 pr-2 font-semibold">Team</th>
            <th className="py-3 pr-2 font-semibold text-center hidden sm:table-cell">Division</th>
            <th className="py-3 pr-2 font-semibold text-center">W</th>
            <th className="py-3 pr-2 font-semibold text-center hidden sm:table-cell">GB</th>
            <th className="py-3 pr-2 font-semibold text-center">PF</th>
            <th className="py-3 pr-4 font-semibold text-center hidden md:table-cell">Streak</th>
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 18).map((row) => (
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

export function DivisionStandingsTable({ rows }: { rows: StandingsRow[] }) {
  return (
    <Card className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-[11px] uppercase tracking-wide text-ink-500 border-b border-line">
            <th className="py-2.5 pl-4 pr-2 font-semibold text-center">#</th>
            <th className="py-2.5 pr-2 font-semibold">Team</th>
            <th className="py-2.5 pr-2 font-semibold text-center">Record</th>
            <th className="py-2.5 pr-2 font-semibold text-center">PF</th>
            <th className="py-2.5 pr-2 font-semibold text-center">PA</th>
            <th className="py-2.5 pr-4 font-semibold text-center">Moves</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
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
