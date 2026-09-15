import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api } from './client'
import type {
  BoxscoreMatchup,
  LeagueInfo,
  PlayerDetail,
  PlayerRanking,
  PlayoffMatchupCreate,
  PlayoffMatchupRead,
  PlayoffMatchupUpdate,
  PlayoffStandingsRow,
  RegularMatchup,
  ScheduleGame,
  StandingsRow,
  TeamDetail,
  TeamSummary,
  WeeklyStats,
} from './types'

export function useCurrentWeek() {
  return useQuery({
    queryKey: ['current-week'],
    queryFn: () => api.get<{ week: number }>('/current-week'),
  })
}

export function useSeasons() {
  return useQuery({
    queryKey: ['seasons'],
    queryFn: () => api.get<{ seasons: number[]; current_season: number }>('/seasons'),
  })
}

export function useLeagues() {
  return useQuery({
    queryKey: ['leagues'],
    queryFn: () => api.get<LeagueInfo[]>('/leagues'),
  })
}

export function useStandings() {
  return useQuery({
    queryKey: ['standings'],
    queryFn: () => api.get<StandingsRow[]>('/standings'),
  })
}

export function usePlayoffStandings() {
  return useQuery({
    queryKey: ['standings', 'playoffs'],
    queryFn: () => api.get<PlayoffStandingsRow[]>('/standings/playoffs'),
  })
}

export function useTeams() {
  return useQuery({
    queryKey: ['teams'],
    queryFn: () => api.get<TeamSummary[]>('/teams'),
  })
}

export function useTeam(leagueId: string | undefined, teamId: number | undefined) {
  return useQuery({
    queryKey: ['team', leagueId, teamId],
    queryFn: () => api.get<TeamDetail>(`/teams/${leagueId}/${teamId}`),
    enabled: Boolean(leagueId) && teamId !== undefined,
  })
}

export function useTeamSchedule(leagueId: string | undefined, teamId: number | undefined) {
  return useQuery({
    queryKey: ['team-schedule', leagueId, teamId],
    queryFn: () => api.get<ScheduleGame[]>(`/teams/${leagueId}/${teamId}/schedule`),
    enabled: Boolean(leagueId) && teamId !== undefined,
  })
}

export function useMatchups(week: number | undefined) {
  return useQuery({
    queryKey: ['matchups', week],
    queryFn: () => api.get<RegularMatchup[]>(`/matchups?week=${week}`),
    enabled: week !== undefined,
  })
}

/** All weeks of regular-season matchups across all leagues — powers weekly high
 * scores and the week selector, which need the full season, not just one week. */
export function useAllMatchups() {
  return useQuery({
    queryKey: ['matchups', 'all'],
    queryFn: () => api.get<RegularMatchup[]>('/matchups'),
  })
}

export function useBoxscore(leagueId: string | undefined, week: number | undefined) {
  return useQuery({
    queryKey: ['boxscore', leagueId, week],
    queryFn: () => api.get<BoxscoreMatchup[]>(`/matchups/${leagueId}/${week}/boxscore`),
    enabled: Boolean(leagueId) && week !== undefined,
  })
}

export function useWeeklyStats(week: number | undefined, phase: 'regular' | 'playoff', season?: number) {
  return useQuery({
    queryKey: ['weekly-stats', week, phase, season],
    queryFn: () =>
      api.get<WeeklyStats>(`/weeks/${week}/stats?phase=${phase}${season ? `&season=${season}` : ''}`),
    enabled: week !== undefined,
  })
}

export function usePlayoffMatchups(season: number | undefined, week?: number) {
  return useQuery({
    queryKey: ['playoff-matchups', season, week],
    queryFn: () =>
      api.get<PlayoffMatchupRead[]>(`/playoff-matchups?season=${season}${week ? `&week=${week}` : ''}`),
    enabled: season !== undefined,
  })
}

export function useCreatePlayoffMatchup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: PlayoffMatchupCreate) => api.post<PlayoffMatchupRead>('/playoff-matchups', payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['playoff-matchups'] }),
  })
}

export function useUpdatePlayoffMatchup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: PlayoffMatchupUpdate }) =>
      api.patch<PlayoffMatchupRead>(`/playoff-matchups/${id}`, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['playoff-matchups'] }),
  })
}

export function useDeletePlayoffMatchup() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.delete<void>(`/playoff-matchups/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['playoff-matchups'] }),
  })
}

export function usePlayerDetail(leagueId: string | undefined, playerId: string | undefined) {
  return useQuery({
    queryKey: ['player-detail', leagueId, playerId],
    queryFn: () => api.get<PlayerDetail>(`/players/${playerId}?league_id=${leagueId}`),
    enabled: Boolean(leagueId) && Boolean(playerId),
  })
}

export function usePlayerRankings() {
  return useQuery({
    queryKey: ['player-rankings'],
    queryFn: () => api.get<PlayerRanking[]>('/players/rankings'),
  })
}
