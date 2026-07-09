from app.models.report import ReportModel
from sqlalchemy.orm import Session

class ReportsRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self):

        return (
            self.db.query(ReportModel)
            .all()
        )

    def create(self, data: dict):

        report = ReportModel(**data)

        self.db.add(report)

        self.db.commit()

        self.db.refresh(report)

        return report
    
    def get_by_id(self, report_id: str):

        return (
            self.db.query(ReportModel)
            .filter(ReportModel.id == report_id)
            .first()
        )