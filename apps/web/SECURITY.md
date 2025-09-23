# Security Documentation

## Current Security Status

### ⚠️ Known Vulnerabilities

1. **JWT Token Storage**: Currently uses `localStorage` for JWT token storage, which is vulnerable to Cross-Site Scripting (XSS) attacks.
   - **Risk Level**: HIGH
   - **Location**: `apps/web/lib/auth.ts`
   - **Impact**: Malicious scripts can access authentication tokens

### 🔒 Implemented Mitigations

#### 1. Centralized Token Management
- All token access is now centralized in `apps/web/lib/auth.ts`
- Added input validation for token format
- Removed any token logging or exposure in error messages
- Added clear deprecation warnings

#### 2. Content Security Policy (CSP)
- **File**: `apps/web/lib/security.ts`
- **Implementation**: Next.js middleware (`apps/web/middleware.ts`)
- **Headers Applied**:
  - `Content-Security-Policy`: Restricts script sources
  - `X-Content-Type-Options: nosniff`: Prevents MIME type sniffing
  - `X-Frame-Options: DENY`: Prevents clickjacking
  - `X-XSS-Protection: 1; mode=block`: Enables XSS filtering
  - `Referrer-Policy: strict-origin-when-cross-origin`: Limits referrer information
  - `Permissions-Policy`: Restricts browser features

#### 3. Security Utilities
- **File**: `apps/web/lib/security.ts`
- **Features**:
  - Input sanitization for XSS prevention
  - JWT format validation
  - CSRF token generation
  - Security middleware for API routes

### 🚧 Migration Path to httpOnly Cookies

#### Phase 1: Backend Preparation (TODO)
1. **Create secure cookie endpoints**:
   - `POST /api/auth/login` - Set httpOnly, Secure, SameSite=Strict cookies
   - `POST /api/auth/logout` - Clear cookies
   - `GET /api/auth/session` - Return current session info
   - `POST /api/auth/refresh` - Refresh access token via httpOnly cookie

2. **Cookie Configuration**:
   ```typescript
   {
     httpOnly: true,
     secure: true,
     sameSite: 'strict',
     maxAge: 3600, // 1 hour for access token
     path: '/',
   }
   ```

#### Phase 2: Frontend Migration (TODO)
1. **Replace localStorage usage**:
   - Remove `getToken()`, `setToken()`, `removeToken()` from auth.ts
   - Update all API calls to use cookie-based authentication
   - Implement automatic cookie handling via fetch credentials

2. **Update API calls**:
   ```typescript
   // Before
   fetch('/api/data', {
     headers: {
       'Authorization': `Bearer ${getToken()}`
     }
   })
   
   // After
   fetch('/api/data', {
     credentials: 'include' // Automatically sends cookies
   })
   ```

#### Phase 3: Security Hardening (TODO)
1. **CSP Refinement**:
   - Remove `'unsafe-eval'` from script-src (requires Next.js nonce implementation)
   - Remove `'unsafe-inline'` from style-src
   - Add strict domain whitelisting

2. **Token Rotation**:
   - Implement refresh token rotation
   - Add token binding to user sessions
   - Implement logout from all devices

### 🛡️ Security Checklist

- [x] Centralized token management
- [x] Input validation
- [x] CSP headers
- [x] Security headers
- [x] XSS prevention utilities
- [ ] httpOnly cookie implementation
- [ ] Token rotation mechanism
- [ ] Rate limiting
- [ ] Session management
- [ ] Security audit

### 🚨 Immediate Actions Required

1. **Review all token usage** in the codebase
2. **Test CSP headers** in staging environment
3. **Plan httpOnly cookie migration** timeline
4. **Rotate existing tokens** after migration

### 📚 Security Resources

- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_Cheat_Sheet.html)
- [Next.js Security Headers](https://nextjs.org/docs/advanced-features/security-headers)
- [MDN CSP Documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [Web Security Best Practices](https://web.dev/secure/)
