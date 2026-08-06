import re
from app.core.queue import queue
from app.repositories.reports_jobs_repository import ReportJobsRepository
from app.services.duckdb_service import DuckDBService
from app.services.report_query_builder import ReportQueryBuilder
from app.workers.jobs import execute_preview_job, execute_query_job, execute_report_job
from fastapi import HTTPException

from app.api.schemas.report import ReportCreate, ReportUpdate
from app.repositories.reports_repository import ReportsRepository


class ReportsService:

    def __init__(self, repo: ReportsRepository):
        self.repo = repo

    def get_report(self, report_id: str):
        report = self.repo.get_by_id(report_id)

        if not report:

            raise HTTPException(
                status_code=404,
                detail="Reporte no encontrado"
            )
        
        return report

    def get_reports(self):
        reports = self.repo.get_all()
        return [
            {
                "id": str(report.id),
                "name": report.name,
                "description": report.description,
                "created_by": report.created_by,
                "created_at": report.created_at,
                "parameters_count": len(report.parameters)
            }
            for report in reports
        ]

    def get_reports_for_user(self, user_id: str, position_name: str = None):
        """
        Retorna la lista formateada de reportes permitidos para un usuario y cargo.
        """
        reports = self.repo.get_all_by_user_permissions(user_id, position_name)
        return [
            {
                "id": str(report.id),
                "name": report.name,
                "description": report.description,
                "created_by": str(report.created_by),
                "created_at": report.created_at,
                "parameters_count": len(report.parameters) if report.parameters else 0
            }
            for report in reports
        ]

    def create_report(self, report: ReportCreate):

        self._validate_parameters(report)

        return self.repo.create(report.model_dump())

    def update_report(self, report_id: str, report_data: ReportUpdate):
        # 1. Verificar si existe
        existing_report = self.get_report(report_id)

        # 2. Si se actualizan el template o los parámetros, revalidar consistencia
        new_template = report_data.sql_template if report_data.sql_template is not None else existing_report.sql_template
        new_params = report_data.parameters if report_data.parameters is not None else existing_report.parameters

        # Construimos un objeto temporal para usar tu método `_validate_parameters`
        temp_report = ReportCreate(
            name=report_data.name or existing_report.name,
            description=report_data.description or existing_report.description or "",
            sql_template=new_template,
            parameters=new_params,
            created_by=report_data.created_by or str(existing_report.created_by)
        )
        self._validate_parameters(temp_report)

        # 3. Mapear datos a diccionario serializando los objetos Pydantic internos
        update_dict = report_data.model_dump(exclude_unset=True)
        
        # Convertir lista de objetos Pydantic `ReportParameter` a lista de dicts (JSONB)
        if "parameters" in update_dict and update_dict["parameters"] is not None:
            update_dict["parameters"] = [p.model_dump() for p in report_data.parameters]

        updated_report = self.repo.update(report_id, update_dict)
        return updated_report

    def delete_report(self, report_id: str):
        # Verificar existencia previa
        self.get_report(report_id)
        
        deleted = self.repo.delete(report_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Reporte no encontrado"
            )
            
        #return {"message": "Reporte eliminado exitosamente", "id": report_id}
        return {"message": "Reporte eliminado exitosamente"}
    
    """def run_report(
        self,
        report_id: str,
        parameters: dict
    ):

        report = self.repo.get_by_id(report_id)

        if not report:

            raise HTTPException(
                status_code=404,
                detail="Reporte no encontrado"
            )

        compiled = ReportQueryBuilder.compile(
            report.sql_template,
            parameters
        )

        return DuckDBService.execute_query(
            compiled["query"],
            compiled["params"]
        )"""
    
    def run_report(self, report_id: str, parameters: dict):

        report = self.repo.get_by_id(report_id)

        if not report:
            raise HTTPException(
                status_code=404,
                detail="Reporte no encontrado"
            )

        db = self.repo.db
        jobs_repo = ReportJobsRepository(db)

        job = jobs_repo.create({
            "report_id": report_id,
            "parameters": parameters,
            "job_type": "report",
            "status": "queued"
        })

        rq_job = queue.enqueue(
            execute_report_job,
            str(job.id),
            job_timeout=3600
        )

        return {
            "job_id": str(job.id),
            "rq_job_id": rq_job.id,
            "status": "queued"
        }
    
    def preview_parquet_queue(self, path: str):

        db = self.repo.db
        jobs_repo = ReportJobsRepository(db)

        job = jobs_repo.create({
            "parameters": {"path": path},
            "job_type": "preview",
            "status": "queued"
        })

        rq_job = queue.enqueue(
            execute_preview_job,
            str(job.id)
        )

        return {
            "job_id": str(job.id),
            "rq_job_id": rq_job.id,
            "status": "queued"
        }
    
    def execute_query_queue(self, query: str):

        db = self.repo.db
        jobs_repo = ReportJobsRepository(db)

        job = jobs_repo.create({
            "parameters": {
                "query": query
            },
            "job_type": "exec",
            "status": "queued"
        })

        rq_job = queue.enqueue(
            execute_query_job,
            str(job.id)
        )

        return {
            "job_id": str(job.id),
            "rq_job_id": rq_job.id,
            "status": "queued"
        }
    
    
    def _validate_parameters(self, report: ReportCreate):

        found_raw = re.findall(r"@\((.*?)\)", report.sql_template)

        found = [f.split(":")[0] for f in found_raw]

        declared = [p.name for p in report.parameters]

        missing = set(found) - set(declared)
        extra = set(declared) - set(found)

        duplicated = {
            x for x in declared
            if declared.count(x) > 1
        }

        if duplicated:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicated parameters: {list(duplicated)}"
            )

        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing parameters in schema: {list(missing)}"
            )

        if extra:
            raise HTTPException(
                status_code=400,
                detail=f"Unused parameters in schema: {list(extra)}"
            )

    def verify_user_access(self, report_id: str, user_id: str, position_name: str) -> bool:
        """
        Método de apoyo para validar antes de ejecutar un reporte específico.
        """
        report = self.get_report(report_id) # Lanza 404 si no existe
        permitted_reports = self.repo.get_all_by_user_permissions(user_id, position_name)
        
        permitted_ids = [str(r.id) for r in permitted_reports]
        if str(report.id) not in permitted_ids:
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para acceder o ejecutar este reporte"
            )
        return True