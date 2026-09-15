export interface TeamRef {
  league_id: string
  league_name: string
  team_id: number
  team_name: string
  owner: string
}

export interface LeagueInfo {
  name: string
  id: string
}

export interface StandingsRow {
  rank: number
  league_rank: number
  team: TeamRef
  wins: number
  losses: number
  points_for: number
  points_against: number
  transactions: number
  streak: string
}

export interface PlayoffStandingsRow {
  rank: number
  team: TeamRef
  wins: number
  losses: number
  points_for: number
  points_against: number
  streak: string
  gb: number
}

export interface RosterPlayer {
  player_id: string
  name: string
  position: string
  nfl_team: string
  nfl_logo: string
  positional_rank: string
  sort_order: number
}

export interface TeamSummary {
  team: TeamRef
  wins: number
  losses: number
}

export interface TeamDetail {
  team: TeamRef
  wins: number
  losses: number
  seed: string
  logo: string
  roster: RosterPlayer[]
}

export interface ScheduleGame {
  week: number
  opponent: TeamRef
  opponent_logo: string
  location: 'vs' | '@'
  result: 'W' | 'L' | 'T' | '-'
  result_color: string
  team_score: number | null
  opp_score: number | null
  is_current: boolean
  game_type: string
}

export interface BoxscorePlayer {
  player_id: string
  name: string
  position: string
  nfl_team: string
  points: number
}

export interface BoxscoreTeam {
  team: TeamRef
  logo: string
  total_points: number
  roster: BoxscorePlayer[]
}

export interface BoxscoreMatchup {
  week: number
  home: BoxscoreTeam
  away: BoxscoreTeam
}

export interface RegularMatchup {
  league_name: string
  week: number
  home: TeamRef
  home_logo: string
  home_score: number
  away: TeamRef
  away_logo: string
  away_score: number
}

export interface ParticipantInput {
  league_id: string
  league_name: string
  team_id: number
  team_name: string
}

export const MATCHUP_TYPES = ['Quarterfinal', 'Semifinal', '3rd Place', 'Championship'] as const
export type MatchupType = (typeof MATCHUP_TYPES)[number]

export interface PlayoffMatchupCreate {
  season: number
  week: number
  round_type: MatchupType
  home: ParticipantInput
  away: ParticipantInput
}

export interface PlayoffMatchupUpdate {
  round_type: MatchupType
}

export interface ParticipantRead {
  team: TeamRef
  wins: number
  losses: number
  seed: string
  score: number | null
  logo: string
  winning: boolean
}

export interface PlayoffMatchupRead {
  id: number
  season: number
  week: number
  round_type: string
  home: ParticipantRead
  away: ParticipantRead
}

export interface TopPerformer {
  name: string
  nfl_team: string
  position: string
  points: number
  player_id: string
  teams: string[]
  team_logos: string[]
}

export interface LeagueLeader {
  league_name: string
  team: TeamRef
  logo: string
  score: number
}

export interface CloseGame {
  league_name: string
  team_a: string
  team_a_ref: TeamRef
  team_b: string
  team_b_ref: TeamRef
  score_a: number
  score_b: number
  margin: number
}

export interface Blowout {
  league_name: string
  winner: string
  winner_ref: TeamRef
  winner_score: number
  loser: string
  loser_ref: TeamRef
  loser_score: number
  margin: number
}

export interface WeeklySummary {
  total_points: number
  average_points: number
  highest_scoring_league: string | null
  highest_scoring_league_points: number
  lowest_scoring_league: string | null
  lowest_scoring_league_points: number
}

export interface WeeklyStats {
  week: number
  top_performers: TopPerformer[]
  league_leaders: LeagueLeader[]
  close_games: CloseGame[]
  blowouts: Blowout[]
  summary: WeeklySummary
}

export interface PlayerNewsItem {
  id: number | null
  headline: string
  description: string
  story: string
  source: string
  published: string
}

export interface WeeklyPoints {
  week: number
  points: number
}

export interface StatSeasonRow {
  year: number | null
  team: string
  values: string[]
}

export interface StatCategory {
  name: string
  display_name: string
  labels: string[]
  seasons: StatSeasonRow[]
}

export interface PlayerDetail {
  player_id: string
  name: string
  position: string
  nfl_team: string
  nfl_logo: string
  weekly_points: WeeklyPoints[]
  news: PlayerNewsItem[]
  stats: StatCategory[]
}

export interface PlayerRanking {
  player_id: string
  name: string
  position: string
  nfl_team: string
  league_id: string
  total_points: number
  games_played: number
  avg_points: number
}
