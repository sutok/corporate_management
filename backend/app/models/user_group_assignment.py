"""
UserGroupAssignment Model
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserGroupAssignment(Base):
    """ユーザーグループ所属モデル（ユーザー⇔グループ）"""

    __tablename__ = "user_group_assignments"
    __table_args__ = (
        UniqueConstraint("user_id", "group_role_id", name="uq_user_group_assignments"),
        {"comment": "ユーザーのグループ所属（ユーザー⇔グループ）"},
    )

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ユーザーID",
    )
    group_role_id = Column(
        Integer,
        ForeignKey("group_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="グループID",
    )
    assigned_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="割り当てた人",
    )
    assigned_at = Column(DateTime(timezone=True), nullable=False, comment="割り当て日時")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="作成日時")

    # リレーションシップ
    user = relationship("User", foreign_keys=[user_id], back_populates="user_group_assignments")
    group_role = relationship("GroupRole", back_populates="user_group_assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])
