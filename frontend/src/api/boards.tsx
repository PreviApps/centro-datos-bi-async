import { BASE_URL } from "../environments/URL";

export async function getBoards() {
  const response = await fetch(`${BASE_URL}boards`);

  if (!response.ok) {
    throw new Error("Failed to fetch boards");
  }

  return response.json();
}

export async function getBoard(boardId: string) {
  const response = await fetch(`${BASE_URL}boards/${boardId}`);

  if (!response.ok) {
    throw new Error("Failed to fetch board details");
  }

  return response.json();
}

export async function getBoardsByUser(userId: string, positionName?: string) {
  const query = positionName ? `?position_name=${encodeURIComponent(positionName)}` : '';
  const response = await fetch(`${BASE_URL}boards/by_user/${userId}${query}`);

  if (!response.ok) {
    throw new Error("Failed to fetch boards for user");
  }

  return response.json();
}

export async function createBoard(payload: any) {
  const response = await fetch(`${BASE_URL}boards/save_board`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to create board");
  }

  return response.json();
}

export async function updateBoard(boardId: string, payload: any) {
  const response = await fetch(`${BASE_URL}boards/edit_board/${boardId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to edit board");
  }

  return response.json();
}

export async function deleteBoard(boardId: string) {
  const response = await fetch(`${BASE_URL}boards/delete_board/${boardId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to delete board");
  }

  return response.json();
}

export async function getBoardEmbed(boardId: string) {
  const response = await fetch(`${BASE_URL}boards/${boardId}/embed`);

  if (!response.ok) {
    throw new Error("Failed to fetch board embed info");
  }

  return response.json();
}

export async function getBoardUsersWithPermissions(boardId: string) {
  const response = await fetch(`${BASE_URL}boards/${boardId}/users_with_permissions`);

  if (!response.ok) {
    throw new Error("Failed to fetch board users with permissions");
  }

  return response.json();
}

export async function updateBoardPermissions(boardId: string, payload: any) {
  const response = await fetch(`${BASE_URL}boards/${boardId}/permissions`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Failed to update board permissions");
  }

  return response.json();
}

// Obtener la lista de workspaces de Power BI
export async function getPowerBIWorkspaces() {
  const response = await fetch(`${BASE_URL}boards/powerbi/workspaces`);

  if (!response.ok) {
    throw new Error("Failed to fetch Power BI workspaces");
  }

  return response.json();
}

// Obtener los reportes de un workspace específico
export async function getPowerBIReports(workspaceId: string) {
  const response = await fetch(`${BASE_URL}boards/powerbi/workspaces/${workspaceId}/reports`);

  if (!response.ok) {
    throw new Error("Failed to fetch Power BI reports for this workspace");
  }

  return response.json();
}