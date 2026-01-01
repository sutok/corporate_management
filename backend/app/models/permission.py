"""
Permission Model
権限の定義（システム全体で共通）
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Permission(Base):
    """権限モデル"""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True, comment="権限ID")
    code = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="権限コード（例: service.subscribe）",
    )
    name = Column(String(255), nullable=False, comment="権限名")
    description = Column(Text, nullable=True, comment="権限の説明")
    resource_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="リソースタイプ（service, user, facility等）",
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="作成日時"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    role_permissions = relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, code='{self.code}', name='{self.name}')>"
