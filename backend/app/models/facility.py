"""
Facility Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Facility(Base):
    """施設モデル"""

    __tablename__ = "facilities"

    id = Column(Integer, primary_key=True, index=True, comment="施設ID")
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属企業ID",
    )
    name = Column(String(255), nullable=False, comment="施設名")
    address = Column(String(500), nullable=True, comment="住所")
    phone = Column(String(20), nullable=True, comment="電話番号")
    description = Column(Text, nullable=True, comment="説明")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    company = relationship("Company", back_populates="facilities")
    facility_assignments = relationship(
        "FacilityAssignment",
        back_populates="facility",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Facility(id={self.id}, name='{self.name}', company_id={self.company_id})>"
