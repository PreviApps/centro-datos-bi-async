import { BASE_URL } from "../environments/URL"


export async function executeQuery(query) {
  const res = await fetch(`${BASE_URL}reports/execute_query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ query })
  })

  const data = await res.json()

  if (!res.ok) {
    throw new Error(
      data.detail || "Error ejecutando query"
    )
  }

  return data
}

export async function saveQuery(query){
  const res = await fetch(`${BASE_URL}reports/save_query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(query)
  })
  const data = await res.json()

  if (!res.ok) {
    const message = Array.isArray(data.detail)
      ? data.detail
          .map(d => `• ${d.loc[d.loc.length - 1]}: ${d.msg}`)
          .join("\n")
      : typeof data.detail === "string"
        ? data.detail  // ← el 400 ya viene como string legible
        : JSON.stringify(data.detail);

    throw new Error(message);
  }
  console.log("RESPUESTA DE SAVE_QUERY", data)
  return data
}