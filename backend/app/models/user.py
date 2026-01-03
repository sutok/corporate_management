"""
User Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """ユーザーモデル"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="ユーザーID")
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属企業ID",
    )
    name = Column(String(255), nullable=False, comment="氏名")
    email = Column(String(255), nullable=False, unique=True, index=True, comment="メールアドレス")
    password_hash = Column(String(255), nullable=False, comment="パスワードハッシュ")
    role = Column(String(50), nullable=False, comment="役割（営業/上長など）")
    position = Column(String(100), nullable=True, comment="役職")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    company = relationship("Company", back_populates="users")
    daily_reports = relationship("DailyReport", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="commenter", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="assigned_user")
    branch_assignments = relationship(
        "UserBranchAssignment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    department_assignments = relationship(
        "UserDepartmentAssignment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    subscription_changes = relationship(
        "ServiceSubscriptionHistory",
        back_populates="changed_by_user",
    )
    # 権限管理システム
    user_role_assignments = relationship(
        "UserRoleAssignment",
        foreign_keys="UserRoleAssignment.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_group_assignments = relationship(
        "UserGroupAssignment",
        foreign_keys="UserGroupAssignment.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
