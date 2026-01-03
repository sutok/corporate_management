"""
GroupRole Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class GroupRole(Base):
    """グループモデル"""

    __tablename__ = "group_roles"
    __table_args__ = {"comment": "グループ一覧"}

    id = Column(Integer, primary_key=True, index=True, comment="グループID")
    code = Column(String(100), nullable=False, unique=True, comment="グループコード（例: admin）")
    name = Column(String(255), nullable=False, comment="グループ名")
    description = Column(Text, nullable=True, comment="グループの説明")
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="企業ID（NULLの場合はシステムグループ）",
    )
    is_system = Column(Boolean, nullable=False, server_default="false", comment="システムグループか")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新日時",
    )

    # リレーションシップ
    company = relationship("Company", back_populates="group_roles")
    group_role_permissions = relationship(
        "GroupRolePermission",
        back_populates="group_role",
        cascade="all, delete-orphan",
    )
    user_group_assignments = relationship(
        "UserGroupAssignment",
        back_populates="group_role",
        cascade="all, delete-orphan",
    )
