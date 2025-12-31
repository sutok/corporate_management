"""
Branch Model
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Branch(Base):
    """支店モデル"""

    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True, comment="支店ID")
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属企業ID",
    )
    name = Column(String(255), nullable=False, comment="支店名")
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
    company = relationship("Company", back_populates="branches")
    departments = relationship("Department", back_populates="branch", cascade="all, delete-orphan")
    user_assignments = relationship(
        "UserBranchAssignment",
        back_populates="branch",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Branch(id={self.id}, name='{self.name}', company_id={self.company_id})>"
