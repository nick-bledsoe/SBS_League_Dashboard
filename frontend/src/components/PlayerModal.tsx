import { BarChart3, Newspaper, TrendingUp, X } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

import { usePlayerDetail } from '../api/queries'
import type { PlayerNewsItem, StatCategory } from '../api/types'
import { formatNewsDate, formatNewsSource, headshotUrl } from '../lib/format'
import { Card } from './ui/Section'
import { Select } from './ui/Select'
import { EmptyState, LoadingState } from './ui/States'

interface PlayerModalProps {
  leagueId: string
  playerId: string
  onClose: () => void
}

export function PlayerModal({ leagueId, playerId, onClose }: PlayerModalProps) {
  const { data: player, isLoading } = usePlayerDetail(leagueId, playerId)
  const [selectedYear, setSelectedYear] = useState<number | null>(null)

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    document.body.style.overflow = 'hidden'
    return () => {
      window.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = ''
    }
  }, [onClose])

  const availableYears = useMemo(() => {
    const years = new Set<number>()
    player?.stats.forEach((c) => c.seasons.forEach((s) => s.year && years.add(s.year)))
    return Array.from(years).sort((a, b) => b - a)
  }, [player])

  useEffect(() => {
    if (availableYears.length > 0 && selectedYear === null) setSelectedYear(availableYears[0])
  }, [availableYears, selectedYear])

  const maxPoints = player ? Math.max(1, ...player.weekly_points.map((w) => w.points)) : 1
  const categoriesForYear = player?.stats.filter((c) => c.seasons.some((s) => s.year === selectedYear)) ?? []

  return (
    <div
      className="fixed inset-0 z-50 flex items-start sm:items-center justify-center bg-black/70 backdrop-blur-sm p-0 sm:p-4 overflow-y-auto"
      onClick={onClose}
    >
      <div
        className="w-full sm:max-w-lg sm:rounded-2xl bg-surface border border-line min-h-full sm:min-h-0 sm:my-8 flex flex-col sm:max-h-[85vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {isLoading || !player ? (
          <div className="p-6">
            <button onClick={onClose} className="float-right text-ink-500 hover:text-ink-100">
              <X className="w-5 h-5" />
            </button>
            <LoadingState label="Loading player…" />
          </div>
        ) : (
          <>
            <div className="shrink-0 flex items-start justify-between gap-4 p-5 border-b border-line">
              <div className="flex items-center gap-3 min-w-0">
                <img
                  src={headshotUrl(player.player_id)}
                  alt=""
                  className="w-16 h-12 rounded-lg object-cover bg-white/5 shrink-0"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none'
                  }}
                />
                <div className="min-w-0">
                  <h2 className="font-display text-lg font-bold text-ink-100 truncate">{player.name}</h2>
                  <div className="flex items-center gap-1.5 text-sm text-ink-400">
                    {player.nfl_logo ? <img src={player.nfl_logo} alt="" className="w-4 h-4" /> : null}
                    {player.nfl_team} · {player.position}
                  </div>
                </div>
              </div>
              <button onClick={onClose} className="text-ink-500 hover:text-ink-100 shrink-0">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="sm:overflow-y-auto p-5 space-y-6">
              <section>
                <h3 className="flex items-center gap-1.5 text-sm font-semibold text-ink-300 mb-3">
                  <TrendingUp className="w-4 h-4 text-brand-400" />
                  Weekly Fantasy Points
                </h3>
                {player.weekly_points.length === 0 ? (
                  <EmptyState label="No games played yet this season" />
                ) : (
                  <div className="flex items-end gap-2 h-24">
                    {player.weekly_points.map((w) => (
                      <div key={w.week} className="flex-1 flex flex-col items-center justify-end gap-1 h-full">
                        <span className="text-xs font-bold tabular-nums text-ink-200">{w.points}</span>
                        <div
                          className="w-full rounded-t bg-brand-500/70"
                          style={{ height: `${Math.max(4, (w.points / maxPoints) * 60)}px` }}
                        />
                        <span className="text-[10px] text-ink-500">W{w.week}</span>
                      </div>
                    ))}
                  </div>
                )}
              </section>

              <section>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="flex items-center gap-1.5 text-sm font-semibold text-ink-300">
                    <BarChart3 className="w-4 h-4 text-brand-400" />
                    Season Stats
                  </h3>
                  {availableYears.length > 1 ? (
                    <Select
                      value={selectedYear ?? ''}
                      onChange={(e) => setSelectedYear(Number(e.target.value))}
                      className="py-1 text-xs"
                    >
                      {availableYears.map((year) => (
                        <option key={year} value={year}>
                          {year}
                        </option>
                      ))}
                    </Select>
                  ) : null}
                </div>
                {categoriesForYear.length === 0 ? (
                  <EmptyState label="No stats available" />
                ) : (
                  <div className="space-y-4">
                    {categoriesForYear.map((category) => (
                      <CategoryStats key={category.name} category={category} year={selectedYear!} />
                    ))}
                  </div>
                )}
              </section>

              <section>
                <h3 className="flex items-center gap-1.5 text-sm font-semibold text-ink-300 mb-3">
                  <Newspaper className="w-4 h-4 text-brand-400" />
                  Recent News
                </h3>
                {player.news.length === 0 ? <EmptyState label="No recent news" /> : <NewsFeed news={player.news} />}
              </section>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

