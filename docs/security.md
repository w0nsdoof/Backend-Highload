# Security Measures

## Middleware
### SecurityHeadersMiddleware
- Enforces HTTPS.
- Adds headers:
  - `Strict-Transport-Security`: Forces HTTPS for one year.
  - `Content-Security-Policy`: Allows resources only from the same origin.
  - `X-Content-Type-Options`: Prevents MIME-sniffing.
  - `X-Frame-Options`: Disallows clickjacking attacks.
  - `X-XSS-Protection`: Enables XSS protection.

## Secure Endpoints
### `/api/auth/login/`
- Rate limiting: 5 requests per minute.
- Logs failed attempts.

### `/api/auth/register/`
- Enforces strong passwords.

### `/api/auth/reset_password/`
- Rate limiting: 2 requests per minute.
- Ensures tokens expire within a short period.

## Token Handling
- Uses `JWT` for authentication.
- Rotates tokens on login.
