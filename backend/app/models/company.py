"""
Company Model
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Company(Base):
    """企業モデル"""

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, comment="企業ID")
    name = Column(String(255), nullable=False, comment="企業名")
    address = Column(String(500), nullable=True, comment="住所")
    phone = Column(String(20), nullable=True, comment="電話番号")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    branches = relationship("Branch", back_populates="company", cascade="all, delete-orphan")
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="company", cascade="all, delete-orphan")
    daily_reports = relationship("DailyReport", back_populates="company", cascade="all, delete-orphan")
    facilities = relationship("Facility", back_populates="company", cascade="all, delete-orphan")
    facility_assignments = relationship(
        "FacilityAssignment",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    service_subscriptions = relationship(
        "CompanyServiceSubscription",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    subscription_history = relationship(
        "ServiceSubscriptionHistory",
        back_populates="company",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"
