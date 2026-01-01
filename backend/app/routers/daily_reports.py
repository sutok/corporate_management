"""
DailyReport API Router
"""
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.daily_report import DailyReport
from app.models.user import User
from app.schemas.daily_report import DailyReportCreate, DailyReportUpdate, DailyReportResponse
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/daily-reports", tags=["daily-reports"])


@router.get("", response_model=List[DailyReportResponse])
async def get_daily_reports(
    user_id: int = None,
    start_date: date = None,
    end_date: date = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """日報一覧取得（同じ企業のユーザーのみ）"""
    # company_idで直接フィルタリング（JOIN不要）
    query = select(DailyReport).where(DailyReport.company_id == current_user.company_id)

    if user_id:
        query = query.where(DailyReport.user_id == user_id)

    if start_date:
        query = query.where(DailyReport.report_date >= start_date)

    if end_date:
        query = query.where(DailyReport.report_date <= end_date)

    result = await db.execute(query.offset(skip).limit(limit))
    daily_reports = result.scalars().all()
    return daily_reports


@router.get("/{report_id}", response_model=DailyReportResponse)
async def get_daily_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """日報詳細取得"""
    result = await db.execute(
        select(DailyReport).where(DailyReport.id == report_id)
    )
    daily_report = result.scalar_one_or_none()

    if not daily_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日報が見つかりません",
        )

    # company_idで直接チェック（JOIN不要）
    if daily_report.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    return daily_report


@router.post("", response_model=DailyReportResponse, status_code=status.HTTP_201_CREATED)
async def create_daily_report(
    daily_report: DailyReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """日報作成"""
    if daily_report.user_id != current_user.id:
        if current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="他のユーザーの日報は作成できません",
            )

        result = await db.execute(select(User).where(User.id == daily_report.user_id))
        user = result.scalar_one_or_none()

        if not user or user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ユーザーが見つかりません",
            )

    # company_idを設定
    new_daily_report = DailyReport(
        **daily_report.model_dump(),
        company_id=current_user.company_id
    )
    db.add(new_daily_report)
    await db.commit()
    await db.refresh(new_daily_report)
    return new_daily_report


@router.put("/{report_id}", response_model=DailyReportResponse)
async def update_daily_report(
    report_id: int,
    daily_report_update: DailyReportUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """日報更新"""
    result = await db.execute(select(DailyReport).where(DailyReport.id == report_id))
    daily_report = result.scalar_one_or_none()

    if not daily_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日報が見つかりません",
        )

    # company_idで直接チェック（JOIN不要）
    if daily_report.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    if daily_report.user_id != current_user.id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他のユーザーの日報は更新できません",
        )

    update_data = daily_report_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(daily_report, field, value)

    await db.commit()
    await db.refresh(daily_report)
    return daily_report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_daily_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """日報削除"""
    result = await db.execute(select(DailyReport).where(DailyReport.id == report_id))
    daily_report = result.scalar_one_or_none()

    if not daily_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日報が見つかりません",
        )

    # company_idで直接チェック（JOIN不要）
    if daily_report.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    if daily_report.user_id != current_user.id and current_user.role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他のユーザーの日報は削除できません",
        )

    await db.delete(daily_report)
    await db.commit()
