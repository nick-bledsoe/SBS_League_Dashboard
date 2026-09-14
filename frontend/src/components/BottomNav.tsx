import type { LucideIcon } from 'lucide-react'
import { NavLink } from 'react-router-dom'

interface NavItem {
  to: string
  label: string
  icon: LucideIcon
  end: boolean
}

/** Fixed bottom tab bar shown only below the `sm` breakpoint — mobile's small width
 * doesn't have room for a horizontal nav row next to the logo/title, and cramming
 * icon-only buttons up top reads as an afterthought. A bottom tab bar (the pattern
 * most sports/score apps use, ESPN's own app included) gives each tab a proper
 * touch target instead. */
export function BottomNav({ items }: { items: NavItem[] }) {
  return (
    <nav
      className="sm:hidden fixed bottom-0 inset-x-0 z-20 bg-surface/95 backdrop-blur-md border-t border-line"
      style={{ transform: 'translateZ(0)' }}
    >
      {/* h-16 matches the header's height exactly, so the two bars read as matching
       * bookends instead of the bottom bar just being whatever its padding added up to. */}
      <div className="h-16 flex items-stretch justify-around">
        {items.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex flex-1 flex-col items-center justify-center gap-1 text-[11px] font-medium transition-colors ${
                isActive ? 'text-brand-400' : 'text-ink-500'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon className="w-5 h-5" strokeWidth={isActive ? 2.5 : 2} />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </div>
      <div style={{ height: 'env(safe-area-inset-bottom)' }} />
    </nav>
  )
}
