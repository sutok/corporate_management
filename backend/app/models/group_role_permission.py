"""
GroupRolePermission Model
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class GroupRolePermission(Base):
    """グループ権限中間テーブル（グループ⇔権限）"""

    __tablename__ = "group_role_permissions"
    __table_args__ = (
        UniqueConstraint("group_role_id", "role_id", name="uq_group_role_permissions"),
        {"comment": "グループに含まれる権限（グループ⇔権限）"},
    )

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    group_role_id = Column(
        Integer,
        ForeignKey("group_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="グループID",
    )
    role_id = Column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="権限ID",
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="作成日時")

    # リレーションシップ
    group_role = relationship("GroupRole", back_populates="group_role_permissions")
    role = relationship("Role", back_populates="group_role_permissions")
