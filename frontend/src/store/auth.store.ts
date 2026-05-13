import { jwtDecode } from "jwt-decode";
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface JwtPayload {
  sub: string;
  role: string;
  exp: number;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  userId: string;
  email: string;
  fullName: string;
  role: string;
  login: (access: string, refresh: string, email: string, fullName: string, role: string, userId: string) => void;
  logout: () => void;
  setTokens: (access: string, refresh: string) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isHydrated: false,
      userId: "",
      email: "",
      fullName: "",
      role: "",

      login: (access, refresh, email, fullName, role, userId) => {
        try {
          const decoded = jwtDecode<JwtPayload>(access);
          const isExpired = decoded.exp * 1000 < Date.now();
          if (isExpired) return;
        } catch {
          return;
        }
        set({ accessToken: access, refreshToken: refresh, isAuthenticated: true, email, fullName, role, userId });
      },

      logout: () => {
        set({
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          email: "",
          fullName: "",
          role: "",
          userId: "",
        });
        localStorage.removeItem("liga-auth-storage");
      },

      setTokens: (access, refresh) => {
        set({ accessToken: access, refreshToken: refresh, isAuthenticated: true });
      },
    }),
    {
      name: "liga-auth-storage",
      onRehydrateStorage: () => (state) => {
        if (state) state.isHydrated = true;
      },
    }
  )
);
