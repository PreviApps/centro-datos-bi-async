from uuid import UUID

from sqlalchemy.orm import Session
from app.models.report import UserReportPermission, PositionReportPermission

class PermissionsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_users_by_report(self, report_id: str) -> list[UserReportPermission]:
        return self.db.query(UserReportPermission).filter(
            UserReportPermission.report_id == report_id
        ).all()

    def get_positions_by_report(self, report_id: str) -> list[PositionReportPermission]:
        return self.db.query(PositionReportPermission).filter(
            PositionReportPermission.report_id == report_id
        ).all()

    def add_user_permission(self, report_id: str, user_ids: str, granted_by: str):
        if not user_ids:
            return
        report_uuid = UUID(report_id) if isinstance(report_id, str) else report_id
        
        new_perms = [
            UserReportPermission(
                user_id=UUID(uid) if isinstance(uid, str) else uid,
                report_id=report_uuid,
                granted_by=granted_by
            )
            for uid in user_ids
        ]
        self.db.bulk_save_objects(new_perms)

    def remove_user_permissions(self, report_id: str, user_ids: list[str]):
        if not user_ids:
            return
        #report_uuid = UUID(report_id) if isinstance(report_id, str) else report_id
        #user_uuids = [UUID(uid) if isinstance(uid, str) else uid for uid in user_ids]

        self.db.query(UserReportPermission).filter(
            UserReportPermission.report_id == report_id,
            UserReportPermission.user_id.in_(user_ids)
        ).delete(synchronize_session=False)

    def add_position_permission(self, report_id: str, position_name: str):
        new_perm = PositionReportPermission(
            position_name=position_name,
            report_id=report_id
        )
        self.db.add(new_perm)

    def remove_position_permissions(self, report_id: str, position_names: list[str]):
        if position_names:
            self.db.query(PositionReportPermission).filter(
                PositionReportPermission.report_id == report_id,
                PositionReportPermission.position_name.in_(position_names)
            ).delete(synchronize_session=False)

    def commit(self):
        self.db.commit()