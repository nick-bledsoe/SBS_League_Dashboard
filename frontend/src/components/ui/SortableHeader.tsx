import { ChevronDown, ChevronUp, ChevronsUpDown } from 'lucide-react'

export type SortDirection = 'asc' | 'desc'

interface SortableHeaderProps<K extends string> {
  label: string
  sortKey: K
  activeKey: K | null
  direction: SortDirection
  onSort: (key: K) => void
  align?: 'left' | 'center' | 'right'
  className?: string
}

/** A <th> whose label toggles sort on click, with a chevron showing the current state. */
export function SortableHeader<K extends string>({
  label,
  sortKey,
  activeKey,
  direction,
  onSort,
  align = 'left',
  className = '',
}: SortableHeaderProps<K>) {
  const active = activeKey === sortKey
  const Icon = active ? (direction === 'asc' ? ChevronUp : ChevronDown) : ChevronsUpDown
  const justify = align === 'center' ? 'justify-center' : align === 'right' ? 'justify-end' : 'justify-start'

  return (
    <th className={`font-semibold ${className}`}>
      <button
        type="button"
        onClick={() => onSort(sortKey)}
        className={`flex items-center gap-1 w-full select-none hover:text-ink-100 transition-colors ${justify} ${
          active ? 'text-brand-400' : ''
        }`}
      >
        {label}
        <Icon className="w-3 h-3 shrink-0" />
      </button>
    </th>
  )
}
