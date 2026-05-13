import api from "../../api/axios.config";

export interface Player {
  player_id: string;
  team_id: string | null;
  first_name: string;
  last_name: string;
  birth_date: string;
  category: string;
  document_type: string;
  document_number: string;
  nationality: string;
  position: string | null;
  photo_url: string | null;
  status: string;
  created_at: string;
  team_name: string | null;
}

export async function getPlayersService(teamId?: string, category?: string, status?: string): Promise<Player[]> {
  const { data } = await api.get<Player[]>("/players", { params: { team_id: teamId, category, status } });
  return data;
}

export async function getPlayerService(id: string): Promise<Player> {
  const { data } = await api.get<Player>(`/players/${id}`);
  return data;
}

export async function createPlayerService(payload: Partial<Player>): Promise<Player> {
  const { data } = await api.post<Player>("/players", payload);
  return data;
}

export async function updatePlayerService(id: string, payload: Partial<Player>): Promise<Player> {
  const { data } = await api.put<Player>(`/players/${id}`, payload);
  return data;
}

export async function deletePlayerService(id: string): Promise<void> {
  await api.delete(`/players/${id}`);
}
