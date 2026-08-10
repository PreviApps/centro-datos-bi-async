import { BASE_URL } from "../environments/URL";

export async function getReportUsersWithPermissions(reportId: string) {
  const response = await fetch(`${BASE_URL}/${reportId}/users_with_permissions`);
  if (!response.ok) {
    throw new Error("Failed to fetch users with permissions");
  }
  return response.json(); // Retorna la lista del SSO con la propiedad 'has_permission'
}

export async function getReportPermissions(reportId: string) {
  const response = await fetch(`${BASE_URL}/${reportId}/permissions`);
  if (!response.ok) {
    throw new Error("Failed to fetch permissions");
  }
  return response.json(); // Retorna { user_ids: [], position_names: [] }
}

export async function updateReportPermissions(
  reportId: string, 
  payload: { user_ids: string[]; position_names: string[]; admin_user_id: string }
) {
  const response = await fetch(`${BASE_URL}/${reportId}/permissions`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("Failed to update permissions");
  }

  return response.json();
}