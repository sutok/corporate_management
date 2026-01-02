"""
UserPermission Model
ユーザー個別権限（グループ権限 + 個別権限のLinux風権限管理）
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserPermission(Base):
    """ユーザー個別権限モデル"""

    __tablename__ = "user_permissions"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ユーザーID",
    )
    permission_id = Column(
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="権限ID",
    )
    granted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="付与者ID（監査用）",
    )
    granted_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="付与日時",
    )
    reason = Column(
        Text,
        nullable=True,
        comment="付与理由（任意）",
    )

    # 制約: 同じユーザーに同じ権限を重複付与できない
    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", name="uq_user_permission"),
    )

    # リレーションシップ
    user = relationship("User", foreign_keys=[user_id], back_populates="user_permissions")
    permission = relationship("Permission", back_populates="user_permissions")
    granter = relationship("User", foreign_keys=[granted_by])

    def __repr__(self):
        return f"<UserPermission(id={self.id}, user_id={self.user_id}, permission_id={self.permission_id})>"
