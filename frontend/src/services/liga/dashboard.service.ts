import api from "../../api/axios.config";

export interface DashboardStats {
  total_clubs: number;
  active_clubs: number;
  total_teams: number;
  total_players: number;
  total_users: number;
  players_by_category: { category: string; count: number }[];
}

export async function getDashboardService(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>("/dashboard");
  return data;
}
