from typing import Optional

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

    def update(self, report_id: str, data: dict) -> Optional[ReportModel]:
        report = self.get_by_id(report_id)
        if not report:
            return None

        # Excluimos None para actualizar solo los campos provistos
        for key, value in data.items():
            if value is not None:
                setattr(report, key, value)

        self.db.commit()
        self.db.refresh(report)
        return report

    def delete(self, report_id: str) -> bool:
        report = self.get_by_id(report_id)
        if not report:
            return False

        self.db.delete(report)
        self.db.commit()
        return True