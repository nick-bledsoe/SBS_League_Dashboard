export function headshotUrl(playerId: string): string {
  if (!playerId) return ''
  return `https://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/${playerId}.png&w=96&h=70&cb=1`
}

export function pointsColor(points: number): string {
  if (points >= 5) return 'text-good'
  if (points >= 0) return 'text-ink-400'
  return 'text-bad'
}

export function formatScore(score: number | string | null): string {
  if (score === null || score === undefined) return '---'
  if (typeof score === 'string') return score
  return score.toFixed(1)
}
