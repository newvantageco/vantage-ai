"""
Privacy API Router
Handles GDPR compliance, data export, and deletion requests
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.api.deps import get_db, get_current_user
from app.schemas.privacy import (
    PrivacyRequestResponse, PrivacyRequestCreate,
    DataRetentionPolicyResponse, DataRetentionPolicyCreate, DataRetentionPolicyUpdate,
    ConsentRecordResponse, ConsentRecordCreate, ConsentRecordUpdate,
    DataProcessingActivityResponse, DataProcessingActivityCreate, DataProcessingActivityUpdate
)
from app.models.privacy import (
    PrivacyRequest, DataExport, DeletionRequest, DataRetentionPolicy, ConsentRecord, DataProcessingActivity
)
from app.models.cms import UserAccount, Organization
from app.workers.tasks.privacy_tasks import process_data_export_task, process_data_deletion_task

router = APIRouter()


# Privacy Request endpoints
@router.post("/privacy/export", response_model=PrivacyRequestResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_data_export(
    request: PrivacyRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> PrivacyRequestResponse:
    """
    Request a data export (GDPR Article 20 - Right to data portability).
    """
    try:
        # Create privacy request
        privacy_request = PrivacyRequest(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            request_type="export",
            requester_email=request.requester_email,
            requester_name=request.requester_name,
            verification_token=str(uuid.uuid4()),
            data_categories=request.data_categories,
            specific_data=request.specific_data,
            expires_at=datetime.utcnow() + timedelta(days=30)  # 30 days to download
        )
        
        db.add(privacy_request)
        db.commit()
        db.refresh(privacy_request)
        
        # Queue background task for data export
        task = process_data_export_task.delay(
            request_id=privacy_request.id,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            data_categories=request.data_categories,
            specific_data=request.specific_data
        )
        
        return PrivacyRequestResponse.from_orm(privacy_request)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data export request failed: {str(e)}"
        )


@router.post("/privacy/delete", response_model=PrivacyRequestResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_data_deletion(
    request: PrivacyRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> PrivacyRequestResponse:
    """
    Request data deletion (GDPR Article 17 - Right to erasure).
    """
    try:
        # Create privacy request
        privacy_request = PrivacyRequest(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            request_type="delete",
            requester_email=request.requester_email,
            requester_name=request.requester_name,
            verification_token=str(uuid.uuid4()),
            data_categories=request.data_categories,
            specific_data=request.specific_data,
            expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days to process
        )
        
        db.add(privacy_request)
        db.commit()
        db.refresh(privacy_request)
        
        # Queue background task for data deletion
        task = process_data_deletion_task.delay(
            request_id=privacy_request.id,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            data_categories=request.data_categories,
            specific_data=request.specific_data
        )
        
        return PrivacyRequestResponse.from_orm(privacy_request)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data deletion request failed: {str(e)}"
        )


@router.get("/privacy/requests", response_model=List[PrivacyRequestResponse])
async def list_privacy_requests(
    skip: int = 0,
    limit: int = 20,
    request_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[PrivacyRequestResponse]:
    """
    List privacy requests for the current organization.
    """
    query = db.query(PrivacyRequest).filter(
        PrivacyRequest.organization_id == current_user.organization_id
    )
    
    if request_type:
        query = query.filter(PrivacyRequest.request_type == request_type)
    if status:
        query = query.filter(PrivacyRequest.status == status)
    
    requests = query.offset(skip).limit(limit).all()
    return [PrivacyRequestResponse.from_orm(req) for req in requests]


@router.get("/privacy/requests/{request_id}", response_model=PrivacyRequestResponse)
async def get_privacy_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> PrivacyRequestResponse:
    """
    Get a specific privacy request.
    """
    privacy_request = db.query(PrivacyRequest).filter(
        PrivacyRequest.id == request_id,
        PrivacyRequest.organization_id == current_user.organization_id
    ).first()
    
    if not privacy_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Privacy request not found"
        )
    
    return PrivacyRequestResponse.from_orm(privacy_request)


@router.post("/privacy/requests/{request_id}/verify", status_code=status.HTTP_200_OK)
async def verify_privacy_request(
    request_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify a privacy request using the verification token.
    """
    privacy_request = db.query(PrivacyRequest).filter(
        PrivacyRequest.id == request_id,
        PrivacyRequest.verification_token == token
    ).first()
    
    if not privacy_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Privacy request not found or invalid token"
        )
    
    if privacy_request.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Privacy request has expired"
        )
    
    return {"status": "success", "message": "Privacy request verified"}


