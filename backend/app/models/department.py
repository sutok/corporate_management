"""
Department Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Department(Base):
    """部署モデル"""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, comment="部署ID")
    branch_id = Column(
        Integer,
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属支店ID",
    )
    name = Column(String(255), nullable=False, comment="部署名")
    description = Column(Text, nullable=True, comment="説明")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    branch = relationship("Branch", back_populates="departments")
    user_assignments = relationship(
        "UserDepartmentAssignment",
        back_populates="department",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}', branch_id={self.branch_id})>"
