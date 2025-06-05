# Reports API Reference

## Endpoints

### Create Report
- `POST /api/v1/reports/`
  - Request: `ReportCreate`
  - Response: `ReportResponse`

### List Reports
- `GET /api/v1/reports/`
  - Response: `List[ReportResponse]`

### Get Report by ID
- `GET /api/v1/reports/{report_id}`
  - Response: `ReportResponse`

### Update Report
- `PUT /api/v1/reports/{report_id}`
  - Request: `ReportUpdate`
  - Response: `ReportResponse`

### Delete Report
- `DELETE /api/v1/reports/{report_id}`
  - Response: `{"status": "success"}`

### Download Report File
- `GET /api/v1/reports/files/{report_id}/file`
  - Response: File stream

### Get File Metadata
- `GET /api/v1/reports/files/{report_id}/metadata`
  - Response: File metadata dict

### List Report Types
- `GET /api/v1/reports/types/`
  - Response: `List[ReportTypeResponse]`

### List Report Statuses
- `GET /api/v1/reports/statuses/`
  - Response: `List[ReportStatusResponse]`

### Report Versions
- `GET /api/v1/reports/{report_id}/versions`
  - Response: `List[ReportVersionResponse]`

### Report Insights
- `GET /api/v1/reports/insights/{report_id}/insights`
  - Response: `List[ReportInsightResponse]`
- `POST /api/v1/reports/insights/{report_id}/insights/generate`
  - Triggers insight generation

### Report Q&A
- `POST /api/v1/reports/{report_id}/query`
  - Request: `{ "question": "..." }`
  - Response: `{ "answer": "..." }`

### Report Shares
- `POST /api/v1/reports/{report_id}/share`
  - Request: `{ "shared_with": "user_id", "permission": "read|write|admin", "expires_at": "..." }`
  - Response: `ReportShareResponse`
- `GET /api/v1/reports/{report_id}/shares`
  - Response: `List[ReportShareResponse]`

# Voice & Audio API Reference

## Endpoints

### Voice Profile
- `GET /api/v1/voice/profile` — Get current user's voice profile
- `POST /api/v1/voice/profile` — Create a new voice profile
- `PUT /api/v1/voice/profile/{profile_id}` — Update a voice profile
- `DELETE /api/v1/voice/profile/{profile_id}` — Delete a voice profile

### Voice Command
- `POST /api/v1/voice/command` — Submit a voice command
- `GET /api/v1/voice/command-history` — List user's voice command history

## Schemas
- See `backend/app/schemas/report.py` for all request/response models.
- See `backend/app/schemas/voice_profile.py` and `backend/app/schemas/voice.py` for request/response models.

## Usage Examples
```json
{
  "title": "Q1 Financial Report",
  "description": "Quarterly results",
  "report_type_id": "...",
  "metadata": {"department": "Finance"}
}
```

# Insights & Q&A API Reference

## Endpoints

### Report Insights
- `GET /api/v1/reports/{report_id}/insights` — List insights for a report
- `POST /api/v1/reports/{report_id}/insights` — Create a new insight for a report
- `PUT /api/v1/reports/insights/{insight_id}` — Update an insight
- `DELETE /api/v1/reports/insights/{insight_id}` — Delete an insight

### Report Q&A
- `POST /api/v1/reports/{report_id}/query` — Ask a contextual question about a report and get an answer

## Schemas
- See `backend/app/schemas/insight.py` for request/response models.

# BI Integration API Reference

## Endpoints

### BI Connections
- `GET /api/v1/bi/connections` — List BI tool connections for the user
- `POST /api/v1/bi/connect` — Create a new BI tool connection

### (Planned) Dashboards/Reports/Sync
- `GET /api/v1/bi/dashboards` — List dashboards (stub)
- `GET /api/v1/bi/reports` — List reports (stub)
- `POST /api/v1/bi/sync` — Trigger sync job (stub)

## Schemas
- See `backend/app/schemas/bi.py` for request/response models.

# Notifications API Reference

## Endpoints

### Notifications
- `GET /api/v1/notifications/` — List notifications for the user
- `POST /api/v1/notifications/` — Create a new notification
- `POST /api/v1/notifications/{notification_id}/read` — Mark a notification as read

### Notification Preferences
- `GET /api/v1/notifications/preferences` — Get notification preferences
- `PUT /api/v1/notifications/preferences` — Update a notification preference

## Schemas
- See `backend/app/schemas/notification.py` for request/response models.

# Audit & Analytics API Reference

## Endpoints

### Audit Logs
- `GET /api/v1/audit/logs` — List audit logs

### User Activity
- `GET /api/v1/audit/user-activity` — List user activity logs for the current user

### System Metrics
- `GET /api/v1/audit/system-metrics` — List system metrics

### Error Logs
- `GET /api/v1/audit/error-logs` — List error logs

## Schemas
- See `backend/app/schemas/audit.py` for response models.

# File Management API Reference

## Endpoints

### Files
- `GET /api/v1/files/` — List files for the user
- `POST /api/v1/files/upload` — Upload a new file (metadata + file upload)

## Schemas
- See `backend/app/schemas/file.py` for request/response models.

# Collaboration API Reference

## Endpoints

### Comments
- `GET /api/v1/comments/report/{report_id}` — List comments for a report
- `POST /api/v1/comments/report/{report_id}` — Create a comment for a report

### Tags
- `GET /api/v1/comments/tags` — List tags
- `POST /api/v1/comments/tags` — Create a tag

## Schemas
- See `backend/app/schemas/comment.py` for request/response models.

# Offline/Processing API Reference

## Endpoints

### Offline Content
- `GET /api/v1/offline/content` — List offline content for the user

### Sync Queue
- `GET /api/v1/offline/sync-queue` — List sync queue jobs

### Processing Jobs
- `GET /api/v1/offline/processing-jobs` — List processing jobs

## Schemas
- See `backend/app/schemas/offline.py` for response models.

---

*This section will be updated as new endpoints and features are added.* 