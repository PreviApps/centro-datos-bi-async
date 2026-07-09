from app.models.report_job import ReportJobModel
from sqlalchemy.orm import Session

class ReportJobsRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict):

        job = ReportJobModel(**data)

        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return job

    def get_by_id(self, job_id: str):

        return (
            self.db.query(ReportJobModel)
            .filter(ReportJobModel.id == job_id)
            .first()
        )

    def update(self, job_id: str, values: dict):

        job = self.get_by_id(job_id)

        if not job:
            return None

        for k, v in values.items():
            setattr(job, k, v)

        try:
            self.db.commit()
            self.db.refresh(job)
            return job
        except Exception:
            self.db.rollback()
            raise