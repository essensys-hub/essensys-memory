# Modération comptes utilisateurs (admin)

Soft-ban via `users.forbidden_at` ; endpoints admin `POST /api/admin/users/{id}/forbid|unforbid`, `DELETE /api/admin/users/{id}`.

Comptes interdits : login/OAuth refusé, redirect `/maintenance/` ; JWT existants invalidés par lookup DB (middleware).

Autorisation : helper `AuthorizeAdminTarget` — `admin_global` (sauf auto-delete/forbid), `admin_local` scope machine + rôles `user`/`guest_local` uniquement.

OpenSpec : `essensys-memory/openspec/changes/essensys-admin-user-forbid-delete-2026-06-027/`

Implémentation : `essensys-user-portal-backend` (prod), miroir `essensys-support-site` (UI + backend dev).
