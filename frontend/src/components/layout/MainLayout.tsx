import {
  BarChart3,
  Building2,
  ClipboardList,
  LogOut,
  Menu,
  Moon,
  PersonStanding,
  Shield,
  Sun,
  Users,
} from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useTheme } from "../../context/ThemeContext";
import { logoutService } from "../../services/liga/auth.service";
import { useAuthStore } from "../../store/auth.store";

const navItems = [
  { to: "/dashboard", icon: BarChart3, label: "Dashboard" },
  { to: "/clubs", icon: Building2, label: "Clubes" },
  { to: "/teams", icon: Shield, label: "Equipos" },
  { to: "/players", icon: PersonStanding, label: "Patinadores" },
  { to: "/users", icon: Users, label: "Usuarios", adminOnly: true },
  { to: "/audit", icon: ClipboardList, label: "Auditoría", adminOnly: true },
];

export default function MainLayout() {
  const { theme, toggleTheme } = useTheme();
  const { fullName, role, logout } = useAuthStore();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = async () => {
    try {
      await logoutService();
    } catch {
      // token already invalid
    } finally {
      logout();
      navigate("/login");
    }
  };

  const visibleItems = navItems.filter(
    (item) => !item.adminOnly || role === "admin" || role === "superadmin"
  );

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-16"
        } transition-all duration-300 bg-liga-green dark:bg-liga-green-dark flex flex-col shadow-xl`}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-liga-green-light/30">
          <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center shrink-0 overflow-hidden">
            <img src="/logo-liga.png" alt="LPH" className="w-full h-full object-contain p-0.5"
              onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
          </div>
          {sidebarOpen && (
            <div className="overflow-hidden">
              <p className="text-white font-bold text-sm leading-tight">Liga Patinaje</p>
              <p className="text-green-200 text-xs">del Huila</p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          {visibleItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm font-medium ${
                  isActive
                    ? "bg-white/20 text-white"
                    : "text-green-100 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              <Icon className="w-5 h-5 shrink-0" />
              {sidebarOpen && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User info */}
        <div className="border-t border-liga-green-light/30 p-3">
          {sidebarOpen && (
            <div className="mb-2 px-2">
              <p className="text-white text-sm font-medium truncate">{fullName}</p>
              <p className="text-green-200 text-xs capitalize">{role}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-3 py-2 rounded-lg text-green-100 hover:bg-white/10 hover:text-white transition-colors text-sm"
          >
            <LogOut className="w-4 h-4 shrink-0" />
            {sidebarOpen && <span>Cerrar sesión</span>}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen((o) => !o)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300"
            >
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
