from app.api.routes import reports
from app.core.database_client import SessionLocal
from app.repositories.minio_repository import MinioRepository
from app.repositories.reports_repository import ReportsRepository
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rq.job import Job
from app.core.queue import queue
from app.workers.jobs import sumar
from dotenv import load_dotenv
import uuid
import os

load_dotenv()

app = FastAPI()

#origins = ["http://localhost:5173"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(reports.router)

#@app.get("/")
#async def root():
 #   return "Hola FastAPI"#

"""@app.get("/")
async def enqueue():
    job = queue.enqueue(sumar, 2, 3)
    minio_repository = MinioRepository()
    list_buckets = await minio_repository.list_buckets()
    for bucket in list_buckets:
        print(bucket.name, bucket.creation_date)
    
    db = SessionLocal()

    repo = ReportsRepository(db)
    repo.create({
        "name": "Ventas",
        "description": "Reporte ventas",
        "parquet_path": "reports/ventas.parquet",
        "sql_template": "SELECT * FROM sales",
        "parameters": {
            "year": 2026
        },
        "created_by": uuid.uuid4()
    })
    result_db = repo.get_all()
    return {"job_id": job.id,
            "reports": result_db}"""


@app.get("/job/{job_id}")
def get_job(job_id: str):

    try:
        job = Job.fetch(job_id, connection=queue.connection)
    except:
        raise ValueError("Job no encontrado")

    return {
        "id": job.id,
        "status": job.get_status(),
        "result": job.result
    }


@app.post("/query")
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
        raise HTTPException(status_code=500, detail=str(e))