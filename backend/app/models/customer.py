"""
Customer Model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Customer(Base):
    """顧客モデル"""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, comment="顧客ID")
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属企業ID",
    )
    assigned_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="担当営業ID",
    )
    name = Column(String(255), nullable=False, comment="顧客名")
    company_name = Column(String(255), nullable=True, comment="会社名")
    address = Column(String(500), nullable=True, comment="住所")
    phone = Column(String(20), nullable=True, comment="電話番号")
    email = Column(String(255), nullable=True, comment="メールアドレス")
    notes = Column(Text, nullable=True, comment="備考")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="作成日時")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    # リレーションシップ
    company = relationship("Company", back_populates="customers")
    assigned_user = relationship("User", back_populates="customers")
    visit_records = relationship("VisitRecord", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', company_name='{self.company_name}')>"
