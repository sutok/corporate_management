"""
Role Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Role(Base):
    """個別権限モデル"""

    __tablename__ = "roles"
    __table_args__ = {"comment": "個別権限一覧"}

    id = Column(Integer, primary_key=True, index=True, comment="権限ID")
    code = Column(String(100), nullable=False, unique=True, comment="権限コード（例: user.create）")
    name = Column(String(255), nullable=False, comment="権限名")
    description = Column(Text, nullable=True, comment="権限の説明")
    resource_type = Column(String(50), nullable=False, index=True, comment="リソース種別（例: user）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新日時",
    )

    # リレーションシップ
    user_role_assignments = relationship(
        "UserRoleAssignment",
        back_populates="role",
        cascade="all, delete-orphan",
    )
    group_role_permissions = relationship(
        "GroupRolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )
