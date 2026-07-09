from datetime import timedelta
from fastapi import HTTPException

from app.repositories.reports_jobs_repository import ReportJobsRepository
from app.core.minio_client import client, BUCKET


class JobsService:

    def __init__(self, repo: ReportJobsRepository):
        self.repo = repo

    def get_job(self, job_id: str):

        job = self.repo.get_by_id(job_id)

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job no encontrado"
            )

        response = {
            "id": str(job.id),
            "report_id": str(job.report_id),
            "status": job.status,
            "job_type": job.job_type,
            "parameters": job.parameters,
            "error": job.error,
            "result_path": job.result_path,
            "preview_results": job.preview_results,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "finished_at": job.finished_at
        }

        if job.status == "success" and job.result_path:

            response["download_url"] = client.presigned_get_object(
                BUCKET,
                job.result_path,
                expires=timedelta(minutes=5)
            )

        return response