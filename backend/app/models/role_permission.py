"""
RolePermission Model
ロールと権限の多対多リレーション
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class RolePermission(Base):
    """ロール権限関連モデル"""

    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True, comment="ID")
    role_id = Column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ロールID",
    )
    permission_id = Column(
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="権限ID",
    )

    # 制約: 同じロールに同じ権限を重複して付与できない
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    # リレーションシップ
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")

    def __repr__(self):
        return f"<RolePermission(id={self.id}, role_id={self.role_id}, permission_id={self.permission_id})>"
