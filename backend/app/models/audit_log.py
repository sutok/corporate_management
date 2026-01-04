"""
Audit Log Model
APIエンドポイントへのリクエストを記録する操作履歴モデル
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class AuditLog(Base):
    """操作履歴モデル - 全てのAPIリクエストを記録"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, comment="操作履歴ID")
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="操作ユーザーID（未認証の場合はNULL）",
    )
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="企業ID（ユーザーに紐づく場合）",
    )
    method = Column(String(10), nullable=False, comment="HTTPメソッド")
    path = Column(String(500), nullable=False, comment="リクエストパス")
    query_params = Column(Text, nullable=True, comment="クエリパラメータ（JSON）")
    request_body = Column(Text, nullable=True, comment="リクエストボディ（JSON、機密情報は除外）")
    status_code = Column(Integer, nullable=False, comment="レスポンスステータスコード")
    response_time_ms = Column(Integer, nullable=True, comment="レスポンス時間（ミリ秒）")
    ip_address = Column(String(45), nullable=True, comment="クライアントIPアドレス")
    user_agent = Column(String(500), nullable=True, comment="User-Agent")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="作成日時",
    )

    # リレーションシップ
    user = relationship("User", foreign_keys=[user_id])
    company = relationship("Company", foreign_keys=[company_id])

    # 90日以上経過したデータを効率的に削除するためのインデックス
    __table_args__ = (
        Index("idx_audit_logs_created_at", "created_at"),
        Index("idx_audit_logs_user_id_created_at", "user_id", "created_at"),
        Index("idx_audit_logs_company_id_created_at", "company_id", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, method='{self.method}', path='{self.path}', user_id={self.user_id})>"
