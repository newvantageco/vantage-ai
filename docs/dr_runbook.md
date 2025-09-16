# Disaster Recovery Runbook

This document outlines the procedures for disaster recovery scenarios in Vantage AI, including database restoration, region failover, and key rotation.

## Table of Contents

1. [Overview](#overview)
2. [Emergency Contacts](#emergency-contacts)
3. [Database Restoration](#database-restoration)
4. [Region Failover](#region-failover)
5. [Key Rotation](#key-rotation)
6. [Service Recovery](#service-recovery)
7. [Post-Incident Procedures](#post-incident-procedures)
8. [Testing and Validation](#testing-and-validation)

## Overview

Vantage AI is designed with high availability and disaster recovery in mind. This runbook provides step-by-step procedures for common disaster recovery scenarios.

### Recovery Time Objectives (RTO)
- **Database**: 15 minutes
- **API Services**: 5 minutes
- **Web Application**: 10 minutes
- **Worker Services**: 10 minutes

### Recovery Point Objectives (RPO)
- **Database**: 5 minutes (continuous backup)
- **Application State**: 1 hour (Redis persistence)

## Emergency Contacts

| Role | Name | Contact | Escalation |
|------|------|---------|------------|
| On-Call Engineer | Primary | +1-XXX-XXX-XXXX | 15 min |
| On-Call Engineer | Secondary | +1-XXX-XXX-XXXX | 30 min |
| Engineering Manager | | +1-XXX-XXX-XXXX | 1 hour |
| CTO | | +1-XXX-XXX-XXXX | 2 hours |

## Database Restoration

### Prerequisites

- Access to backup storage (S3/GCS)
- Database credentials for target environment
- Sufficient disk space for restoration
- Network connectivity to database

### Automated Restoration

```bash
# Run the automated restore script
./infra/restore_from_backup.sh \
  --backup-file "backup-2024-01-15-10-30-00.sql" \
  --target-db "vantage_ai_prod" \
  --dry-run false
```

### Manual Restoration Steps

1. **Stop Application Services**
   ```bash
   # Stop all services to prevent data corruption
   kubectl scale deployment vantage-api --replicas=0
   kubectl scale deployment vantage-worker --replicas=0
   kubectl scale deployment vantage-scheduler --replicas=0
   ```

2. **Download Backup**
   ```bash
   # Download the latest backup
   aws s3 cp s3://vantage-ai-backups/prod/backup-2024-01-15-10-30-00.sql ./backup.sql
   ```

3. **Restore Database**
   ```bash
   # Restore the database
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME < backup.sql
   ```

4. **Verify Restoration**
   ```bash
   # Check database integrity
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM organizations;"
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM schedules;"
   ```

5. **Restart Services**
   ```bash
   # Restart all services
   kubectl scale deployment vantage-api --replicas=3
   kubectl scale deployment vantage-worker --replicas=2
   kubectl scale deployment vantage-scheduler --replicas=1
   ```

### Point-in-Time Recovery

For point-in-time recovery using WAL files:

```bash
# Stop the database
sudo systemctl stop postgresql

# Restore base backup
pg_basebackup -D /var/lib/postgresql/data -Ft -z -P -U replicator

# Restore WAL files up to target time
pg_receivewal -D /var/lib/postgresql/wal_archive --until="2024-01-15 10:30:00"

# Start database
sudo systemctl start postgresql
```

## Region Failover

### Prerequisites

- Multi-region deployment configured
- DNS management access
- Load balancer configuration
- Database replication setup

### Automated Failover

```bash
# Run the automated failover script
./infra/failover_to_region.sh \
  --target-region "us-west-2" \
  --reason "us-east-1 outage" \
  --dry-run false
```

### Manual Failover Steps

1. **Assess Situation**
   ```bash
   # Check current region status
   kubectl get nodes -o wide
   kubectl get pods --all-namespaces
   ```

2. **Update DNS**
   ```bash
   # Update DNS to point to backup region
   aws route53 change-resource-record-sets \
     --hosted-zone-id Z123456789 \
     --change-batch file://dns-change.json
   ```

3. **Scale Up Backup Region**
   ```bash
   # Scale up services in backup region
   kubectl config use-context us-west-2
   kubectl scale deployment vantage-api --replicas=5
   kubectl scale deployment vantage-worker --replicas=3
   ```

4. **Verify Services**
   ```bash
   # Check service health
   curl -f https://api-backup.vantage-ai.com/health
   curl -f https://app-backup.vantage-ai.com/health
   ```

5. **Update Monitoring**
   ```bash
   # Update monitoring alerts to new region
   kubectl apply -f monitoring/backup-region-alerts.yaml
   ```

### Database Failover

1. **Promote Read Replica**
   ```bash
   # Promote read replica to primary
   aws rds promote-read-replica \
     --db-instance-identifier vantage-ai-prod-replica
   ```

2. **Update Connection Strings**
   ```bash
   # Update application configuration
   kubectl set env deployment/vantage-api \
     DATABASE_URL="postgresql://user:pass@new-primary:5432/vantage_ai"
   ```

3. **Verify Database**
   ```bash
   # Test database connectivity
   psql -h new-primary -U $DB_USER -d $DB_NAME -c "SELECT 1;"
   ```

## Key Rotation

### Prerequisites

- Access to secret management system
- Database access for token re-encryption
- Application restart capability

### Automated Key Rotation

```bash
# Run the automated key rotation script
python scripts/rotate_secrets.py \
  --new-key "$NEW_SECRET_KEY" \
  --dry-run false
```

### Manual Key Rotation Steps

1. **Generate New Key**
   ```bash
   # Generate new encryption key
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

2. **Update Environment**
   ```bash
   # Update secret in environment
   export SECRET_KEY_VERSION=2
   export SECRET_KEY="$NEW_SECRET_KEY"
   ```

3. **Rotate Secrets**
   ```bash
   # Run secret rotation script
   python scripts/rotate_secrets.py \
     --new-key "$NEW_SECRET_KEY" \
     --verify
   ```

4. **Restart Services**
   ```bash
   # Restart all services to pick up new key
   kubectl rollout restart deployment/vantage-api
   kubectl rollout restart deployment/vantage-worker
   kubectl rollout restart deployment/vantage-scheduler
   ```

5. **Verify Rotation**
   ```bash
   # Verify all secrets can be decrypted
   python scripts/rotate_secrets.py \
     --new-key "$NEW_SECRET_KEY" \
     --verify
   ```

## Service Recovery

### API Service Recovery

1. **Check Service Status**
   ```bash
   kubectl get pods -l app=vantage-api
   kubectl logs -l app=vantage-api --tail=100
   ```

2. **Restart if Needed**
   ```bash
   kubectl rollout restart deployment/vantage-api
   kubectl rollout status deployment/vantage-api
   ```

3. **Verify Health**
   ```bash
   curl -f https://api.vantage-ai.com/health
   curl -f https://api.vantage-ai.com/ready
   ```

### Worker Service Recovery

1. **Check Worker Status**
   ```bash
   kubectl get pods -l app=vantage-worker
   kubectl logs -l app=vantage-worker --tail=100
   ```

2. **Restart Workers**
   ```bash
   kubectl rollout restart deployment/vantage-worker
   kubectl rollout status deployment/vantage-worker
   ```

3. **Check Queue Status**
   ```bash
   # Check Redis queue status
   redis-cli -h $REDIS_HOST llen "scheduler:queue"
   redis-cli -h $REDIS_HOST llen "worker:queue"
   ```

### Scheduler Service Recovery

1. **Check Scheduler Status**
   ```bash
   kubectl get pods -l app=vantage-scheduler
   kubectl logs -l app=vantage-scheduler --tail=100
   ```

2. **Restart Scheduler**
   ```bash
   kubectl rollout restart deployment/vantage-scheduler
   kubectl rollout status deployment/vantage-scheduler
   ```

3. **Verify Scheduling**
   ```bash
   # Check if schedules are being processed
   psql -h $DB_HOST -U $DB_USER -d $DB_NAME \
     -c "SELECT COUNT(*) FROM schedules WHERE status = 'scheduled';"
   ```

## Post-Incident Procedures

### Immediate Actions (0-15 minutes)

1. **Document Incident**
   - Record start time
   - Note affected services
   - Document initial symptoms

2. **Notify Stakeholders**
   - Send incident notification
   - Update status page
   - Notify on-call team

3. **Begin Recovery**
   - Follow appropriate recovery procedure
   - Monitor recovery progress
   - Document all actions taken

### Short-term Actions (15-60 minutes)

1. **Verify Recovery**
   - Test all critical functions
   - Verify data integrity
   - Check service health

2. **Communicate Status**
   - Update stakeholders
   - Post status updates
   - Provide ETA for full recovery

3. **Monitor Systems**
   - Watch for recurring issues
   - Monitor performance metrics
   - Check error rates

### Long-term Actions (1-24 hours)

1. **Root Cause Analysis**
   - Investigate root cause
   - Document findings
   - Identify contributing factors

2. **Implement Fixes**
   - Deploy permanent fixes
   - Update monitoring
   - Improve procedures

3. **Post-Mortem**
   - Schedule post-mortem meeting
   - Document lessons learned
   - Update runbook

## Testing and Validation

### Monthly DR Tests

1. **Database Restore Test**
   ```bash
   # Test database restoration
   ./infra/restore_from_backup.sh \
     --backup-file "test-backup.sql" \
     --target-db "vantage_ai_test" \
     --dry-run true
   ```

2. **Region Failover Test**
   ```bash
   # Test region failover
   ./infra/failover_to_region.sh \
     --target-region "us-west-2" \
     --reason "monthly test" \
     --dry-run true
   ```

3. **Key Rotation Test**
   ```bash
   # Test key rotation
   python scripts/rotate_secrets.py \
     --new-key "$TEST_KEY" \
     --dry-run true
   ```

### Quarterly Full DR Test

1. **Simulate Complete Outage**
   - Shut down primary region
   - Test full failover
   - Verify all services

2. **Test Data Recovery**
   - Restore from backup
   - Verify data integrity
   - Test application functionality

3. **Test Communication**
   - Test incident notification
   - Verify status page updates
   - Test stakeholder communication

## Monitoring and Alerting

### Key Metrics to Monitor

- Database connection count
- API response times
- Worker queue depth
- Scheduler lag
- Error rates
- Memory usage
- CPU usage

### Alert Thresholds

- Database connections > 80% of max
- API response time > 2 seconds
- Worker queue depth > 1000
- Scheduler lag > 5 minutes
- Error rate > 5%
- Memory usage > 90%
- CPU usage > 90%

### Escalation Procedures

1. **Level 1**: Automated alerts
2. **Level 2**: On-call engineer notification
3. **Level 3**: Engineering manager escalation
4. **Level 4**: CTO escalation

## Backup and Recovery

### Backup Schedule

- **Database**: Every 6 hours
- **Configuration**: Daily
- **Application State**: Every 4 hours
- **Logs**: Daily (retained for 30 days)

### Backup Retention

- **Daily backups**: 30 days
- **Weekly backups**: 12 weeks
- **Monthly backups**: 12 months
- **Yearly backups**: 7 years

### Backup Verification

- **Daily**: Automated restore test
- **Weekly**: Full restore test
- **Monthly**: Cross-region restore test

## Security Considerations

### Access Control

- Limit DR access to essential personnel
- Use multi-factor authentication
- Log all DR activities
- Regular access reviews

### Data Protection

- Encrypt all backups
- Secure backup storage
- Regular security audits
- Compliance monitoring

### Incident Response

- Follow security incident procedures
- Notify security team
- Document security implications
- Post-incident security review

## Appendices

### A. Environment Variables

```bash
# Database
DATABASE_URL="postgresql://user:pass@host:5432/vantage_ai"
DB_HOST="vantage-ai-prod.cluster-xyz.us-east-1.rds.amazonaws.com"
DB_USER="vantage_ai"
DB_NAME="vantage_ai"

# Redis
REDIS_URL="redis://vantage-ai-redis:6379"
REDIS_HOST="vantage-ai-redis"

# Secrets
SECRET_KEY="your-secret-key"
SECRET_KEY_VERSION="1"

# Monitoring
GRAFANA_URL="https://grafana.vantage-ai.com"
PROMETHEUS_URL="https://prometheus.vantage-ai.com"
```

### B. Useful Commands

```bash
# Check service status
kubectl get pods --all-namespaces
kubectl get services --all-namespaces
kubectl get ingress --all-namespaces

# Check logs
kubectl logs -l app=vantage-api --tail=100
kubectl logs -l app=vantage-worker --tail=100

# Check database
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT version();"
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) FROM organizations;"

# Check Redis
redis-cli -h $REDIS_HOST ping
redis-cli -h $REDIS_HOST info memory
```

### C. Contact Information

- **Slack**: #incidents
- **PagerDuty**: vantage-ai-oncall
- **Status Page**: https://status.vantage-ai.com
- **Documentation**: https://docs.vantage-ai.com

---

**Last Updated**: 2024-01-15
**Version**: 1.0
**Next Review**: 2024-02-15
