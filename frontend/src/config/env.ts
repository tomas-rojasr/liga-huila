interface EnvVars {
  VITE_API_URL: string;
}

function getEnv(): EnvVars {
  return {
    VITE_API_URL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
  };
}

export const env = getEnv();
