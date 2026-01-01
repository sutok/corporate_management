"""
Role Model
ロール定義（企業別 + システム共通）
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Role(Base):
    """ロールモデル"""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True, comment="ロールID")
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="企業ID（NULL=システムロール）",
    )
    code = Column(
        String(50),
        nullable=False,
        index=True,
        comment="ロールコード（例: subscription_manager）",
    )
    name = Column(String(255), nullable=False, comment="ロール名")
    description = Column(Text, nullable=True, comment="ロールの説明")
    is_system = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="システムロール（削除・編集不可）",
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

    # 制約
    __table_args__ = (
        # 企業内でcodeはユニーク（システムロールはcompany_id=NULLで別管理）
        UniqueConstraint("company_id", "code", name="uq_company_role_code"),
        # システムロールはcompany_idがNULL
        CheckConstraint(
            "(is_system = false) OR (is_system = true AND company_id IS NULL)",
            name="ck_system_role_no_company",
        ),
    )

    # リレーションシップ
    company = relationship("Company", backref="roles")
    role_permissions = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    user_roles = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )

    def __repr__(self):
        company_str = f"company_id={self.company_id}" if self.company_id else "SYSTEM"
        return f"<Role(id={self.id}, {company_str}, code='{self.code}', name='{self.name}')>"
