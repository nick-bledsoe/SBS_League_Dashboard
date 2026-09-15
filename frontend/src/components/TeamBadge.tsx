import { Link } from 'react-router-dom'

interface TeamBadgeProps {
  name: string
  owner?: string
  logo?: string
  bold?: boolean
  size?: number
  subtitle?: string
  /** When both are given, the badge links to that team's page (/teams/:leagueId/:teamId). */
  leagueId?: string
  teamId?: number
}

export function TeamBadge({ name, owner, logo, bold, size = 32, subtitle, leagueId, teamId }: TeamBadgeProps) {
  const content = (
    <div className="flex items-center gap-3 min-w-0">
      {logo ? (
        <img
          src={logo}
          alt=""
          style={{ width: size, height: size }}
          className="rounded-full object-cover ring-1 ring-white/10 shrink-0"
          onError={(e) => {
            e.currentTarget.style.display = 'none'
          }}
        />
      ) : (
        <div
          style={{ width: size, height: size }}
          className="rounded-full bg-white/5 ring-1 ring-white/10 shrink-0"
        />
      )}
      <div className="min-w-0">
        <div className={`truncate ${bold ? 'font-bold text-ink-100' : 'font-medium text-ink-200'}`}>
          {name}
          {owner ? <span className="ml-2 text-xs font-normal text-ink-500">{owner}</span> : null}
        </div>
        {subtitle ? <div className="text-xs text-ink-500 mt-0.5">{subtitle}</div> : null}
      </div>
    </div>
  )

  if (leagueId && teamId !== undefined) {
    return (
      <Link
        to={`/teams/${leagueId}/${teamId}`}
        className="hover:opacity-80 transition-opacity min-w-0"
        onClick={(e) => e.stopPropagation()}
      >
        {content}
      </Link>
    )
  }

  return content
}
