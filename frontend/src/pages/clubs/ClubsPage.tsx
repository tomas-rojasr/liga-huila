import { Building2, Edit2, Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

import {
  type Club,
  createClubService,
  deleteClubService,
  getClubsService,
  updateClubService,
} from "../../services/liga/clubs.service";
import { useAuthStore } from "../../store/auth.store";

const emptyForm = { name: "", code: "", address: "", phone: "", email: "", description: "" };

export default function ClubsPage() {
  const { role } = useAuthStore();
  const canEdit = role === "admin" || role === "superadmin";

  const [clubs, setClubs] = useState<Club[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<Club | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () =>
    getClubsService()
      .then(setClubs)
      .catch(console.error)
      .finally(() => setLoading(false));

  useEffect(() => { load(); }, []);

  const openCreate = () => { setEditing(null); setForm(emptyForm); setError(null); setShowModal(true); };
  const openEdit = (club: Club) => {
    setEditing(club);
    setForm({ name: club.name, code: club.code, address: club.address ?? "", phone: club.phone ?? "", email: club.email ?? "", description: club.description ?? "" });
    setError(null);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      if (editing) {
        await updateClubService(editing.club_id, form);
      } else {
        await createClubService(form);
      }
      setShowModal(false);
      load();
    } catch (err: any) {
      const code = err?.response?.data?.detail?.code;
      setError(code === "CLUB_CODE_ALREADY_EXISTS" ? "El código de club ya existe" : "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("¿Eliminar este club?")) return;
    await deleteClubService(id).then(load).catch(console.error);
  };

  const toggleActive = async (club: Club) => {
    await updateClubService(club.club_id, { is_active: !club.is_active }).then(load).catch(console.error);
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Clubes</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Gestión de clubes deportivos</p>
        </div>
        {canEdit && (
          <button onClick={openCreate} className="flex items-center gap-2 px-4 py-2 bg-liga-green hover:bg-liga-green-dark text-white rounded-lg text-sm font-medium transition-colors">
            <Plus className="w-4 h-4" /> Nuevo club
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
                <th className="px-4 py-3 text-left font-medium">Club</th>
                <th className="px-4 py-3 text-left font-medium">Código</th>
                <th className="px-4 py-3 text-left font-medium">Contacto</th>
                <th className="px-4 py-3 text-left font-medium">Estado</th>
                {canEdit && <th className="px-4 py-3 text-right font-medium">Acciones</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {clubs.length === 0 && (
                <tr><td colSpan={5} className="text-center py-10 text-gray-400">Sin clubes registrados</td></tr>
              )}
              {clubs.map((club) => (
                <tr key={club.club_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-liga-green/10 flex items-center justify-center">
                        <Building2 className="w-4 h-4 text-liga-green" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{club.name}</p>
                        {club.description && <p className="text-xs text-gray-400 truncate max-w-xs">{club.description}</p>}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-300 font-mono">{club.code}</td>
                  <td className="px-4 py-3 text-gray-500 dark:text-gray-400">
                    {club.phone && <p>{club.phone}</p>}
                    {club.email && <p className="text-xs">{club.email}</p>}
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => canEdit && toggleActive(club)} disabled={!canEdit}
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${club.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                      {club.is_active ? "Activo" : "Inactivo"}
                    </button>
                  </td>
                  {canEdit && (
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => openEdit(club)} className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg text-gray-500 dark:text-gray-400 transition-colors">
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button onClick={() => handleDelete(club.club_id)} className="p-1.5 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-lg text-red-500 transition-colors">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {showModal && createPortal(
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md">
            <div className="px-6 py-4 border-b dark:border-gray-700">
              <h2 className="font-semibold text-gray-900 dark:text-white">{editing ? "Editar club" : "Nuevo club"}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>}
              {[
                { name: "name", label: "Nombre *", type: "text", required: true },
                { name: "code", label: "Código *", type: "text", required: true, disabled: !!editing },
                { name: "address", label: "Dirección", type: "text" },
                { name: "phone", label: "Teléfono", type: "text" },
                { name: "email", label: "Email", type: "email" },
              ].map(({ name, label, type, required, disabled }) => (
                <div key={name}>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{label}</label>
                  <input
                    type={type} required={required} disabled={disabled}
                    value={(form as any)[name]}
                    onChange={(e) => setForm((f) => ({ ...f, [name]: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50 focus:ring-2 focus:ring-liga-green outline-none text-sm"
                  />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Descripción</label>
                <textarea rows={2} value={form.description}
                  onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm resize-none" />
              </div>
              <div className="flex gap-3 justify-end pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">Cancelar</button>
                <button type="submit" disabled={saving} className="px-4 py-2 text-sm bg-liga-green hover:bg-liga-green-dark disabled:opacity-60 text-white rounded-lg font-medium transition-colors">
                  {saving ? "Guardando..." : "Guardar"}
                </button>
              </div>
            </form>
          </div>
        </div>
      , document.body)}
    </div>
  );
}
