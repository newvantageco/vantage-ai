# Privacy Compliance Implementation

This document describes the privacy compliance features implemented in the Vantage AI platform.

## Overview

The privacy compliance system provides:
- Data export functionality (GDPR Article 20)
- Data deletion functionality (GDPR Article 17)
- Configurable data retention policies
- Audit logging for privacy operations

## Components

### 1. Database Models

#### `OrgRetention` (`app/models/retention.py`)
- Stores retention policies per organization
- Configurable retention periods for messages, logs, and metrics
- Default values: 90 days for messages, 30 days for logs, 365 days for metrics

#### `PrivacyJob` (`app/models/retention.py`)
- Tracks privacy-related operations (export/delete)
- Provides audit trail and status tracking
- Stores file URLs for completed exports

### 2. API Endpoints

#### Privacy Routes (`app/routes/privacy.py`)

- `POST /privacy/export` - Request data export
- `POST /privacy/delete` - Request data deletion
- `GET /privacy/jobs` - List privacy jobs
- `GET /privacy/jobs/{job_id}` - Get specific job details
- `GET /privacy/retention` - Get retention policy
- `PUT /privacy/retention` - Update retention policy

### 3. Background Workers

#### Privacy Worker (`app/workers/privacy_worker.py`)
- Processes export and deletion jobs asynchronously
- Handles data collection and anonymization
- Manages file uploads and signed URLs

#### Cleanup Worker (`workers/privacy_cleanup_worker.py`)
- Runs nightly to enforce retention policies
- Anonymizes expired data according to policies

### 4. Web Interface

#### Privacy Settings Page (`web/src/app/(dashboard)/privacy/page.tsx`)
- Retention policy configuration
- Data export interface
- Data deletion interface with confirmation
- Job status monitoring

## Features

### Data Export
- Exports all organization data in JSON and CSV formats
- Includes conversations, content, schedules, metrics
- Optional media file inclusion
- Signed URLs for secure download (24-hour expiry)

### Data Deletion
- Soft deletion with configurable grace period
- PII anonymization (emails, phone numbers, etc.)
- OAuth token revocation
- Content anonymization
- Organization name anonymization

### Retention Policies
- Per-organization configuration
- Automatic cleanup of expired data
- Configurable retention periods (1-3650 days)
- Separate policies for messages, logs, and metrics

### Security & Compliance
- Owner-only access to privacy operations
- Confirmation required for destructive operations
- Audit logging of all privacy operations
- Grace periods for data deletion

## Usage

### Setting Up Retention Policies

```python
# Update retention policy via API
PUT /api/v1/privacy/retention
{
  "messages_days": 90,
  "logs_days": 30,
  "metrics_days": 365
}
```

### Requesting Data Export

```python
# Request data export
POST /api/v1/privacy/export
{
  "include_media": true,
  "format": "both"  # "json", "csv", or "both"
}
```

### Requesting Data Deletion

```python
# Request data deletion
POST /api/v1/privacy/delete
{
  "confirm_org_name": "Organization Name",
  "delete_media": false,
  "grace_period_days": 7
}
```

## Database Migration

Run the migration to create the required tables:

```bash
alembic upgrade head
```

This creates:
- `org_retention` table for retention policies
- `privacy_jobs` table for job tracking

## Running Workers

### Privacy Cleanup Worker
Runs nightly to enforce retention policies:

```bash
python workers/privacy_cleanup_worker.py
```

### Privacy Worker
Processes export/delete jobs (integrated with FastAPI background tasks).

## Testing

Run the test script to verify functionality:

```bash
python test_privacy.py
```

## Security Considerations

1. **Authentication Required**: All privacy endpoints require valid authentication
2. **Owner-Only Access**: Only organization owners can modify retention policies or request deletions
3. **Confirmation Required**: Data deletion requires organization name confirmation
4. **Grace Periods**: Deletions have configurable grace periods to prevent accidental data loss
5. **Audit Logging**: All privacy operations are logged for compliance

## Compliance Notes

- **GDPR Article 20**: Right to data portability (export functionality)
- **GDPR Article 17**: Right to erasure (deletion functionality)
- **GDPR Article 5**: Data minimization (retention policies)
- **GDPR Article 25**: Data protection by design (anonymization)

## Future Enhancements

1. **Real Storage Integration**: Replace placeholder URLs with actual S3/R2 integration
2. **Advanced Anonymization**: More sophisticated PII detection and anonymization
3. **Compliance Reporting**: Generate compliance reports for audits
4. **Data Subject Requests**: Handle individual data subject requests
5. **Cross-Border Transfers**: Track and manage international data transfers
