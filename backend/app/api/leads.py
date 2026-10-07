"""Leads API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.services import lead_service

router = APIRouter(prefix="/api/leads", tags=["Leads"])


@router.get("", response_model=list[LeadResponse], summary="List leads with filters")
def list_leads(
    status_filter: Optional[str] = Query(None, alias="status"),
    temperature: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    leads, total = lead_service.get_leads(
        db, status=status_filter, temperature=temperature, search=search, skip=skip, limit=limit
    )
    return [LeadResponse.model_validate(l) for l in leads]


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED, summary="Create a lead")
def create_lead(
    data: LeadCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = lead_service.create_lead(db, data)
    return LeadResponse.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadResponse, summary="Get lead by ID")
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.put("/{lead_id}", response_model=LeadResponse, summary="Update a lead")
def update_lead(
    lead_id: int,
    data: LeadUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lead = lead_service.update_lead(db, lead_id, data)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a lead")
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not lead_service.delete_lead(db, lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
