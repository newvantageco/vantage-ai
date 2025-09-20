"""
Privacy Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PrivacyRequestType(str, Enum):
    EXPORT = "export"
    DELETE = "delete"
    RECTIFICATION = "rectification"
    PORTABILITY = "portability"


class PrivacyRequestStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConsentMethod(str, Enum):
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"


class LegalBasis(str, Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGITIMATE_INTEREST = "legitimate_interest"
    VITAL_INTERESTS = "vital_interests"
    LEGAL_OBLIGATION = "legal_obligation"
    PUBLIC_TASK = "public_task"


# Privacy Request Schemas
class PrivacyRequestCreate(BaseModel):
    requester_email: str = Field(..., description="Email of the person making the request")
    requester_name: Optional[str] = Field(None, description="Name of the person making the request")
    data_categories: Optional[List[str]] = Field(None, description="Categories of data to include")
    specific_data: Optional[Dict[str, Any]] = Field(None, description="Specific data items requested")


class PrivacyRequestResponse(BaseModel):
    id: int
    organization_id: int
    user_id: Optional[int]
    request_type: PrivacyRequestType
    status: PrivacyRequestStatus
    requester_email: str
    requester_name: Optional[str]
    verification_token: Optional[str]
    data_categories: Optional[List[str]]
    specific_data: Optional[Dict[str, Any]]
    processing_notes: Optional[str]
    error_message: Optional[str]
    export_file_url: Optional[str]
    export_file_size: Optional[int]
    deletion_confirmation: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


# Data Retention Policy Schemas
class DataRetentionPolicyCreate(BaseModel):
    data_type: str = Field(..., description="Type of data (user_data, analytics, content, etc.)")
    retention_period_days: int = Field(..., description="Retention period in days")
    auto_delete: bool = Field(False, description="Whether to automatically delete data")
    legal_basis: Optional[LegalBasis] = Field(None, description="Legal basis for retention")
    purpose: Optional[str] = Field(None, description="Purpose of data retention")


class DataRetentionPolicyUpdate(BaseModel):
    data_type: Optional[str] = None
    retention_period_days: Optional[int] = None
    auto_delete: Optional[bool] = None
    legal_basis: Optional[LegalBasis] = None
    purpose: Optional[str] = None
    is_active: Optional[bool] = None


class DataRetentionPolicyResponse(BaseModel):
    id: int
    organization_id: int
    data_type: str
    retention_period_days: int
    auto_delete: bool
    legal_basis: Optional[LegalBasis]
    purpose: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Consent Record Schemas
class ConsentRecordCreate(BaseModel):
    consent_type: str = Field(..., description="Type of consent (marketing, analytics, cookies, etc.)")
    granted: bool = Field(..., description="Whether consent was granted")
    consent_method: ConsentMethod = Field(..., description="Method of consent collection")
    consent_text: Optional[str] = Field(None, description="Text of the consent")
    consent_version: Optional[str] = Field(None, description="Version of the consent text")
    ip_address: Optional[str] = Field(None, description="IP address when consent was given")
    user_agent: Optional[str] = Field(None, description="User agent when consent was given")


class ConsentRecordUpdate(BaseModel):
    granted: Optional[bool] = None
    consent_method: Optional[ConsentMethod] = None
    consent_text: Optional[str] = None
    consent_version: Optional[str] = None


class ConsentRecordResponse(BaseModel):
    id: int
    organization_id: int
    user_id: Optional[int]
    consent_type: str
    granted: bool
    consent_method: ConsentMethod
    consent_text: Optional[str]
    consent_version: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    withdrawn_at: Optional[datetime]
    withdrawal_method: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Data Processing Activity Schemas
class DataProcessingActivityCreate(BaseModel):
    activity_name: str = Field(..., description="Name of the processing activity")
    description: Optional[str] = Field(None, description="Description of the activity")
    personal_data_categories: Optional[List[str]] = Field(None, description="Categories of personal data")
    special_categories: Optional[List[str]] = Field(None, description="Special categories of personal data")
    purposes: Optional[List[str]] = Field(None, description="Purposes of processing")
    legal_basis: Optional[LegalBasis] = Field(None, description="Legal basis for processing")
    data_subjects: Optional[List[str]] = Field(None, description="Types of data subjects")
    recipients: Optional[List[str]] = Field(None, description="Who receives the data")
    third_country_transfers: Optional[List[str]] = Field(None, description="Third country transfers")
    safeguards: Optional[str] = Field(None, description="Safeguards for transfers")
    retention_period: Optional[str] = Field(None, description="Data retention period")


class DataProcessingActivityUpdate(BaseModel):
    activity_name: Optional[str] = None
    description: Optional[str] = None
    personal_data_categories: Optional[List[str]] = None
    special_categories: Optional[List[str]] = None
    purposes: Optional[List[str]] = None
    legal_basis: Optional[LegalBasis] = None
    data_subjects: Optional[List[str]] = None
    recipients: Optional[List[str]] = None
    third_country_transfers: Optional[List[str]] = None
    safeguards: Optional[str] = None
    retention_period: Optional[str] = None
    is_active: Optional[bool] = None


class DataProcessingActivityResponse(BaseModel):
    id: int
    organization_id: int
    activity_name: str
    description: Optional[str]
    personal_data_categories: Optional[List[str]]
    special_categories: Optional[List[str]]
    purposes: Optional[List[str]]
    legal_basis: Optional[LegalBasis]
    data_subjects: Optional[List[str]]
    recipients: Optional[List[str]]
    third_country_transfers: Optional[List[str]]
    safeguards: Optional[str]
    retention_period: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Privacy Compliance Schemas
class PrivacyComplianceResponse(BaseModel):
    organization_id: int
    gdpr_compliant: bool
    ccpa_compliant: bool
    last_audit: Optional[datetime]
    compliance_score: float
    issues: List[str]
    recommendations: List[str]


class DataSubjectRightsResponse(BaseModel):
    right_to_access: bool
    right_to_rectification: bool
    right_to_erasure: bool
    right_to_restrict_processing: bool
    right_to_data_portability: bool
    right_to_object: bool
    automated_decision_making: bool


class PrivacyImpactAssessmentResponse(BaseModel):
    id: int
    organization_id: int
    assessment_name: str
    description: str
    risk_level: str
    mitigation_measures: List[str]
    data_protection_officer_approval: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Privacy Settings Schemas
class PrivacySettingsResponse(BaseModel):
    organization_id: int
    data_retention_enabled: bool
    consent_management_enabled: bool
    cookie_consent_enabled: bool
    data_anonymization_enabled: bool
    audit_logging_enabled: bool
    privacy_policy_url: Optional[str]
    cookie_policy_url: Optional[str]
    data_protection_officer_email: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PrivacySettingsUpdate(BaseModel):
    data_retention_enabled: Optional[bool] = None
    consent_management_enabled: Optional[bool] = None
    cookie_consent_enabled: Optional[bool] = None
    data_anonymization_enabled: Optional[bool] = None
    audit_logging_enabled: Optional[bool] = None
    privacy_policy_url: Optional[str] = None
    cookie_policy_url: Optional[str] = None
    data_protection_officer_email: Optional[str] = None


# Data Breach Schemas
class DataBreachResponse(BaseModel):
    id: int
    organization_id: int
    breach_type: str
    description: str
    affected_data_categories: List[str]
    affected_data_subjects: int
    discovery_date: datetime
    notification_date: Optional[datetime]
    authority_notification_date: Optional[datetime]
    status: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DataBreachCreate(BaseModel):
    breach_type: str = Field(..., description="Type of data breach")
    description: str = Field(..., description="Description of the breach")
    affected_data_categories: List[str] = Field(..., description="Categories of affected data")
    affected_data_subjects: int = Field(..., description="Number of affected data subjects")
    discovery_date: datetime = Field(..., description="Date when breach was discovered")


# Privacy Audit Schemas
class PrivacyAuditResponse(BaseModel):
    id: int
    organization_id: int
    audit_type: str
    audit_date: datetime
    auditor: str
    findings: List[str]
    recommendations: List[str]
    compliance_score: float
    next_audit_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
