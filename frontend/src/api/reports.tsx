import { BASE_URL } from "../environments/URL";

export async function getReports() {
  const response = await fetch(`${BASE_URL}`);

  if (!response.ok) {
    throw new Error("Failed to fetch reports");
  }

  return response.json();
}

export async function getReportsByUser(userId: string, positionName?: string) {
  const query = positionName ? `?position_name=${encodeURIComponent(positionName)}` : '';
  const response = await fetch(`${BASE_URL}/by_user/${userId}${query}`);
  if (!response.ok) {
    throw new Error("Failed to fetch user reports");
  }
  return response.json();
}

export async function getReport(reportId: string) {
  const response = await fetch(`${BASE_URL}/${reportId}`);

  if (!response.ok) {
    throw new Error("Failed to fetch report");
  }

  return response.json();
}

export async function updateReport(reportId: string, payload: any){
  const response = await fetch(`${BASE_URL}/edit_report/${reportId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    }
  );

  if (!response.ok) {
    throw new Error("Failed to edit report");
  }

  return response.json();
}

export async function deleteReport(reportId: string){
  const response = await fetch(`${BASE_URL}/delete_report/${reportId}`,
    {
      method: "DELETE"
    }
  );

  if (!response.ok) {
    throw new Error("Failed to delete report");
  }

  return response.json();
}

export async function runReport(
  reportId: string,
  parameters: Record<string, unknown>
) {

  const response = await fetch(
    `${BASE_URL}/${reportId}/run`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        parameters
      })
    }
  );

  if (!response.ok) {
    throw new Error("Failed to run report");
  }

  return response.json();
}