# Data Retention Policy endpoints
@router.post("/privacy/retention-policies", response_model=DataRetentionPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_retention_policy(
    policy: DataRetentionPolicyCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> DataRetentionPolicyResponse:
    """
    Create a data retention policy.
    """
    retention_policy = DataRetentionPolicy(
        organization_id=current_user.organization_id,
        **policy.dict()
    )
    
    db.add(retention_policy)
    db.commit()
    db.refresh(retention_policy)
    
    return DataRetentionPolicyResponse.from_orm(retention_policy)


@router.get("/privacy/retention-policies", response_model=List[DataRetentionPolicyResponse])
async def list_retention_policies(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[DataRetentionPolicyResponse]:
    """
    List data retention policies for the current organization.
    """
    policies = db.query(DataRetentionPolicy).filter(
        DataRetentionPolicy.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    
    return [DataRetentionPolicyResponse.from_orm(policy) for policy in policies]


@router.put("/privacy/retention-policies/{policy_id}", response_model=DataRetentionPolicyResponse)
async def update_retention_policy(
    policy_id: int,
    policy_update: DataRetentionPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> DataRetentionPolicyResponse:
    """
    Update a data retention policy.
    """
    policy = db.query(DataRetentionPolicy).filter(
        DataRetentionPolicy.id == policy_id,
        DataRetentionPolicy.organization_id == current_user.organization_id
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retention policy not found"
        )
    
    update_data = policy_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)
    
    db.commit()
    db.refresh(policy)
    
    return DataRetentionPolicyResponse.from_orm(policy)


# Consent Record endpoints
@router.post("/privacy/consent", response_model=ConsentRecordResponse, status_code=status.HTTP_201_CREATED)
async def record_consent(
    consent: ConsentRecordCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ConsentRecordResponse:
    """
    Record user consent.
    """
    consent_record = ConsentRecord(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        **consent.dict()
    )
    
    db.add(consent_record)
    db.commit()
    db.refresh(consent_record)
    
    return ConsentRecordResponse.from_orm(consent_record)


@router.get("/privacy/consent", response_model=List[ConsentRecordResponse])
async def list_consent_records(
    skip: int = 0,
    limit: int = 20,
    consent_type: Optional[str] = None,
    granted: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ConsentRecordResponse]:
    """
    List consent records for the current organization.
    """
    query = db.query(ConsentRecord).filter(
        ConsentRecord.organization_id == current_user.organization_id
    )
    
    if consent_type:
        query = query.filter(ConsentRecord.consent_type == consent_type)
    if granted is not None:
        query = query.filter(ConsentRecord.granted == granted)
    
    records = query.offset(skip).limit(limit).all()
    return [ConsentRecordResponse.from_orm(record) for record in records]


@router.put("/privacy/consent/{consent_id}/withdraw", status_code=status.HTTP_200_OK)
async def withdraw_consent(
    consent_id: int,
    withdrawal_method: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Withdraw user consent.
    """
    consent_record = db.query(ConsentRecord).filter(
        ConsentRecord.id == consent_id,
        ConsentRecord.organization_id == current_user.organization_id
    ).first()
    
    if not consent_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent record not found"
        )
    
    consent_record.granted = False
    consent_record.withdrawn_at = datetime.utcnow()
    consent_record.withdrawal_method = withdrawal_method
    
    db.commit()
    
    return {"status": "success", "message": "Consent withdrawn"}


# Data Processing Activity endpoints
@router.post("/privacy/processing-activities", response_model=DataProcessingActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_processing_activity(
    activity: DataProcessingActivityCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> DataProcessingActivityResponse:
    """
    Create a data processing activity record.
    """
    processing_activity = DataProcessingActivity(
        organization_id=current_user.organization_id,
        **activity.dict()
    )
    
    db.add(processing_activity)
    db.commit()
    db.refresh(processing_activity)
    
    return DataProcessingActivityResponse.from_orm(processing_activity)


@router.get("/privacy/processing-activities", response_model=List[DataProcessingActivityResponse])
async def list_processing_activities(
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[DataProcessingActivityResponse]:
    """
    List data processing activities for the current organization.
    """
    query = db.query(DataProcessingActivity).filter(
        DataProcessingActivity.organization_id == current_user.organization_id
    )
    
    if is_active is not None:
        query = query.filter(DataProcessingActivity.is_active == is_active)
    
    activities = query.offset(skip).limit(limit).all()
    return [DataProcessingActivityResponse.from_orm(activity) for activity in activities]


@router.get("/privacy/processing-activities/{activity_id}", response_model=DataProcessingActivityResponse)
async def get_processing_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> DataProcessingActivityResponse:
    """
    Get a specific data processing activity.
    """
    activity = db.query(DataProcessingActivity).filter(
        DataProcessingActivity.id == activity_id,
        DataProcessingActivity.organization_id == current_user.organization_id
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing activity not found"
        )
    
    return DataProcessingActivityResponse.from_orm(activity)


@router.put("/privacy/processing-activities/{activity_id}", response_model=DataProcessingActivityResponse)
async def update_processing_activity(
    activity_id: int,
    activity_update: DataProcessingActivityUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> DataProcessingActivityResponse:
    """
    Update a data processing activity.
    """
    activity = db.query(DataProcessingActivity).filter(
        DataProcessingActivity.id == activity_id,
        DataProcessingActivity.organization_id == current_user.organization_id
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processing activity not found"
        )
    
    update_data = activity_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)
    
    db.commit()
    db.refresh(activity)
    
    return DataProcessingActivityResponse.from_orm(activity)


# Privacy Dashboard
@router.get("/privacy/dashboard", response_model=Dict[str, Any])
async def get_privacy_dashboard(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get privacy compliance dashboard data.
    """
    try:
        # Get privacy requests summary
        total_requests = db.query(PrivacyRequest).filter(
            PrivacyRequest.organization_id == current_user.organization_id
        ).count()
        
        pending_requests = db.query(PrivacyRequest).filter(
            PrivacyRequest.organization_id == current_user.organization_id,
            PrivacyRequest.status == "pending"
        ).count()
        
        completed_requests = db.query(PrivacyRequest).filter(
            PrivacyRequest.organization_id == current_user.organization_id,
            PrivacyRequest.status == "completed"
        ).count()
        
        # Get consent summary
        total_consent_records = db.query(ConsentRecord).filter(
            ConsentRecord.organization_id == current_user.organization_id
        ).count()
        
        active_consent = db.query(ConsentRecord).filter(
            ConsentRecord.organization_id == current_user.organization_id,
            ConsentRecord.granted == True,
            ConsentRecord.withdrawn_at.is_(None)
        ).count()
        
        # Get retention policies
        active_policies = db.query(DataRetentionPolicy).filter(
            DataRetentionPolicy.organization_id == current_user.organization_id,
            DataRetentionPolicy.is_active == True
        ).count()
        
        # Get processing activities
        active_activities = db.query(DataProcessingActivity).filter(
            DataProcessingActivity.organization_id == current_user.organization_id,
            DataProcessingActivity.is_active == True
        ).count()
        
        return {
            "privacy_requests": {
                "total": total_requests,
                "pending": pending_requests,
                "completed": completed_requests
            },
            "consent": {
                "total_records": total_consent_records,
                "active_consent": active_consent,
                "withdrawn": total_consent_records - active_consent
            },
            "compliance": {
                "retention_policies": active_policies,
                "processing_activities": active_activities
            },
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Privacy dashboard failed: {str(e)}"
        )
