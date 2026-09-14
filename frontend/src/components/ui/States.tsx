import { Loader2, type LucideIcon } from 'lucide-react'

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-ink-500 py-6">
      <Loader2 className="w-4 h-4 animate-spin" />
      {label}
    </div>
  )
}

export function EmptyState({ icon: Icon, label }: { icon?: LucideIcon; label: string }) {
  return (
    <div className="flex flex-col items-center gap-2 text-center text-sm text-ink-500 py-8 border border-dashed border-line rounded-xl">
      {Icon ? <Icon className="w-6 h-6 text-ink-600" /> : null}
      {label}
    </div>
  )
}
