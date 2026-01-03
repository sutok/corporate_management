"""
UserRoleAssignment Model
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRoleAssignment(Base):
    """ユーザー個別権限割り当てモデル（ユーザー⇔権限）"""

    __tablename__ = "user_role_assignments"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role_assignments"),
        {"comment": "ユーザーへの個別権限割り当て（ユーザー⇔権限）"},
    )

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ユーザーID",
    )
    role_id = Column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="権限ID",
    )
    granted_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="付与者ID",
    )
    granted_at = Column(DateTime(timezone=True), nullable=False, comment="付与日時")
    reason = Column(Text, nullable=True, comment="付与理由（監査用）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="作成日時")

    # リレーションシップ
    user = relationship("User", foreign_keys=[user_id], back_populates="user_role_assignments")
    role = relationship("Role", back_populates="user_role_assignments")
    granter = relationship("User", foreign_keys=[granted_by])
