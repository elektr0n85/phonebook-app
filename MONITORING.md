# 📊 Monitoring & Maintenance Guide

Guide for monitoring, maintaining, and operating the Phonebook application in production.

---

## 📈 **Monitoring Strategy**

### **1. Application Metrics** 🎯

#### **Key Metrics to Track:**

**Performance:**
- Response time (p50, p95, p99)
- Requests per second
- Error rate (4xx, 5xx)
- Database query time

**Business:**
- User registrations (daily/weekly)
- Active users (DAU/MAU)
- API usage by endpoint
- Failed login attempts

**Infrastructure:**
- CPU usage
- Memory usage
- Disk space
- Network I/O

#### **Tools:**

**Option 1: Prometheus + Grafana** (Recommended)

Add to `docker-compose.monitoring.yml`:
```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

**Option 2: Datadog** (Cloud service)
```bash
# Install Datadog agent
DD_API_KEY=<your-key> DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
```

**Option 3: New Relic** (Cloud service)
```bash
pip install newrelic
newrelic-admin generate-config <license-key> newrelic.ini
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program uvicorn app.main:app
```

---

### **2. Error Tracking** 🐛

#### **Sentry Integration**

Install:
```bash
pip install sentry-sdk[fastapi]
```

Configure in `app/main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
    environment="production",
    integrations=[FastApiIntegration()]
)
```

Features:
- Real-time error alerts
- Stack traces
- User context
- Release tracking
- Performance monitoring

---

### **3. Logging** 📝

#### **Log Levels:**

```python
DEBUG   = Detailed diagnostic information
INFO    = General informational messages
WARNING = Warning messages, but application still works
ERROR   = Error messages, functionality impaired
CRITICAL = Critical errors, application may crash
```

#### **Structured Logging:**

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "user_logged_in",
    user_id=user.id,
    email=user.email,
    ip_address=request.client.host
)
```

#### **Log Aggregation:**

**Option 1: ELK Stack** (Elasticsearch, Logstash, Kibana)

Add to `docker-compose.monitoring.yml`:
```yaml
elasticsearch:
  image: elasticsearch:8.11.0
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false
  ports:
    - "9200:9200"

logstash:
  image: logstash:8.11.0
  volumes:
    - ./logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  ports:
    - "5000:5000"

kibana:
  image: kibana:8.11.0
  ports:
    - "5601:5601"
  environment:
    - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

**Option 2: Loki + Grafana**

```yaml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"
  command: -config.file=/etc/loki/local-config.yaml

promtail:
  image: grafana/promtail:latest
  volumes:
    - /var/log:/var/log
    - ./promtail-config.yml:/etc/promtail/config.yml
  command: -config.file=/etc/promtail/config.yml
```

---

### **4. Uptime Monitoring** ⏰

**Tools:**
- UptimeRobot (free tier available)
- Pingdom
- StatusCake
- AWS CloudWatch Synthetics

**Setup:**
1. Monitor: `https://yourdomain.com/health`
2. Frequency: Every 1-5 minutes
3. Alert on: 3 consecutive failures
4. Notification: Email, SMS, Slack

**Health Check Endpoint:**

Already implemented in `app/main.py`:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

---

## 🔔 **Alerting**

### **Alert Rules:**

**Critical (Page On-Call):**
- Application down (3+ consecutive failures)
- Database connection lost
- Disk space >90%
- Error rate >5%
- Memory usage >95%

**Warning (Email/Slack):**
- Error rate >1%
- Response time p95 >1s
- Failed login attempts >20 in 5 min
- Disk space >80%
- CPU usage >80% for 10 min

**Info:**
- Deployment completed
- Backup completed
- Certificate renewal

### **Notification Channels:**

```yaml
# AlertManager config
receivers:
  - name: 'team-pager'
    pagerduty_configs:
      - service_key: '<key>'
  
  - name: 'team-slack'
    slack_configs:
      - channel: '#alerts'
        api_url: '<webhook-url>'
  
  - name: 'team-email'
    email_configs:
      - to: 'team@example.com'
```

---

## 🔧 **Maintenance Tasks**

### **Daily** 🌅

```bash
#!/bin/bash
# daily_checks.sh

# Check application health
curl -f https://yourdomain.com/health || echo "ALERT: App down!"

# Check disk space
df -h | awk '$5 > 80 {print "WARNING: "$0}'

# Check recent errors
docker-compose logs --since=24h backend | grep ERROR

# Check database connections
docker-compose exec db psql -U phonebook_user -d phonebook_db -c "SELECT count(*) FROM pg_stat_activity;"
```

### **Weekly** 📅

```bash
#!/bin/bash
# weekly_maintenance.sh

# Update dependencies
cd backend && pip list --outdated
cd ../frontend && npm outdated

# Security scan
safety check
npm audit

# Restart services (if needed)
# docker-compose restart
```

