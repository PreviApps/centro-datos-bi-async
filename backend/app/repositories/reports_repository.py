from typing import List, Optional

from app.models.report import PositionReportPermission, ReportModel, UserReportPermission
from sqlalchemy import or_
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

    def get_all_by_user_permissions(self, user_id: str, position_name: str) -> List[ReportModel]:
        """
        Consulta los reportes a los que tiene acceso el usuario,
        ya sea directamente por su user_id o por su posición/cargo.
        """
        return (
            self.db.query(ReportModel)
            .outerjoin(
                UserReportPermission,
                (UserReportPermission.report_id == ReportModel.id) & (UserReportPermission.user_id == user_id)
            )
            .outerjoin(
                PositionReportPermission,
                (PositionReportPermission.report_id == ReportModel.id) & (PositionReportPermission.position_name == position_name)
            )
            .filter(
                or_(
                    UserReportPermission.report_id.is_not(None),
                    PositionReportPermission.report_id.is_not(None)
                )
            )
            .distinct()
            .all()
        )