function CategoryStats({ category, year }: { category: StatCategory; year: number }) {
  const row = category.seasons.find((s) => s.year === year)
  if (!row) return null

  return (
    <div>
      <p className="text-xs font-semibold text-ink-500 mb-1.5">
        {category.display_name} <span className="font-normal text-ink-600">· {row.team}</span>
      </p>
      <div className="grid grid-cols-4 gap-1.5">
        {category.labels.map((label, i) => (
          <div key={i} className="rounded-lg bg-surface-raised border border-line px-1.5 py-1.5 text-center">
            <div className="text-[9px] text-ink-500 truncate">{label}</div>
            <div className="text-xs font-semibold tabular-nums text-ink-100">{row.values[i]}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function NewsFeed({ news }: { news: PlayerNewsItem[] }) {
  const [showAll, setShowAll] = useState(false)
  const [latest, ...older] = news

  return (
    <div className="space-y-3">
      <NewsCard item={latest} />
      {showAll ? older.map((item) => <NewsCard key={item.id ?? item.headline} item={item} />) : null}
      {older.length > 0 ? (
        <button
          onClick={() => setShowAll((v) => !v)}
          className="w-full text-center text-xs font-medium text-brand-400 hover:text-brand-300 py-2"
        >
          {showAll ? 'Hide Previous Stories' : `Show Previous Stories (${older.length})`}
        </button>
      ) : null}
    </div>
  )
}

const NEWS_TRUNCATE_LENGTH = 220

function NewsCard({ item }: { item: PlayerNewsItem }) {
  const [expanded, setExpanded] = useState(false)
  const story = item.story || item.description
  const isLong = story.length > NEWS_TRUNCATE_LENGTH
  const shownStory = expanded || !isLong ? story : `${story.slice(0, NEWS_TRUNCATE_LENGTH)}…`

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between mb-2 pb-2 border-b border-dashed border-line">
        <span className="text-[11px] text-ink-500">{formatNewsDate(item.published)}</span>
        <span className="text-[11px] text-ink-500">{formatNewsSource(item.source)}</span>
      </div>
      <p className="text-sm text-ink-100 mb-2 leading-relaxed">{item.headline}</p>
      {story ? (
        <p className="text-sm text-ink-300 leading-relaxed">
          <span className="font-bold text-ink-100">Spin: </span>
          {shownStory}
        </p>
      ) : null}
      {isLong ? (
        <button
          onClick={() => setExpanded((v) => !v)}
          className="w-full text-center text-xs font-medium text-brand-400 hover:text-brand-300 mt-3 pt-2 border-t border-dashed border-line"
        >
          {expanded ? 'Show Less' : 'Show More'}
        </button>
      ) : null}
    </Card>
  )
}
