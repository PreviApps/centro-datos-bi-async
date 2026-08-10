from app.api.routes import reports, permissions
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuración de orígenes permitidos (replicando la seguridad de los proyectos en NestJS)
origins = [
    "https://centro-datos-bi-v2.previsalud.com.co",
    "http://10.10.119.97:4008",
    "http://10.10.119.45:4008",
    "https://previsalud.com.co",
    "http://localhost:4008",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Expresión regular para permitir cualquier subdominio de previsalud y cualquier puerto de localhost
    allow_origin_regex=r"https://.*\.previsalud\.com\.co|http://(localhost|10\.10\.119\.45)(:\d+)?",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "x-api-key"]
)

app.include_router(reports.router)
app.include_router(permissions.router)

'''@app.post("/query")
async def execute_query(query_body: dict):
    
    from app.core.minio_client import client, BUCKET
    import duckdb
    import polars as pl
    import tempfile
    import re
    from app.core.duckdb_client import con

    """
    Recibe: {"query": "SELECT * FROM DGH_EXAMPLE"}
    Reemplaza 'DGH_EXAMPLE' por 'read_parquet("s3://exports/DGH EXAMPLE/file.parquet")'
    y limita a 10 filas.
    """
    query = query_body.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="No query provided")

    # Validar query
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "COPY", "INSTALL", "LOAD"]
    for word in forbidden:
        if word in query.upper():
            raise HTTPException(status_code=400, detail=f"Operación no permitida: {word}")

    # Buscar parquet correspondiente en MinIO
    objects = client.list_objects(BUCKET, recursive=True)
    parquet_path = None
    for obj in objects:
        if obj.object_name.startswith("DGH EXAMPLE/") and obj.object_name.endswith(".parquet"):
            parquet_path = obj.object_name
            break

    if not parquet_path:
        raise HTTPException(status_code=404, detail="No se encontró parquet en DGH EXAMPLE")

    # Reemplazar tabla por read_parquet
    table_pattern = re.compile(r"\bDGH_EXAMPLE\b", re.IGNORECASE)
    query = table_pattern.sub(f'read_parquet("s3://{BUCKET}/{parquet_path}")', query)

    # Agregar LIMIT 10 si no existe
    if "LIMIT" not in query.upper():
        query = query.strip().rstrip(";") + " LIMIT 10"

    try:
        result = con.execute(query).fetchdf()
        return {
            "query_executed": query,
            "result": result.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''