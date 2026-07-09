from app.api.schemas.path import PathRequest
from app.api.schemas.query import QueryRequest
from app.api.schemas.report import ExecuteReportRequest, ReportCreate
from app.core.database_client import SessionLocal
from app.providers.reports_providers import get_reports_service
from app.repositories.minio_repository import MinioRepository
from app.repositories.reports_jobs_repository import ReportJobsRepository
from app.services.duckdb_service import DuckDBService
from app.services.jobs_service import JobsService
from app.services.reports_service import ReportsService
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(
    prefix = "/reports"
)

#Listar reportes
@router.get("/")
async def get_reports(service: ReportsService = Depends(get_reports_service)):
    return service.get_reports()

@router.get("/{report_id}")
async def report_detail(report_id: str, service: ReportsService = Depends(get_reports_service)):
    return service.get_report(report_id)

@router.post("/list_tables")
async def list_tables(body: PathRequest):
    minio_repository = MinioRepository()
    response = await minio_repository.list_objects(body.path)
    return {
        "items": response,
    }

"""@router.post("/preview")
async def preview(body: PathRequest):
    return DuckDBService.preview_parquet(body.path)"""

@router.post("/preview")
async def preview(body: PathRequest, service: ReportsService = Depends(get_reports_service)):
    return service.preview_parquet_queue(body.path)

"""@router.post("/execute_query")
async def execute_query(body: QueryRequest):
    return DuckDBService.execute_query(body.query)"""

@router.post("/execute_query")
async def execute_query(body: QueryRequest, service: ReportsService = Depends(get_reports_service)):
    return service.execute_query_queue(body.query)

@router.post("/save_query")
async def save_query(body: ReportCreate, service: ReportsService = Depends(get_reports_service)):
    return service.create_report(body)

@router.post("/{report_id}/run")
async def run_report(report_id: str, body: ExecuteReportRequest, service: ReportsService = Depends(get_reports_service)):
    return service.run_report(
        report_id,
        body.parameters
    )

@router.get("/jobs/{job_id}")
async def get_job(job_id: str):

    db = SessionLocal()

    try:

        repo = ReportJobsRepository(db)

        service = JobsService(repo)

        return service.get_job(job_id)

    finally:
        db.close()