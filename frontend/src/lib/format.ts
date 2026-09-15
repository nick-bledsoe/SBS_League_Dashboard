export function headshotUrl(playerId: string): string {
  if (!playerId) return ''
  return `https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/${playerId}.png&w=96&h=70&cb=1`
}

export function pointsColor(points: number): string {
  if (points >= 5) return 'text-good'
  if (points >= 0) return 'text-ink-400'
  return 'text-bad'
}

const NAME_SUFFIXES = new Set(['jr', 'jr.', 'sr', 'sr.', 'ii', 'iii', 'iv', 'v'])

/** Last name only, for tight layouts (e.g. a matchup card's "Top Scorers" preview).
 * Skips trailing suffixes like "Jr." or "III" so they don't get mistaken for the surname. */
export function lastName(fullName: string): string {
  const parts = fullName.trim().split(/\s+/)
  while (parts.length > 1 && NAME_SUFFIXES.has(parts[parts.length - 1].toLowerCase())) {
    parts.pop()
  }
  return parts[parts.length - 1] || fullName
}

export function formatScore(score: number | string | null): string {
  if (score === null || score === undefined) return '---'
  if (typeof score === 'string') return score
  return score.toFixed(1)
}

/** Matches ESPN's own news-card date format, e.g. "WED, SEP 9, 11:13 PM". */
export function formatNewsDate(iso: string): string {
  if (!iso) return ''
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return ''
  return date
    .toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    })
    .toUpperCase()
}

/** ESPN displays wire-service sources with a .com suffix (e.g. "ROTOWIRE.COM");
 * anything else (their own staff bylines, "Media", etc.) just gets uppercased. */
export function formatNewsSource(source: string): string {
  if (!source) return ''
  return source.toLowerCase() === 'rotowire' ? 'ROTOWIRE.COM' : source.toUpperCase()
}