### **Monthly** 🗓️

- [ ] Review logs for patterns
- [ ] Analyze performance metrics
- [ ] Check and optimize database queries
- [ ] Review and rotate access logs
- [ ] Update documentation
- [ ] Review security alerts
- [ ] Test backup restoration

### **Quarterly** 📆

- [ ] Dependency updates (major versions)
- [ ] Security audit
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Review and update runbooks
- [ ] Team security training

---

## 💾 **Backup & Recovery**

### **Backup Strategy (3-2-1 Rule)**

- **3** copies of data
- **2** different storage media
- **1** copy off-site

### **Automated Backups**

**Database Backup Script:**

```bash
#!/bin/bash
# backup_database.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="phonebook_db"
DB_USER="phonebook_user"

# Create backup
docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME | gzip > "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Encrypt backup (optional)
gpg --encrypt --recipient backups@yourdomain.com "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Upload to S3
aws s3 cp "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz.gpg" s3://your-bucket/backups/

# Remove old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

**Cron Schedule:**

```cron
# Daily backups at 2 AM
0 2 * * * /opt/scripts/backup_database.sh >> /var/log/backups.log 2>&1

# Weekly full backup (Sunday 3 AM)
0 3 * * 0 /opt/scripts/backup_full.sh >> /var/log/backups.log 2>&1
```

### **Restoration Procedure**

```bash
#!/bin/bash
# restore_database.sh

BACKUP_FILE=$1

# Decompress
gunzip $BACKUP_FILE

# Restore
docker-compose exec -T db psql -U phonebook_user phonebook_db < ${BACKUP_FILE%.gz}

echo "Database restored from $BACKUP_FILE"
```

**Test restoration monthly!**

---

## 🚀 **Performance Optimization**

### **Database Optimization**

```sql
-- Check slow queries
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Create indexes for common queries
CREATE INDEX idx_contacts_user_id ON contacts(user_id) WHERE is_deleted = false;
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_phones_number ON phones(phone_number);

-- Vacuum database (auto-vacuum should handle this)
VACUUM ANALYZE;
```

### **Application Optimization**

```python
# Use connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=100)
async def get_user_by_id(user_id: int):
    # ...
```

### **CDN for Static Assets**

Use Cloudflare or AWS CloudFront for:
- Frontend static files
- Images
- CSS/JS bundles

---

## 📱 **On-Call Runbook**

### **Common Issues & Solutions**

#### **1. Application Not Responding**

```bash
# Check if containers are running
docker-compose ps

# Check logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# If still down, check resources
docker stats

# Nuclear option: restart all
docker-compose down && docker-compose up -d
```

#### **2. High CPU Usage**

```bash
# Identify process
docker stats
htop

# Check for slow queries
# (See database optimization above)

# Scale horizontally (if configured)
docker-compose up -d --scale backend=3
```

#### **3. Database Connection Errors**

```bash
# Check database is running
docker-compose ps db

# Check connections
docker-compose exec db psql -U phonebook_user -c "SELECT count(*) FROM pg_stat_activity;"

# Restart database (last resort)
docker-compose restart db
```

#### **4. Out of Disk Space**

```bash
# Check space
df -h

# Clear Docker images/volumes
docker system prune -a

# Clear logs
truncate -s 0 /var/log/nginx/access.log
find /var/log -type f -name "*.log" -mtime +7 -delete

# Resize volume (cloud provider)
```

---

## 📞 **Escalation Procedures**

### **Severity Levels:**

**P0 - Critical (Page immediately)**
- Application completely down
- Data breach
- Database corruption

**P1 - High (Page during business hours)**
- Partial outage
- Degraded performance
- Failed backups

**P2 - Medium (Email alert)**
- Minor bugs
- Slow queries
- Non-critical errors

**P3 - Low (Ticket)**
- Feature requests
- Documentation updates
- Nice-to-have improvements

### **Contact List:**

```
Primary On-Call: +1-XXX-XXX-XXXX (John)
Secondary On-Call: +1-XXX-XXX-XXXX (Jane)
Engineering Manager: +1-XXX-XXX-XXXX (Bob)
Database Admin: +1-XXX-XXX-XXXX (Alice)

Email: oncall@yourdomain.com
Slack: #incidents
PagerDuty: https://yourorg.pagerduty.com
```

---

## ✅ **Monthly Review Checklist**

- [ ] Review metrics and trends
- [ ] Check error rates
- [ ] Review slow queries
- [ ] Test backup restoration
- [ ] Review and update documentation
- [ ] Check security alerts
- [ ] Review access logs
- [ ] Update dependencies
- [ ] Team retrospective

---

**Monitoring Guide Version**: 1.0.0  
**Last Updated**: 2026-01-20  
**Status**: Production Ready ✅
