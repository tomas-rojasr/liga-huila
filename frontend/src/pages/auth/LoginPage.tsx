import { useFormik } from "formik";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import * as Yup from "yup";

import { loginService } from "../../services/liga/auth.service";
import { useAuthStore } from "../../store/auth.store";

const schema = Yup.object({
  email: Yup.string().email("Email inválido").required("Campo requerido"),
  password: Yup.string().min(4, "Mínimo 4 caracteres").required("Campo requerido"),
});

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [serverError, setServerError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const formik = useFormik({
    initialValues: { email: "", password: "" },
    validationSchema: schema,
    onSubmit: async (values, { setSubmitting }) => {
      setServerError(null);
      try {
        const res = await loginService(values);
        login(res.access_token, res.refresh_token, res.email, res.full_name, res.role, res.user_id);
        navigate("/dashboard");
      } catch (err: any) {
        const code = err?.response?.data?.detail?.code;
        const messages: Record<string, string> = {
          INVALID_CREDENTIALS: "Email o contraseña incorrectos",
          USER_INACTIVE: "Tu cuenta está inactiva",
          ACCOUNT_LOCKED: "Cuenta bloqueada temporalmente por múltiples intentos fallidos",
        };
        setServerError(messages[code] ?? "Error al iniciar sesión");
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <div className="min-h-screen flex">
      {/* Panel izquierdo — marca */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-b from-[#1a5c2a] to-[#0f3a19] flex-col items-center justify-center relative overflow-hidden px-12">

        {/* Círculos decorativos de fondo */}
        <div className="absolute top-[-80px] left-[-80px] w-72 h-72 rounded-full bg-white/5" />
        <div className="absolute bottom-[-60px] right-[-60px] w-56 h-56 rounded-full bg-white/5" />
        <div className="absolute top-1/2 right-[-100px] w-80 h-80 rounded-full bg-white/5" />

        {/* Logo */}
        <div className="relative z-10 flex flex-col items-center text-center">
          <div className="w-52 h-52 rounded-full bg-white shadow-2xl flex items-center justify-center mb-8 overflow-hidden">
            <img
              src="/logo-liga.png"
              alt="Liga de Patinaje del Huila"
              className="w-full h-full object-contain p-2"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
                (e.target as HTMLImageElement).parentElement!.innerHTML =
                  `<span class="text-5xl font-black text-[#1a5c2a]">LPH</span>`;
              }}
            />
          </div>

          <h1 className="text-white text-3xl font-black tracking-tight leading-tight mb-2">
            LIGA DE PATINAJE
          </h1>
          <h2 className="text-white text-3xl font-black tracking-tight leading-tight mb-4">
            DEL HUILA
          </h2>

          <div className="flex items-center gap-2 mb-6">
            <div className="h-px w-10 bg-white/40" />
            <p className="text-white/70 text-sm tracking-widest uppercase font-medium">
              Velocidad · Patinaje · Huila
            </p>
            <div className="h-px w-10 bg-white/40" />
          </div>

          <div className="bg-white/10 border border-white/20 rounded-2xl px-8 py-4 text-center">
            <p className="text-white/80 text-sm font-medium">Sistema de Gestión Deportiva</p>
            <p className="text-white/50 text-xs mt-1">Neiva, Huila — Colombia</p>
          </div>
        </div>

        {/* Footer izquierdo */}
        <p className="absolute bottom-6 text-white/30 text-xs">
          © {new Date().getFullYear()} Liga de Patinaje del Huila
        </p>
      </div>

      {/* Panel derecho — formulario */}
      <div className="w-full lg:w-1/2 flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 px-8 py-12">

        {/* Logo solo visible en móvil */}
        <div className="lg:hidden mb-8 flex flex-col items-center">
          <div className="w-20 h-20 rounded-full bg-[#1a5c2a] flex items-center justify-center mb-3 overflow-hidden shadow-lg">
            <img
              src="/logo-liga.png"
              alt="Liga de Patinaje del Huila"
              className="w-full h-full object-contain p-1"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          </div>
          <p className="text-[#1a5c2a] font-bold text-lg">Liga de Patinaje del Huila</p>
        </div>

        <div className="w-full max-w-md">
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Bienvenido</h2>
            <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">
              Ingresa tus credenciales para continuar
            </p>
          </div>

          {serverError && (
            <div className="mb-5 p-3.5 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm flex items-start gap-2">
              <span className="mt-0.5">⚠</span>
              <span>{serverError}</span>
            </div>
          )}

          <form onSubmit={formik.handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
                Correo electrónico
              </label>
              <input
                type="email"
                name="email"
                value={formik.values.email}
                onChange={formik.handleChange}
                onBlur={formik.handleBlur}
                placeholder="correo@ejemplo.com"
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-[#1a5c2a] focus:border-transparent outline-none transition text-sm"
              />
              {formik.touched.email && formik.errors.email && (
                <p className="mt-1.5 text-xs text-red-500">{formik.errors.email}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">
                Contraseña
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formik.values.password}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-[#1a5c2a] focus:border-transparent outline-none transition text-sm pr-12"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-xs font-medium"
                >
                  {showPassword ? "Ocultar" : "Ver"}
                </button>
              </div>
              {formik.touched.password && formik.errors.password && (
                <p className="mt-1.5 text-xs text-red-500">{formik.errors.password}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={formik.isSubmitting}
              className="w-full py-3 bg-[#1a5c2a] hover:bg-[#154a22] disabled:opacity-60 text-white font-bold rounded-xl transition-colors text-sm shadow-lg shadow-[#1a5c2a]/30 mt-2"
            >
              {formik.isSubmitting ? "Verificando..." : "Ingresar al sistema"}
            </button>
          </form>

          <p className="text-center text-xs text-gray-400 mt-8">
            Liga de Patinaje del Huila — Sistema administrativo interno
          </p>
        </div>
      </div>
    </div>
  );
}
