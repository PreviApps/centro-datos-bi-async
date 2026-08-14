import { BASE_URL } from "../environments/URL";
import { MinioItem } from "../utils/interfaces/minio/minio.interface";

export interface ListTablesResponse {
  items: MinioItem[];
}

export async function listTables(
  path: string = ""
): Promise<ListTablesResponse> {
  const res = await fetch(`${BASE_URL}reports/list_tables`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ path }),
  });

  if (!res.ok) {
    throw new Error("Error fetching tables");
  }

  const data: ListTablesResponse = await res.json();

  return data;
}