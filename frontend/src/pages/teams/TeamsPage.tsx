import { Edit2, Plus, Shield, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import { type Club, getClubsService } from "../../services/liga/clubs.service";
import {
  type Team,
  createTeamService,
  deleteTeamService,
  getTeamsService,
  updateTeamService,
} from "../../services/liga/teams.service";
import { useAuthStore } from "../../store/auth.store";

const CATEGORIES = ["SUB-8", "SUB-10", "SUB-12", "SUB-14", "SUB-16", "SUB-18", "SUB-20", "PRIMERA"];
const emptyForm = { club_id: "", name: "", category: "PRIMERA", is_active: true };

export default function TeamsPage() {
  const { role } = useAuthStore();
  const canEdit = role === "admin" || role === "superadmin";

  const [teams, setTeams] = useState<Team[]>([]);
  const [clubs, setClubs] = useState<Club[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Team | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () =>
    Promise.all([getTeamsService(), getClubsService()])
      .then(([t, c]) => { setTeams(t); setClubs(c); })
      .catch(console.error)
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const openCreate = () => { setEditing(null); setForm(emptyForm); setError(null); setShowModal(true); };
  const openEdit = (team: Team) => {
    setEditing(team);
    setForm({ club_id: team.club_id ?? "", name: team.name, category: team.category, is_active: team.is_active });
    setError(null);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    const payload = { ...form, club_id: form.club_id || undefined };
    try {
      if (editing) await updateTeamService(editing.team_id, payload);
      else await createTeamService(payload);
      setShowModal(false);
      load();
    } catch {
      setError("Error al guardar el equipo");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("¿Eliminar este equipo?")) return;
    await deleteTeamService(id).then(load).catch(console.error);
  };

  const categoryColor: Record<string, string> = {
    "SUB-8": "bg-pink-100 text-pink-700", "SUB-10": "bg-purple-100 text-purple-700",
    "SUB-12": "bg-blue-100 text-blue-700", "SUB-14": "bg-cyan-100 text-cyan-700",
    "SUB-16": "bg-teal-100 text-teal-700", "SUB-18": "bg-lime-100 text-lime-700",
    "SUB-20": "bg-orange-100 text-orange-700", "PRIMERA": "bg-liga-green/10 text-liga-green",
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Equipos</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Gestión de equipos por club y categoría</p>
        </div>
        {canEdit && (
          <button onClick={openCreate} className="flex items-center gap-2 px-4 py-2 bg-liga-green hover:bg-liga-green-dark text-white rounded-lg text-sm font-medium transition-colors">
            <Plus className="w-4 h-4" /> Nuevo equipo
          </button>
        )}
      </div>

      {loading ? (
        <div className="flex justify-center py-16"><div className="animate-spin rounded-full h-10 w-10 border-4 border-liga-green border-t-transparent" /></div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
              <tr>
                <th className="px-4 py-3 text-left font-medium">Equipo</th>
                <th className="px-4 py-3 text-left font-medium">Club</th>
                <th className="px-4 py-3 text-left font-medium">Categoría</th>
                <th className="px-4 py-3 text-left font-medium">Estado</th>
                {canEdit && <th className="px-4 py-3 text-right font-medium">Acciones</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {teams.length === 0 && (
                <tr><td colSpan={5} className="text-center py-10 text-gray-400">Sin equipos registrados</td></tr>
              )}
              {teams.map((team) => (
                <tr key={team.team_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                        <Shield className="w-4 h-4 text-blue-500" />
                      </div>
                      <p className="font-medium text-gray-900 dark:text-white">{team.name}</p>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-500 dark:text-gray-400">{team.club_name ?? "-"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${categoryColor[team.category] ?? "bg-gray-100 text-gray-600"}`}>
                      {team.category}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${team.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                      {team.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  {canEdit && (
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => openEdit(team)} className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg text-gray-500 transition-colors"><Edit2 className="w-4 h-4" /></button>
                        <button onClick={() => handleDelete(team.team_id)} className="p-1.5 hover:bg-red-50 rounded-lg text-red-500 transition-colors"><Trash2 className="w-4 h-4" /></button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md">
            <div className="px-6 py-4 border-b dark:border-gray-700">
              <h2 className="font-semibold text-gray-900 dark:text-white">{editing ? "Editar equipo" : "Nuevo equipo"}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Nombre *</label>
                <input type="text" required value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Club</label>
                <select value={form.club_id} onChange={(e) => setForm((f) => ({ ...f, club_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm">
                  <option value="">Sin club asignado</option>
                  {clubs.filter((c) => c.is_active).map((c) => <option key={c.club_id} value={c.club_id}>{c.name}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Categoría *</label>
                <select value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm">
                  {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div className="flex gap-3 justify-end pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">Cancelar</button>
                <button type="submit" disabled={saving} className="px-4 py-2 text-sm bg-liga-green hover:bg-liga-green-dark disabled:opacity-60 text-white rounded-lg font-medium transition-colors">
                  {saving ? "Guardando..." : "Guardar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
