# Legal Automation System - API Documentation

## Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer {token}
```

### Logout
```http
POST /api/auth/logout
Authorization: Bearer {token}
```

## Document Management

### Create Document
```http
POST /api/documents
Authorization: Bearer {token}
Content-Type: application/json

{
    "title": "string",
    "content": "string",
    "metadata": {
        "type": "string",
        "jurisdiction": "string",
        "security_level": "string"
    }
}
```

### Get Document
```http
GET /api/documents/{id}
Authorization: Bearer {token}
```

### Update Document
```http
PUT /api/documents/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
    "content": "string",
    "metadata": {}
}
```

## Compliance API

### Check Compliance
```http
POST /api/compliance/check
Authorization: Bearer {token}
Content-Type: application/json

{
    "document_id": "string",
    "jurisdictions": ["US", "EU"],
    "regulations": ["GDPR", "CCPA"]
}
```

### Get Compliance Report
```http
GET /api/compliance/report/{document_id}
Authorization: Bearer {token}
```

## Error Responses

### Standard Error Format
```json
{
    "error": {
        "code": "string",
        "message": "string",
        "details": {}
    }
}
``` 