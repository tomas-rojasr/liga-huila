import api from "../../api/axios.config";

export interface User {
  user_id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export async function getUsersService(): Promise<User[]> {
  const { data } = await api.get<User[]>("/users");
  return data;
}

export async function createUserService(payload: Partial<User> & { password: string }): Promise<User> {
  const { data } = await api.post<User>("/users", payload);
  return data;
}

export async function updateUserService(id: string, payload: Partial<User>): Promise<User> {
  const { data } = await api.put<User>(`/users/${id}`, payload);
  return data;
}

export async function deleteUserService(id: string): Promise<void> {
  await api.delete(`/users/${id}`);
}
