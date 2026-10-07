"""Calls API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.call import CallCreate, CallResponse, CallUpdate
from app.services import call_service

router = APIRouter(prefix="/api/calls", tags=["Calls"])


@router.get("", response_model=list[CallResponse], summary="List calls with filters")
def list_calls(
    direction: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    outcome: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    calls, total = call_service.get_calls(
        db, direction=direction, status=status_filter,
        outcome=outcome, search=search, skip=skip, limit=limit
    )
    return [CallResponse.model_validate(c) for c in calls]


@router.post("", response_model=CallResponse, status_code=status.HTTP_201_CREATED, summary="Create a call")
def create_call(
    data: CallCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    call = call_service.create_call(db, data)
    return CallResponse.model_validate(call)


@router.get("/{call_id}", response_model=CallResponse, summary="Get call by ID")
def get_call(
    call_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    call = call_service.get_call(db, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return CallResponse.model_validate(call)


@router.put("/{call_id}", response_model=CallResponse, summary="Update a call")
def update_call(
    call_id: int,
    data: CallUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    call = call_service.update_call(db, call_id, data)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return CallResponse.model_validate(call)
