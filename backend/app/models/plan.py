"""
Plan Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Plan(Base):
    """明日やることモデル"""

    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True, comment="計画ID")
    daily_report_id = Column(
        Integer,
        ForeignKey("daily_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="日報ID",
    )
    content = Column(Text, nullable=False, comment="計画内容")
    priority = Column(String(50), nullable=True, comment="優先度")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    daily_report = relationship("DailyReport", back_populates="plans")

    def __repr__(self):
        return f"<Plan(id={self.id}, daily_report_id={self.daily_report_id}, priority='{self.priority}')>"
