"""
Customer API Router
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.auth.permissions import require_permission

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("customer.view")),
    db: AsyncSession = Depends(get_db),
):
    """
    顧客一覧取得

    必要な権限: customer.view
    注意: 将来的にcustomer.view_assigned権限で担当顧客のみ表示する機能を追加予定
    """
    result = await db.execute(
        select(Customer)
        .where(Customer.company_id == current_user.company_id)
        .offset(skip)
        .limit(limit)
    )
    customers = result.scalars().all()
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: User = Depends(require_permission("customer.view")),
    db: AsyncSession = Depends(get_db),
):
    """
    顧客詳細取得

    必要な権限: customer.view
    """
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="顧客が見つかりません",
        )

    if customer.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    return customer


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    current_user: User = Depends(require_permission("customer.create")),
    db: AsyncSession = Depends(get_db),
):
    """
    顧客作成

    必要な権限: customer.create
    """
    if customer.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他の企業の顧客は作成できません",
        )

    if customer.assigned_user_id:
        result = await db.execute(
            select(User).where(User.id == customer.assigned_user_id)
        )
        assigned_user = result.scalar_one_or_none()

        if not assigned_user or assigned_user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="担当営業が見つかりません",
            )

    new_customer = Customer(**customer.model_dump())
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    return new_customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    current_user: User = Depends(require_permission("customer.update")),
    db: AsyncSession = Depends(get_db),
):
    """
    顧客更新

    必要な権限: customer.update
    """
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="顧客が見つかりません",
        )

    if customer.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    update_data = customer_update.model_dump(exclude_unset=True)

    if "assigned_user_id" in update_data and update_data["assigned_user_id"]:
        result = await db.execute(
            select(User).where(User.id == update_data["assigned_user_id"])
        )
        assigned_user = result.scalar_one_or_none()

        if not assigned_user or assigned_user.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="担当営業が見つかりません",
            )

    for field, value in update_data.items():
        setattr(customer, field, value)

    await db.commit()
    await db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(require_permission("customer.delete")),
    db: AsyncSession = Depends(get_db),
):
    """
    顧客削除

    必要な権限: customer.delete
    """
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="顧客が見つかりません",
        )

    if customer.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="権限がありません",
        )

    await db.delete(customer)
    await db.commit()
