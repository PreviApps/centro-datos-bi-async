from app.api.schemas.path import PathRequest
from app.api.schemas.query import QueryRequest
from app.api.schemas.report import ExecuteReportRequest, ReportCreate, ReportUpdate
from app.core.database_client import SessionLocal
from app.providers.reports_providers import get_reports_service
from app.repositories.minio_repository import MinioRepository
from app.repositories.reports_jobs_repository import ReportJobsRepository
from app.services.duckdb_service import DuckDBService
from app.services.jobs_service import JobsService
from app.services.reports_service import ReportsService
from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas.permission import UpdatePermissions
from app.providers.report_permissions_providers import get_permissions_service
from app.services.report_permissions_service import ReportPermissionsService

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

@router.get("/by_user/{user_id}")
async def get_my_reports(
    user_id: str, 
    position_name: str = None,
    service: ReportsService = Depends(get_reports_service)
):
    """
    Retorna solo los reportes a los que el usuario específico tiene permiso otorgado.
    """
    return service.get_reports_for_user(user_id, position_name)

@router.patch("/edit_report/{report_id}")
async def update_report(
    report_id: str, 
    body: ReportUpdate, 
    service: ReportsService = Depends(get_reports_service)
):
    return service.update_report(report_id, body)

@router.delete("/delete_report/{report_id}")
async def delete_report(
    report_id: str, 
    service: ReportsService = Depends(get_reports_service)
):
    return service.delete_report(report_id)

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


@router.get("/{report_id}/users_with_permissions")
def get_report_users_with_permissions(
    report_id: str,
    service: ReportPermissionsService = Depends(get_permissions_service)
):
    """
    Retorna la lista de usuarios del SSO cruzada con los permisos del reporte.
    """
    return service.get_report_users_with_permissions(report_id)

@router.put("/{report_id}/permissions")
def update_report_permissions(
    report_id: str,
    payload: UpdatePermissions,
    service: ReportPermissionsService = Depends(get_permissions_service)
):
    return service.update_user_permissions(report_id, payload.user_ids, payload.admin_user_id)