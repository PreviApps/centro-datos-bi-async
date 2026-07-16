from datetime import datetime
import tempfile
import os
import uuid

from app.core.database_client import SessionLocal
from app.core.duckdb_client import initialize_duckdb
from app.repositories.reports_jobs_repository import ReportJobsRepository
from app.repositories.reports_repository import ReportsRepository
from app.services.parquet_service import ParquetService
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

    parquet_temp = None
    excel_temp = None

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
            #suffix=".xlsx",
            suffix=".parquet",
            delete=False
        ) as tmp:

            parquet_temp = tmp.name

        #result = DuckDBService.export_query_to_excel(
        parquet_result = DuckDBService.execute_query_to_parquet(
            compiled["query"],
            compiled["params"],
            parquet_temp
        )

        print("PARQUET GENERATED:", parquet_result)

        jobs_repo.update(job_id, {
            "status": "parquet_generated",
            "started_at": datetime.utcnow()
        })

        with tempfile.NamedTemporaryFile(
            suffix=".xlsx",
            delete=False
        ) as tmp:

            excel_temp = tmp.name
        
        excel_result = ParquetService.parquet_to_excel(
            parquet_temp,
            excel_temp
        )

        print("EXCEL GENERATED", excel_result)

        jobs_repo.update(job_id, {
            "status": "excel_generated",
            "started_at": datetime.utcnow()
        })

        object_name = f"temp/jobs/{job_id}/report-{datetime.utcnow()}.xlsx"
        #object_name = f"temp/jobs/{job_id}.parquet"

        upload_result = minio_repo.upload_file(
            excel_temp,
            object_name
        )

        print("MINIO RESULT:", upload_result)

        jobs_repo.update(job_id, {
            "status": "success",
            #"result_path": upload_result["object_name"],
            "result_path": upload_result.get("url"),
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
        if parquet_temp and os.path.exists(parquet_temp):
            os.remove(parquet_temp)

        if excel_temp and os.path.exists(excel_temp):
            os.remove(excel_temp)

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