"""Campaigns API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignUpdate
from app.services import campaign_service

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])


class AddLeadsRequest(BaseModel):
    lead_ids: list[int]


@router.get("", response_model=list[CampaignResponse], summary="List campaigns")
def list_campaigns(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    campaigns, total = campaign_service.get_campaigns(db, status=status_filter, skip=skip, limit=limit)
    return [CampaignResponse.model_validate(c) for c in campaigns]


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED, summary="Create campaign")
def create_campaign(
    data: CampaignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    campaign = campaign_service.create_campaign(db, data)
    return CampaignResponse.model_validate(campaign)


@router.get("/{campaign_id}", response_model=CampaignResponse, summary="Get campaign by ID")
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    campaign = campaign_service.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse.model_validate(campaign)


@router.put("/{campaign_id}", response_model=CampaignResponse, summary="Update campaign")
def update_campaign(
    campaign_id: int,
    data: CampaignUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    campaign = campaign_service.update_campaign(db, campaign_id, data)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse.model_validate(campaign)


@router.post("/{campaign_id}/leads", summary="Add leads to campaign")
def add_leads_to_campaign(
    campaign_id: int,
    data: AddLeadsRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    added = campaign_service.add_leads_to_campaign(db, campaign_id, data.lead_ids)
    return {"added": added}
