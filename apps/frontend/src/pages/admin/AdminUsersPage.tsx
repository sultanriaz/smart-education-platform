import { useMemo, useState, type FormEvent } from "react";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import * as api from "../../features/admin/admin-api";
import {
  adminKeys,
  useAdminMutation,
  useAdminPermissions,
  useAdminRoles,
  useAdminUsers
} from "../../features/admin/hooks";

export function AdminUsersPage() {
  const users = useAdminUsers();
  const roles = useAdminRoles();
  const permissions = useAdminPermissions();
  const toast = useToast();

  const createUser = useAdminMutation(api.createUser, adminKeys.users);
  const updateUser = useAdminMutation(
    ({ userId, input }: { userId: string; input: Parameters<typeof api.updateUser>[1] }) =>
      api.updateUser(userId, input),
    adminKeys.users
  );
  const deactivate = useAdminMutation(api.deactivateUser, adminKeys.users);
  const createRole = useAdminMutation(api.createRole, adminKeys.roles);

  const [query, setQuery] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [userRole, setUserRole] = useState("student");

  const [roleName, setRoleName] = useState("");
  const [roleDescription, setRoleDescription] = useState("");
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  const filteredUsers = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return users.data ?? [];
    return (users.data ?? []).filter((item) =>
      [item.email, item.fullName, item.roles.join(" ")]
        .join(" ")
        .toLowerCase()
        .includes(needle)
    );
  }, [query, users.data]);

  if (users.isLoading || roles.isLoading || permissions.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading user administration…" />
      </div>
    );
  }

  if (users.error || roles.error || permissions.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Admin" title="Users & RBAC" />
        <InlineError message="Identity administration data could not be loaded." />
      </div>
    );
  }

  const submitUser = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await createUser.mutateAsync({
        email,
        full_name: fullName,
        password,
        role: userRole
      });
      setEmail("");
      setFullName("");
      setPassword("");
      toast.push("User account created.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Could not create user.", "error");
    }
  };

  const submitRole = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await createRole.mutateAsync({
        name: roleName.trim(),
        description: roleDescription.trim() || undefined,
        permissions: selectedPermissions
      });
      setRoleName("");
      setRoleDescription("");
      setSelectedPermissions([]);
      toast.push("Role created.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Could not create role.", "error");
    }
  };

  const toggleActive = async (userId: string, value: boolean) => {
    try {
      await updateUser.mutateAsync({
        userId,
        input: { is_active: value }
      });
      toast.push(value ? "User activated." : "User deactivated.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Update failed.", "error");
    }
  };

  const setRoles = async (userId: string, roleNameValue: string) => {
    try {
      await updateUser.mutateAsync({
        userId,
        input: { roles: [roleNameValue] }
      });
      toast.push("User role updated.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Role update failed.", "error");
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Admin"
        title="Users & RBAC"
        description="Provision accounts, manage activation and verification state, assign roles, and create permission-backed roles."
      />

      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <Card title="Create user">
          <form className="space-y-4" onSubmit={(event) => void submitUser(event)}>
            <Input label="Full name" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <Input label="Temporary password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            <label className="block text-sm font-medium">
              Initial role
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={userRole}
                onChange={(e) => setUserRole(e.target.value)}
              >
                {(roles.data ?? []).map((item) => (
                  <option key={item.id} value={item.name}>{item.name}</option>
                ))}
              </select>
            </label>
            <Button type="submit" disabled={createUser.isPending}>
              {createUser.isPending ? "Creating…" : "Create user"}
            </Button>
          </form>
        </Card>

        <Card title="Create role">
          <form className="space-y-4" onSubmit={(event) => void submitRole(event)}>
            <Input label="Role name" value={roleName} onChange={(e) => setRoleName(e.target.value)} />
            <Input label="Description" value={roleDescription} onChange={(e) => setRoleDescription(e.target.value)} />
            <fieldset>
              <legend className="text-sm font-medium">Permissions</legend>
              <div className="mt-2 max-h-56 space-y-2 overflow-auto rounded-xl border border-line p-3">
                {(permissions.data ?? []).map((item) => (
                  <label key={item.id} className="flex items-start gap-3 text-sm">
                    <input
                      type="checkbox"
                      checked={selectedPermissions.includes(item.code)}
                      onChange={(event) =>
                        setSelectedPermissions((current) =>
                          event.target.checked
                            ? [...current, item.code]
                            : current.filter((code) => code !== item.code)
                        )
                      }
                    />
                    <span>
                      <span className="font-medium">{item.code}</span>
                      {item.description ? (
                        <span className="mt-1 block text-xs text-muted">{item.description}</span>
                      ) : null}
                    </span>
                  </label>
                ))}
              </div>
            </fieldset>
            <Button type="submit" disabled={createRole.isPending}>
              {createRole.isPending ? "Creating…" : "Create role"}
            </Button>
          </form>
        </Card>
      </div>

      <Card className="mt-6" title="User directory">
        <div className="mb-4">
          <Input
            label="Search"
            placeholder="Name, email, or role"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] text-left text-sm">
            <thead>
              <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                <th className="px-2 py-3">User</th>
                <th className="px-2 py-3">Roles</th>
                <th className="px-2 py-3">Verified</th>
                <th className="px-2 py-3">Active</th>
                <th className="px-2 py-3">Role change</th>
                <th className="px-2 py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((item) => (
                <tr key={item.id} className="border-b border-line/70">
                  <td className="px-2 py-3">
                    <p className="font-semibold">{item.fullName}</p>
                    <p className="mt-1 text-xs text-muted">{item.email}</p>
                  </td>
                  <td className="px-2 py-3">
                    <div className="flex flex-wrap gap-1">
                      {item.roles.map((name) => <Badge key={name}>{name}</Badge>)}
                    </div>
                  </td>
                  <td className="px-2 py-3">{item.isVerified ? "Yes" : "No"}</td>
                  <td className="px-2 py-3">{item.isActive ? "Active" : "Inactive"}</td>
                  <td className="px-2 py-3">
                    <select
                      aria-label={`Role for ${item.fullName}`}
                      className="rounded-lg border border-line bg-panel px-2 py-2"
                      defaultValue={item.roles[0] ?? ""}
                      onChange={(event) => void setRoles(item.id, event.target.value)}
                    >
                      {(roles.data ?? []).map((roleItem) => (
                        <option key={roleItem.id} value={roleItem.name}>
                          {roleItem.name}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td className="px-2 py-3">
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        onClick={() => void toggleActive(item.id, !item.isActive)}
                      >
                        {item.isActive ? "Deactivate" : "Activate"}
                      </Button>
                      {item.isActive ? (
                        <Button
                          variant="ghost"
                          onClick={async () => {
                            try {
                              await deactivate.mutateAsync(item.id);
                              toast.push("User deactivated.", "success");
                            } catch (error) {
                              toast.push(
                                error instanceof Error ? error.message : "Deactivate failed.",
                                "error"
                              );
                            }
                          }}
                        >
                          Disable
                        </Button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
