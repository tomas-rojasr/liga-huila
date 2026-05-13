import { Edit2, Plus, Trash2, Volleyball } from "lucide-react";
import { useEffect, useState } from "react";

import { type Team, getTeamsService } from "../../services/liga/teams.service";
import {
  type Player,
  createPlayerService,
  deletePlayerService,
  getPlayersService,
  updatePlayerService,
} from "../../services/liga/players.service";
import { useAuthStore } from "../../store/auth.store";

const STATUSES = ["ACTIVO", "INACTIVO", "SUSPENDIDO", "TRANSFERIDO"];
const DOC_TYPES = ["CC", "TI", "CE", "PASAPORTE"];
const POSITIONS = ["Portero", "Defensa", "Mediocampista", "Delantero"];

const emptyForm = {
  team_id: "", first_name: "", last_name: "", birth_date: "",
  document_type: "CC", document_number: "", nationality: "Colombiana",
  position: "", photo_url: "", status: "ACTIVO",
};

const statusColors: Record<string, string> = {
  ACTIVO: "bg-green-100 text-green-700",
  INACTIVO: "bg-gray-100 text-gray-600",
  SUSPENDIDO: "bg-red-100 text-red-700",
  TRANSFERIDO: "bg-blue-100 text-blue-700",
};

export default function PlayersPage() {
  const { role } = useAuthStore();
  const canEdit = role === "admin" || role === "superadmin";

  const [players, setPlayers] = useState<Player[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Player | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () =>
    Promise.all([getPlayersService(), getTeamsService()])
      .then(([p, t]) => { setPlayers(p); setTeams(t); })
      .catch(console.error)
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const openCreate = () => { setEditing(null); setForm(emptyForm); setError(null); setShowModal(true); };
  const openEdit = (p: Player) => {
    setEditing(p);
    setForm({
      team_id: p.team_id ?? "", first_name: p.first_name, last_name: p.last_name,
      birth_date: p.birth_date, document_type: p.document_type, document_number: p.document_number,
      nationality: p.nationality, position: p.position ?? "", photo_url: p.photo_url ?? "", status: p.status,
    });
    setError(null);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    const payload = { ...form, team_id: form.team_id || undefined, position: form.position || undefined, photo_url: form.photo_url || undefined };
    try {
      if (editing) await updatePlayerService(editing.player_id, payload);
      else await createPlayerService(payload);
      setShowModal(false);
      load();
    } catch (err: any) {
      const code = err?.response?.data?.detail?.code;
      setError(code === "DOCUMENT_NUMBER_ALREADY_EXISTS" ? "El número de documento ya está registrado" : "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("¿Eliminar este jugador?")) return;
    await deletePlayerService(id).then(load).catch(console.error);
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Jugadores</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Registro y gestión de jugadores</p>
        </div>
        {canEdit && (
          <button onClick={openCreate} className="flex items-center gap-2 px-4 py-2 bg-liga-green hover:bg-liga-green-dark text-white rounded-lg text-sm font-medium transition-colors">
            <Plus className="w-4 h-4" /> Nuevo jugador
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
                <th className="px-4 py-3 text-left font-medium">Jugador</th>
                <th className="px-4 py-3 text-left font-medium">Documento</th>
                <th className="px-4 py-3 text-left font-medium">Categoría</th>
                <th className="px-4 py-3 text-left font-medium">Equipo</th>
                <th className="px-4 py-3 text-left font-medium">Estado</th>
                {canEdit && <th className="px-4 py-3 text-right font-medium">Acciones</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {players.length === 0 && (
                <tr><td colSpan={6} className="text-center py-10 text-gray-400">Sin jugadores registrados</td></tr>
              )}
              {players.map((player) => (
                <tr key={player.player_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-liga-gold/10 flex items-center justify-center">
                        <Volleyball className="w-4 h-4 text-liga-gold" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{player.first_name} {player.last_name}</p>
                        {player.position && <p className="text-xs text-gray-400">{player.position}</p>}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-500 dark:text-gray-400">
                    <p className="font-mono text-xs">{player.document_type}</p>
                    <p>{player.document_number}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 bg-liga-green/10 text-liga-green rounded-full text-xs font-medium">{player.category}</span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 dark:text-gray-400">{player.team_name ?? "-"}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[player.status] ?? "bg-gray-100 text-gray-600"}`}>
                      {player.status}
                    </span>
                  </td>
                  {canEdit && (
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => openEdit(player)} className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg text-gray-500 transition-colors"><Edit2 className="w-4 h-4" /></button>
                        <button onClick={() => handleDelete(player.player_id)} className="p-1.5 hover:bg-red-50 rounded-lg text-red-500 transition-colors"><Trash2 className="w-4 h-4" /></button>
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
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="px-6 py-4 border-b dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-800">
              <h2 className="font-semibold text-gray-900 dark:text-white">{editing ? "Editar jugador" : "Nuevo jugador"}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>}

              <div className="grid grid-cols-2 gap-4">
                {[{ name: "first_name", label: "Nombre *", required: true }, { name: "last_name", label: "Apellido *", required: true }].map(({ name, label, required }) => (
                  <div key={name}>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{label}</label>
                    <input type="text" required={required} value={(form as any)[name]}
                      onChange={(e) => setForm((f) => ({ ...f, [name]: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm" />
                  </div>
                ))}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Fecha de nacimiento *</label>
                <input type="date" required value={form.birth_date} onChange={(e) => setForm((f) => ({ ...f, birth_date: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Tipo documento</label>
                  <select value={form.document_type} onChange={(e) => setForm((f) => ({ ...f, document_type: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm">
                    {DOC_TYPES.map((d) => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Número documento *</label>
                  <input type="text" required value={form.document_number} onChange={(e) => setForm((f) => ({ ...f, document_number: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Posición</label>
                  <select value={form.position} onChange={(e) => setForm((f) => ({ ...f, position: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm">
                    <option value="">Sin asignar</option>
                    {POSITIONS.map((p) => <option key={p} value={p}>{p}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Estado</label>
                  <select value={form.status} onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm">
                    {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Equipo</label>
                <select value={form.team_id} onChange={(e) => setForm((f) => ({ ...f, team_id: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm">
                  <option value="">Sin equipo asignado</option>
                  {teams.filter((t) => t.is_active).map((t) => <option key={t.team_id} value={t.team_id}>{t.name} ({t.category})</option>)}
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
