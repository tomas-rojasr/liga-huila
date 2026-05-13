import api from "../../api/axios.config";

export interface Club {
  club_id: string;
  name: string;
  code: string;
  address: string | null;
  phone: string | null;
  email: string | null;
  logo_url: string | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
}

export async function getClubsService(activeOnly?: boolean): Promise<Club[]> {
  const { data } = await api.get<Club[]>("/clubs", { params: { active_only: activeOnly } });
  return data;
}

export async function getClubService(id: string): Promise<Club> {
  const { data } = await api.get<Club>(`/clubs/${id}`);
  return data;
}

export async function createClubService(payload: Partial<Club>): Promise<Club> {
  const { data } = await api.post<Club>("/clubs", payload);
  return data;
}

export async function updateClubService(id: string, payload: Partial<Club>): Promise<Club> {
  const { data } = await api.put<Club>(`/clubs/${id}`, payload);
  return data;
}

export async function deleteClubService(id: string): Promise<void> {
  await api.delete(`/clubs/${id}`);
}
