import { ChevronDown } from 'lucide-react'
import type { SelectHTMLAttributes } from 'react'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
}

export function Select({ label, className = '', ...props }: SelectProps) {
  const select = (
    <div className="relative inline-block">
      <select
        {...props}
        className={`appearance-none bg-surface-raised border border-line hover:border-line-strong rounded-lg pl-3 pr-9 py-2 text-sm font-medium text-ink-100 transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500/50 focus:border-brand-500 ${className}`}
      />
      <ChevronDown className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-500" />
    </div>
  )

  if (!label) return select

  return (
    <label className="block">
      <span className="block text-xs font-semibold uppercase tracking-wide text-ink-500 mb-1.5">{label}</span>
      {select}
    </label>
  )
}
