"""
Comment Model
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Comment(Base):
    """コメントモデル"""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, comment="コメントID")
    daily_report_id = Column(
        Integer,
        ForeignKey("daily_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="日報ID",
    )
    commenter_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="コメント者ID",
    )
    content = Column(Text, nullable=False, comment="コメント内容")
    commented_at = Column(DateTime(timezone=True), nullable=False, comment="コメント日時")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    daily_report = relationship("DailyReport", back_populates="comments")
    commenter = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, daily_report_id={self.daily_report_id}, commenter_id={self.commenter_id})>"
