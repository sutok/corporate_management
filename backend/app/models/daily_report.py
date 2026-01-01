"""
DailyReport Model
"""
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class DailyReport(Base):
    """日報モデル"""

    __tablename__ = "daily_reports"

    id = Column(Integer, primary_key=True, index=True, comment="日報ID")
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="企業ID",
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="作成者ID",
    )
    report_date = Column(Date, nullable=False, index=True, comment="報告日")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    company = relationship("Company", back_populates="daily_reports")
    user = relationship("User", back_populates="daily_reports")
    visit_records = relationship("VisitRecord", back_populates="daily_report", cascade="all, delete-orphan")
    problems = relationship("Problem", back_populates="daily_report", cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="daily_report", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="daily_report", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DailyReport(id={self.id}, user_id={self.user_id}, report_date={self.report_date})>"
