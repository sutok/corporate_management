"""
UserRole Model
ユーザーとロールの多対多リレーション
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserRole(Base):
    """ユーザーロール関連モデル"""

    __tablename__ = "user_roles"

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
        comment="ロールID",
    )
    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="割り当て日時",
    )
    assigned_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="割り当て実行者ID",
    )

    # 制約: 同じユーザーに同じロールを重複して付与できない
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    # リレーションシップ
    user = relationship("User", foreign_keys=[user_id], back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    assigner = relationship("User", foreign_keys=[assigned_by])

    def __repr__(self):
        return f"<UserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"
