"""
FacilityAssignment Model
ユーザーと施設の多対多関係を管理する中間テーブル
ユーザーは複数の施設に所属でき、契約形態を持つ
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class FacilityAssignment(Base):
    """施設所属管理モデル"""

    __tablename__ = "facility_assignments"

    id = Column(Integer, primary_key=True, index=True, comment="所属ID")
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="企業ID",
    )
    facility_id = Column(
        Integer,
        ForeignKey("facilities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="施設ID",
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ユーザーID",
    )
    contract_type = Column(
        String(50),
        nullable=False,
        comment="契約形態（正社員、契約社員、派遣、業務委託など）",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # ユニーク制約: 同じユーザーが同じ施設に重複して所属できない
    __table_args__ = (
        UniqueConstraint("facility_id", "user_id", name="uq_facility_user"),
    )

    # リレーションシップ
    company = relationship("Company", back_populates="facility_assignments")
    facility = relationship("Facility", back_populates="facility_assignments")
    user = relationship("User", back_populates="facility_assignments")

    def __repr__(self):
        return (
            f"<FacilityAssignment(id={self.id}, "
            f"facility_id={self.facility_id}, user_id={self.user_id}, "
            f"contract_type='{self.contract_type}')>"
        )
