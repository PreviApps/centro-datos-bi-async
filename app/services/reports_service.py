import re
from app.core.queue import queue
from app.repositories.reports_jobs_repository import ReportJobsRepository
from app.services.duckdb_service import DuckDBService
from app.services.report_query_builder import ReportQueryBuilder
from app.workers.jobs import execute_preview_job, execute_query_job, execute_report_job
from fastapi import HTTPException

from app.api.schemas.report import ReportCreate
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

    def create_report(self, report: ReportCreate):

        self._validate_parameters(report)

        return self.repo.create(report.model_dump())
    
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
            str(job.id)
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