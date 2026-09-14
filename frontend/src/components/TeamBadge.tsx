interface TeamBadgeProps {
  name: string
  owner?: string
  logo?: string
  bold?: boolean
  size?: number
  subtitle?: string
}

export function TeamBadge({ name, owner, logo, bold, size = 32, subtitle }: TeamBadgeProps) {
  return (
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
}
