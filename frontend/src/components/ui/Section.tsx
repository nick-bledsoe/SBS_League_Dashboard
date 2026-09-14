import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

interface SectionProps {
  title: string
  subtitle?: string
  icon?: LucideIcon
  action?: ReactNode
  children: ReactNode
}

export function Section({ title, subtitle, icon: Icon, action, children }: SectionProps) {
  return (
    <section>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-4 mb-4">
        <div>
          <h2 className="font-display flex items-center gap-2 text-xl font-bold text-ink-100">
            {Icon ? <Icon className="w-5 h-5 text-brand-400" strokeWidth={2.25} /> : null}
            {title}
          </h2>
          {subtitle ? <p className="text-sm text-ink-500 mt-1">{subtitle}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </section>
  )
}

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <div className={`rounded-xl border border-line bg-surface/70 backdrop-blur-sm ${className}`}>{children}</div>
  )
}
