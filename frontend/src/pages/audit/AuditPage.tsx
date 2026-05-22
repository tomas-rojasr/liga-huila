import { useEffect, useState } from "react";

import api from "../../api/axios.config";

interface AuditLog {
  audit_id: string;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  description: string | null;
  actor_ip: string | null;
  created_at: string;
  actor_email: string | null;
}

const actionColors: Record<string, string> = {
  CREATE: "bg-green-100 text-green-700",
  UPDATE: "bg-blue-100 text-blue-700",
  DELETE: "bg-red-100 text-red-700",
  LOGIN: "bg-purple-100 text-purple-700",
  LOGOUT: "bg-gray-100 text-gray-600",
};

const ACTIONS = ["CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT"];
const ENTITY_TYPES = ["USER", "CLUB", "TEAM", "PLAYER"];

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  const [filterAction, setFilterAction] = useState("");
  const [filterEntity, setFilterEntity] = useState("");
  const [filterDateFrom, setFilterDateFrom] = useState("");
  const [filterDateTo, setFilterDateTo] = useState("");
  const [filterEmail, setFilterEmail] = useState("");

  const fetchLogs = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (filterAction) params.set("action", filterAction);
    if (filterEntity) params.set("entity_type", filterEntity);
    if (filterDateFrom) params.set("date_from", filterDateFrom);
    if (filterDateTo) params.set("date_to", filterDateTo);
    params.set("limit", "200");

    api.get(`/audit?${params.toString()}`)
      .then((res) => setLogs(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchLogs(); }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchLogs();
  };

  const handleClear = () => {
    setFilterAction("");
    setFilterEntity("");
    setFilterDateFrom("");
    setFilterDateTo("");
    setFilterEmail("");
    setLoading(true);
    api.get("/audit?limit=200")
      .then((res) => setLogs(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const displayed = filterEmail
    ? logs.filter((l) => l.actor_email?.toLowerCase().includes(filterEmail.toLowerCase()))
    : logs;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Auditoría</h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm">Historial de acciones del sistema</p>
      </div>

      {/* Filtros */}
      <form onSubmit={handleSearch} className="bg-white dark:bg-gray-800 rounded-xl shadow p-4">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Acción</label>
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="text-sm rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-liga-green"
            >
              <option value="">Todas</option>
              {ACTIONS.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Entidad</label>
            <select
              value={filterEntity}
              onChange={(e) => setFilterEntity(e.target.value)}
              className="text-sm rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-liga-green"
            >
              <option value="">Todas</option>
              {ENTITY_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Desde</label>
            <input
              type="date"
              value={filterDateFrom}
              onChange={(e) => setFilterDateFrom(e.target.value)}
              className="text-sm rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-liga-green"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Hasta</label>
            <input
              type="date"
              value={filterDateTo}
              onChange={(e) => setFilterDateTo(e.target.value)}
              className="text-sm rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-liga-green"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Usuario</label>
            <input
              type="text"
              placeholder="email..."
              value={filterEmail}
              onChange={(e) => setFilterEmail(e.target.value)}
              className="text-sm rounded-lg border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-liga-green"
            />
          </div>
        </div>

        <div className="flex gap-2 mt-3">
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium rounded-lg bg-liga-green text-white hover:bg-liga-green/90 transition-colors"
          >
            Buscar
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="px-4 py-2 text-sm font-medium rounded-lg border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Limpiar
          </button>
          {displayed.length > 0 && (
            <span className="ml-auto self-center text-xs text-gray-400">
              {displayed.length} registro{displayed.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
      </form>

      {/* Tabla */}
      {loading ? (
        <div className="flex justify-center py-16">
          <div className="animate-spin rounded-full h-10 w-10 border-4 border-liga-green border-t-transparent" />
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Fecha</th>
                <th className="px-4 py-3 text-left font-medium">Usuario</th>
                <th className="px-4 py-3 text-left font-medium">Acción</th>
                <th className="px-4 py-3 text-left font-medium">Entidad</th>
                <th className="px-4 py-3 text-left font-medium">Descripción</th>
                <th className="px-4 py-3 text-left font-medium">IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {displayed.length === 0 && (
                <tr>
                  <td colSpan={6} className="text-center py-10 text-gray-400">
                    Sin registros de auditoría
                  </td>
                </tr>
              )}
              {displayed.map((log) => (
                <tr key={log.audit_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="px-4 py-3 text-gray-500 dark:text-gray-400 text-xs whitespace-nowrap">
                    {new Date(log.created_at).toLocaleString("es-CO")}
                  </td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-300 text-xs">{log.actor_email ?? "-"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${actionColors[log.action] ?? "bg-gray-100 text-gray-600"}`}>
                      {log.action}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 dark:text-gray-400 text-xs">{log.entity_type ?? "-"}</td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-300 text-xs max-w-xs truncate">{log.description ?? "-"}</td>
                  <td className="px-4 py-3 font-mono text-gray-400 text-xs">{log.actor_ip ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
