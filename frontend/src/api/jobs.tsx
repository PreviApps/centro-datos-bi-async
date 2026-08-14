import { BASE_URL } from "../environments/URL";

export async function runJob(
  reportId: string,
  parameters: Record<string, unknown>
) {

  const response = await fetch(
    `${BASE_URL}reports/${reportId}/run`,
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

export async function getJob(jobId: string) {
    const response = await fetch(`${BASE_URL}reports/jobs/${jobId}`);

    if (!response.ok) {
        throw new Error("Error fetching job");
    }

    return response.json();
}