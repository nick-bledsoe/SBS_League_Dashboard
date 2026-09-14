export function Badge({ label, color }: { label: string; color: string }) {
  return (
    <span
      className="inline-block px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wide text-black/80"
      style={{ backgroundColor: color }}
    >
      {label}
    </span>
  )
}

export function SeedBadge({ seed }: { seed: number }) {
  const isIn = seed <= 8
  const isBubble = seed > 8 && seed <= 18
  return (
    <span
      className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold tabular-nums ${
        isIn
          ? 'bg-good/15 text-good ring-1 ring-good/40'
          : isBubble
            ? 'bg-bad/15 text-bad ring-1 ring-bad/30'
            : 'bg-white/5 text-ink-400'
      }`}
    >
      {seed}
    </span>
  )
}
