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

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/audit")
      .then((res) => setLogs(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Auditoría</h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm">Historial de acciones del sistema</p>
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-10 w-10 border-4 border-liga-green border-t-transparent" /></div>
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
              {logs.length === 0 && (
                <tr><td colSpan={6} className="text-center py-10 text-gray-400">Sin registros de auditoría</td></tr>
              )}
              {logs.map((log) => (
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
