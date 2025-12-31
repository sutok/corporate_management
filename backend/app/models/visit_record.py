"""
VisitRecord Model
"""
from sqlalchemy import Column, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class VisitRecord(Base):
    """訪問記録モデル"""

    __tablename__ = "visit_records"

    id = Column(Integer, primary_key=True, index=True, comment="訪問記録ID")
    daily_report_id = Column(
        Integer,
        ForeignKey("daily_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="日報ID",
    )
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="顧客ID",
    )
    visit_datetime = Column(DateTime(timezone=True), nullable=False, comment="訪問日時")
    remote = Column(Boolean, default=False, nullable=False, comment="リモート種別 (0:対面 1:リモート)")
    visit_content = Column(Text, nullable=True, comment="訪問内容")
    result = Column(Text, nullable=True, comment="結果")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    daily_report = relationship("DailyReport", back_populates="visit_records")
    customer = relationship("Customer", back_populates="visit_records")

    def __repr__(self):
        return f"<VisitRecord(id={self.id}, customer_id={self.customer_id}, visit_datetime={self.visit_datetime})>"
