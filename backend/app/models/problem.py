"""
Problem Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Problem(Base):
    """課題・相談モデル"""

    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True, comment="課題ID")
    daily_report_id = Column(
        Integer,
        ForeignKey("daily_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="日報ID",
    )
    content = Column(Text, nullable=False, comment="課題内容")
    priority = Column(String(50), nullable=True, comment="優先度")
    status = Column(String(50), nullable=True, comment="ステータス")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    daily_report = relationship("DailyReport", back_populates="problems")

    def __repr__(self):
        return f"<Problem(id={self.id}, daily_report_id={self.daily_report_id}, priority='{self.priority}')>"
