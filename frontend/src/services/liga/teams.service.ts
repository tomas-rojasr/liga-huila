import api from "../../api/axios.config";

export interface Team {
  team_id: string;
  club_id: string | null;
  name: string;
  category: string;
  is_active: boolean;
  created_at: string;
  club_name: string | null;
}

export async function getTeamsService(clubId?: string, category?: string): Promise<Team[]> {
  const { data } = await api.get<Team[]>("/teams", { params: { club_id: clubId, category } });
  return data;
}

export async function getTeamService(id: string): Promise<Team> {
  const { data } = await api.get<Team>(`/teams/${id}`);
  return data;
}

export async function createTeamService(payload: Partial<Team>): Promise<Team> {
  const { data } = await api.post<Team>("/teams", payload);
  return data;
}

export async function updateTeamService(id: string, payload: Partial<Team>): Promise<Team> {
  const { data } = await api.put<Team>(`/teams/${id}`, payload);
  return data;
}

export async function deleteTeamService(id: string): Promise<void> {
  await api.delete(`/teams/${id}`);
}
