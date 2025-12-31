"""
Service Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Service(Base):
    """サービスマスタモデル"""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True, comment="サービスID")
    service_code = Column(String(100), nullable=False, unique=True, index=True, comment="サービスコード")
    service_name = Column(String(255), nullable=False, comment="サービス名")
    description = Column(Text, nullable=True, comment="サービス説明")
    base_price = Column(Numeric(10, 2), nullable=False, comment="基本料金")
    is_active = Column(Boolean, default=True, nullable=False, comment="提供中か")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    subscriptions = relationship(
        "CompanyServiceSubscription",
        back_populates="service",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Service(id={self.id}, service_code='{self.service_code}', service_name='{self.service_name}')>"


class CompanyServiceSubscription(Base):
    """企業サービス契約モデル"""

    __tablename__ = "company_service_subscriptions"

    id = Column(Integer, primary_key=True, index=True, comment="契約ID")
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="企業ID",
    )
    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="サービスID",
    )
    status = Column(
        String(50),
        nullable=False,
        default="active",
        comment="契約状態（active/suspended/cancelled）",
    )
    start_date = Column(Date, nullable=False, comment="契約開始日")
    end_date = Column(Date, nullable=True, comment="契約終了日")
    monthly_price = Column(Numeric(10, 2), nullable=False, comment="月額料金（企業別カスタム料金）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    company = relationship("Company", back_populates="service_subscriptions")
    service = relationship("Service", back_populates="subscriptions")
    history = relationship(
        "ServiceSubscriptionHistory",
        back_populates="subscription",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<CompanyServiceSubscription(id={self.id}, company_id={self.company_id}, service_id={self.service_id}, status='{self.status}')>"


class ServiceSubscriptionHistory(Base):
    """サービス契約変更履歴モデル"""

    __tablename__ = "service_subscription_history"

    id = Column(Integer, primary_key=True, index=True, comment="履歴ID")
    subscription_id = Column(
        Integer,
        ForeignKey("company_service_subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="契約ID",
    )
    changed_by_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="変更者ID",
    )
    change_type = Column(String(50), nullable=False, comment="変更種別（create/update/delete）")
    old_status = Column(String(50), nullable=True, comment="変更前の契約状態")
    new_status = Column(String(50), nullable=True, comment="変更後の契約状態")
    old_end_date = Column(Date, nullable=True, comment="変更前の終了日")
    new_end_date = Column(Date, nullable=True, comment="変更後の終了日")
    old_monthly_price = Column(Numeric(10, 2), nullable=True, comment="変更前の月額料金")
    new_monthly_price = Column(Numeric(10, 2), nullable=True, comment="変更後の月額料金")
    change_reason = Column(Text, nullable=True, comment="変更理由")
    changed_at = Column(DateTime(timezone=True), nullable=False, comment="変更日時")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")

    # リレーションシップ
    subscription = relationship("CompanyServiceSubscription", back_populates="history")
    changed_by_user = relationship("User", back_populates="subscription_changes")

    def __repr__(self):
        return f"<ServiceSubscriptionHistory(id={self.id}, subscription_id={self.subscription_id}, change_type='{self.change_type}')>"
