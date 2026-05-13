import { Edit2, Plus, Trash2, Users } from "lucide-react";
import { useEffect, useState } from "react";

import {
  type User,
  createUserService,
  deleteUserService,
  getUsersService,
  updateUserService,
} from "../../services/liga/users.service";
import { useAuthStore } from "../../store/auth.store";

const ROLES = ["superadmin", "admin", "consulta"];
const roleColors: Record<string, string> = {
  superadmin: "bg-purple-100 text-purple-700",
  admin: "bg-blue-100 text-blue-700",
  consulta: "bg-gray-100 text-gray-600",
};

const emptyForm = { email: "", username: "", password: "", first_name: "", last_name: "", role: "consulta" };

export default function UsersPage() {
  const { role: myRole } = useAuthStore();
  const isSuperadmin = myRole === "superadmin";

  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => getUsersService().then(setUsers).catch(console.error).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const openCreate = () => { setEditing(null); setForm(emptyForm); setError(null); setShowModal(true); };
  const openEdit = (u: User) => {
    setEditing(u);
    setForm({ email: u.email, username: u.username, password: "", first_name: u.first_name, last_name: u.last_name, role: u.role });
    setError(null);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      if (editing) {
        const payload: any = { email: form.email, username: form.username, first_name: form.first_name, last_name: form.last_name, role: form.role };
        await updateUserService(editing.user_id, payload);
      } else {
        await createUserService(form);
      }
      setShowModal(false);
      load();
    } catch (err: any) {
      const code = err?.response?.data?.detail?.code;
      const msgs: Record<string, string> = { EMAIL_ALREADY_EXISTS: "El email ya está en uso", USERNAME_ALREADY_EXISTS: "El usuario ya existe" };
      setError(msgs[code] ?? "Error al guardar");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("¿Eliminar este usuario?")) return;
    await deleteUserService(id).then(load).catch(console.error);
  };

  const toggleActive = async (u: User) => {
    await updateUserService(u.user_id, { is_active: !u.is_active }).then(load).catch(console.error);
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Usuarios</h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm">Gestión de usuarios y roles del sistema</p>
        </div>
        {isSuperadmin && (
          <button onClick={openCreate} className="flex items-center gap-2 px-4 py-2 bg-liga-green hover:bg-liga-green-dark text-white rounded-lg text-sm font-medium transition-colors">
            <Plus className="w-4 h-4" /> Nuevo usuario
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
                <th className="px-4 py-3 text-left font-medium">Usuario</th>
                <th className="px-4 py-3 text-left font-medium">Username</th>
                <th className="px-4 py-3 text-left font-medium">Rol</th>
                <th className="px-4 py-3 text-left font-medium">Estado</th>
                {isSuperadmin && <th className="px-4 py-3 text-right font-medium">Acciones</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
              {users.length === 0 && (
                <tr><td colSpan={5} className="text-center py-10 text-gray-400">Sin usuarios registrados</td></tr>
              )}
              {users.map((u) => (
                <tr key={u.user_id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-purple-50 flex items-center justify-center">
                        <Users className="w-4 h-4 text-purple-500" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">{u.first_name} {u.last_name}</p>
                        <p className="text-xs text-gray-400">{u.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 font-mono text-gray-600 dark:text-gray-300 text-xs">{u.username}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${roleColors[u.role] ?? "bg-gray-100 text-gray-600"}`}>{u.role}</span>
                  </td>
                  <td className="px-4 py-3">
                    <button onClick={() => isSuperadmin && toggleActive(u)} disabled={!isSuperadmin}
                      className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                      {u.is_active ? "Activo" : "Inactivo"}
                    </button>
                  </td>
                  {isSuperadmin && (
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => openEdit(u)} className="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg text-gray-500 transition-colors"><Edit2 className="w-4 h-4" /></button>
                        <button onClick={() => handleDelete(u.user_id)} className="p-1.5 hover:bg-red-50 rounded-lg text-red-500 transition-colors"><Trash2 className="w-4 h-4" /></button>
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
              <h2 className="font-semibold text-gray-900 dark:text-white">{editing ? "Editar usuario" : "Nuevo usuario"}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {error && <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>}
              <div className="grid grid-cols-2 gap-4">
                {[{ n: "first_name", l: "Nombre *", r: true }, { n: "last_name", l: "Apellido *", r: true }].map(({ n, l, r }) => (
                  <div key={n}>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{l}</label>
                    <input type="text" required={r} value={(form as any)[n]} onChange={(e) => setForm((f) => ({ ...f, [n]: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm" />
                  </div>
                ))}
              </div>
              {[{ n: "email", l: "Email *", t: "email", r: true }, { n: "username", l: "Username *", t: "text", r: true }].map(({ n, l, t, r }) => (
                <div key={n}>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{l}</label>
                  <input type={t} required={r} value={(form as any)[n]} onChange={(e) => setForm((f) => ({ ...f, [n]: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm" />
                </div>
              ))}
              {!editing && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Contraseña *</label>
                  <input type="password" required value={form.password} onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm" />
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Rol</label>
                <select value={form.role} onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-liga-green outline-none text-sm">
                  {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
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
