"""
User Assignment Models
"""
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserBranchAssignment(Base):
    """ユーザー支店所属モデル"""

    __tablename__ = "user_branch_assignments"

    id = Column(Integer, primary_key=True, index=True, comment="所属ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ユーザーID",
    )
    branch_id = Column(
        Integer,
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="支店ID",
    )
    is_primary = Column(Boolean, default=False, nullable=False, comment="主たる所属か")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    user = relationship("User", back_populates="branch_assignments")
    branch = relationship("Branch", back_populates="user_assignments")

    def __repr__(self):
        return f"<UserBranchAssignment(id={self.id}, user_id={self.user_id}, branch_id={self.branch_id}, is_primary={self.is_primary})>"


class UserDepartmentAssignment(Base):
    """ユーザー部署所属モデル"""

    __tablename__ = "user_department_assignments"

    id = Column(Integer, primary_key=True, index=True, comment="所属ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ユーザーID",
    )
    department_id = Column(
        Integer,
        ForeignKey("departments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="部署ID",
    )
    is_primary = Column(Boolean, default=False, nullable=False, comment="主たる所属か")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    user = relationship("User", back_populates="department_assignments")
    department = relationship("Department", back_populates="user_assignments")

    def __repr__(self):
        return f"<UserDepartmentAssignment(id={self.id}, user_id={self.user_id}, department_id={self.department_id}, is_primary={self.is_primary})>"
