import { BarChart3, Building2, Shield, Users, Volleyball } from "lucide-react";
import { useEffect, useState } from "react";

import { type DashboardStats, getDashboardService } from "../../services/liga/dashboard.service";

interface StatCardProps {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
}

function StatCard({ label, value, icon, color }: StatCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${color}`}>{icon}</div>
      <div>
        <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardService()
      .then(setStats)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-4 border-liga-green border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm">Resumen general del sistema</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Clubes"
          value={stats?.total_clubs ?? 0}
          icon={<Building2 className="w-6 h-6 text-white" />}
          color="bg-liga-green"
        />
        <StatCard
          label="Total Equipos"
          value={stats?.total_teams ?? 0}
          icon={<Shield className="w-6 h-6 text-white" />}
          color="bg-blue-500"
        />
        <StatCard
          label="Total Jugadores"
          value={stats?.total_players ?? 0}
          icon={<Volleyball className="w-6 h-6 text-white" />}
          color="bg-liga-gold"
        />
        <StatCard
          label="Usuarios"
          value={stats?.total_users ?? 0}
          icon={<Users className="w-6 h-6 text-white" />}
          color="bg-purple-500"
        />
      </div>

      {/* Players by category */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
        <div className="flex items-center gap-2 mb-4">
          <BarChart3 className="w-5 h-5 text-liga-green" />
          <h2 className="font-semibold text-gray-900 dark:text-white">Jugadores por categoría</h2>
        </div>

        {stats?.players_by_category && stats.players_by_category.length > 0 ? (
          <div className="space-y-3">
            {stats.players_by_category
              .sort((a, b) => b.count - a.count)
              .map(({ category, count }) => {
                const max = Math.max(...stats.players_by_category.map((c) => c.count));
                const pct = max > 0 ? (count / max) * 100 : 0;
                return (
                  <div key={category} className="flex items-center gap-4">
                    <span className="w-20 text-sm font-medium text-gray-600 dark:text-gray-400 text-right">
                      {category}
                    </span>
                    <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-full h-3">
                      <div
                        className="bg-liga-green h-3 rounded-full transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="w-8 text-sm font-bold text-gray-900 dark:text-white">{count}</span>
                  </div>
                );
              })}
          </div>
        ) : (
          <p className="text-gray-400 text-sm text-center py-6">Sin datos de jugadores aún</p>
        )}
      </div>
    </div>
  );
}
