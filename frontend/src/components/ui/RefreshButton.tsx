import { useQueryClient } from '@tanstack/react-query'
import { RefreshCw } from 'lucide-react'
import { useState } from 'react'

export function RefreshButton({ label = 'Refresh' }: { label?: string }) {
  const queryClient = useQueryClient()
  const [spinning, setSpinning] = useState(false)

  return (
    <button
      onClick={() => {
        setSpinning(true)
        queryClient.invalidateQueries().finally(() => setTimeout(() => setSpinning(false), 500))
      }}
      className="inline-flex items-center gap-2 px-3.5 py-2 text-sm font-medium rounded-lg border border-line bg-surface-raised text-ink-300 hover:text-ink-100 hover:border-line-strong transition-colors"
    >
      <RefreshCw className={`w-3.5 h-3.5 ${spinning ? 'animate-spin' : ''}`} />
      {label}
    </button>
  )
}
