import api from "../../api/axios.config";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  role: string;
  user_id: string;
  email: string;
  full_name: string;
}

export async function loginService(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/login", payload);
  return data;
}

export async function logoutService(): Promise<void> {
  await api.post("/auth/logout");
}

export async function getMeService() {
  const { data } = await api.get("/auth/me");
  return data;
}
