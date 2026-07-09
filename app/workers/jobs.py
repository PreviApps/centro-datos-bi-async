from datetime import datetime
import tempfile
import os
import uuid

from app.core.database_client import SessionLocal
from app.core.duckdb_client import initialize_duckdb
from app.repositories.reports_jobs_repository import ReportJobsRepository
from app.repositories.reports_repository import ReportsRepository
from app.services.report_query_builder import ReportQueryBuilder
from app.services.duckdb_service import DuckDBService
from app.repositories.minio_repository import MinioRepository

def sumar(a, b):
    return a + b

def execute_report_job(job_id: str):

    initialize_duckdb()

    print("EJECUTA ALGO")
    print("EJECUTA ALGO")

    db = SessionLocal()

    jobs_repo = ReportJobsRepository(db)
    reports_repo = ReportsRepository(db)
    minio_repo = MinioRepository()

    temp_path = None
    object_name = None

    try:

        jobs_repo.update(job_id, {
            "status": "running",
            "started_at": datetime.utcnow()
        })

        job = jobs_repo.get_by_id(job_id)
        report = reports_repo.get_by_id(job.report_id)

        compiled = ReportQueryBuilder.compile(
            report.sql_template,
            job.parameters
        )

        # 🔴 POR AHORA: ejecución simple (sin export aún)
        with tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            delete=False
        ) as tmp:

            temp_path = tmp.name

        result = DuckDBService.export_query_to_excel(
            compiled["query"],
            compiled["params"],
            temp_path
        )

        print("EXCEL GENERATED:", temp_path)
        print("ROWS:", result["rows"])

        object_name = f"temp/jobs/{job_id}.xlsx"

        upload_result = minio_repo.upload_file(
            temp_path,
            object_name
        )
        print("MINIO RESULT:", upload_result)

        jobs_repo.update(job_id, {
            "status": "success",
            "result_path": upload_result["object_name"],
            "finished_at": datetime.utcnow()
        })

    except Exception as e:

        jobs_repo.update(job_id, {
            "status": "failed",
            "error": str(e),
            "finished_at": datetime.utcnow()
        })

        raise

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        db.close()


def execute_preview_job(job_id: str):

    initialize_duckdb()

    print("STEP 1")

    db = SessionLocal()

    jobs_repo = ReportJobsRepository(db)

    try:

        jobs_repo.update(job_id, {
            "status": "running",
            "started_at": datetime.utcnow()
        })

        job = jobs_repo.get_by_id(job_id)

        result = DuckDBService.preview_parquet(
            job.parameters["path"]
        )

        jobs_repo.update(job_id, {
            "status": "success",
            "preview_results": result,
            "finished_at": datetime.utcnow()
        })

    except Exception as e:

        jobs_repo.update(job_id, {
            "status": "failed",
            "error": str(e),
            "finished_at": datetime.utcnow()
        })

        raise

    finally:

        db.close()


def execute_query_job(job_id: str):

    initialize_duckdb()

    print("STEP 1")

    db = SessionLocal()

    jobs_repo = ReportJobsRepository(db)

    try:

        jobs_repo.update(job_id, {
            "status": "running",
            "started_at": datetime.utcnow()
        })

        job = jobs_repo.get_by_id(job_id)

        result = DuckDBService.execute_query(
            job.parameters["query"]
        )

        jobs_repo.update(job_id, {
            "status": "success",
            "preview_results": result,
            "finished_at": datetime.utcnow()
        })

    except Exception as e:

        jobs_repo.update(job_id, {
            "status": "failed",
            "error": str(e),
            "finished_at": datetime.utcnow()
        })

        raise

    finally:

        db.close()