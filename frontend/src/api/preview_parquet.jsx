import { BASE_URL } from "../environments/URL";

export async function previewParquet(path) {

  const res = await fetch(
    `${BASE_URL}reports/preview`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ path })
    }
  );

  return await res.json();
}