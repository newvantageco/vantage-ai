# Authentication

VANTAGE AI uses JWT (JSON Web Tokens) for authentication. This guide explains how to authenticate with the API.

## Authentication Methods

### 1. JWT Token Authentication

The primary authentication method is JWT tokens. Include the token in the `Authorization` header:

```http
Authorization: Bearer <your_jwt_token>
```

### 2. API Key Authentication

For programmatic access, you can use API keys:

```http
Authorization: ApiKey <your_api_key>
```

## Getting Started

### 1. Register a User

First, register a new user account:

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "John Doe"
}
```

### 2. Login

Login to get a JWT token:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "org_id": "org_456"
  }
}
```

### 3. Use the Token

Include the token in subsequent requests:

```http
GET /api/v1/posts
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Keys

### Creating an API Key

Create an API key for programmatic access:

```http
POST /api/v1/api-keys
Authorization: Bearer <your_jwt_token>
Content-Type: application/json

{
  "name": "My API Key",
  "description": "API key for my application",
  "permissions": ["read:posts", "write:posts"]
}
```

Response:
```json
{
  "id": "key_123",
  "name": "My API Key",
  "key": "vantage_1234567890abcdef",
  "permissions": ["read:posts", "write:posts"],
  "created_at": "2024-01-15T10:00:00Z",
  "expires_at": "2025-01-15T10:00:00Z"
}
```

### Using API Keys

Use the API key in the Authorization header:

```http
GET /api/v1/posts
Authorization: ApiKey vantage_1234567890abcdef
```

## Token Refresh

JWT tokens expire after a certain period. Refresh your token:

```http
POST /api/v1/auth/refresh
Authorization: Bearer <your_current_token>
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Error Handling

### Invalid Token

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Could not validate credentials",
  "error": "invalid_token"
}
```

### Expired Token

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Token has expired",
  "error": "token_expired"
}
```

### Insufficient Permissions

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "detail": "Insufficient permissions",
  "error": "insufficient_permissions"
}
```

## Rate Limiting

API requests are rate limited per user/organization:

- **Free Plan**: 100 requests per hour
- **Growth Plan**: 1,000 requests per hour
- **Pro Plan**: 10,000 requests per hour

Rate limit headers are included in responses:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## Security Best Practices

### 1. Store Tokens Securely

- Never store tokens in plain text
- Use secure storage mechanisms
- Implement token rotation

### 2. Use HTTPS

Always use HTTPS in production to protect tokens in transit.

### 3. Implement Token Refresh

Implement automatic token refresh to maintain seamless access.

### 4. Monitor API Usage

Monitor your API usage to stay within rate limits.

## SDK Examples

### Python

```python
import requests

# Login
response = requests.post('https://api.vantageai.com/api/v1/auth/login', json={
    'email': 'user@example.com',
    'password': 'secure_password'
})

token = response.json()['access_token']

# Make authenticated requests
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('https://api.vantageai.com/api/v1/posts', headers=headers)
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('https://api.vantageai.com/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'secure_password'
  })
});

const { access_token } = await loginResponse.json();

// Make authenticated requests
const response = await fetch('https://api.vantageai.com/api/v1/posts', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

### cURL

```bash
# Login
curl -X POST https://api.vantageai.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure_password"}'

# Use token
curl -H "Authorization: Bearer <your_token>" \
  https://api.vantageai.com/api/v1/posts
```

## Troubleshooting

### Common Issues

#### Token Not Working
- Check if the token is correctly formatted
- Verify the token hasn't expired
- Ensure you're using the correct header format

#### Rate Limit Exceeded
- Check your current usage
- Wait for the rate limit to reset
- Consider upgrading your plan

#### Permission Denied
- Verify your API key has the required permissions
- Check if your organization has the necessary plan

### Getting Help

If you need help with authentication:

1. Check the [API Reference](/docs/api-reference/endpoints)
2. Search [GitHub Issues](https://github.com/vantage-ai/vantage-ai/issues)
3. Join our [Discord Community](https://discord.gg/vantage-ai)
4. Contact [Support](https://support.vantageai.com)
