# Agent Skill: Security & Risk Management

## Purpose
Identify security vulnerabilities, assess risks, implement protections, and maintain security posture: threat modeling, attack surface analysis, vulnerability scanning, and secure-by-design practices.

## When to Use
- "Use security-risk skill: Assess security vulnerabilities in..."
- "Use security-risk skill: Threat model this component"
- "Use security-risk skill: Identify attack vectors for..."
- "Use security-risk skill: Design for secure data handling"
- "Use security-risk skill: Risk assessment and mitigation"

## Typical Workflow

1. **Threat Modeling**
   - Identify assets (what needs protection?)
   - Identify threats (what could go wrong?)
   - Identify threat actors (who would attack?)
   - Identify attack vectors (how would they attack?)

2. **Vulnerability Assessment**
   - Scan for known vulnerabilities
   - Review for common security flaws
   - Test authentication/authorization
   - Check for injection vulnerabilities
   - Review sensitive data handling

3. **Risk Analysis**
   - Probability: How likely is this attack?
   - Impact: What's the damage if it happens?
   - Exploitability: How hard is it to execute?
   - Detectability: Would we notice it?
   - Severity score: (Probability × Impact × Exploitability)

4. **Mitigation Strategy**
   - Prevent: Can we block the attack?
   - Detect: Can we notice the attack?
   - Respond: Can we recover from it?
   - Plan implementation
   - Measure effectiveness

## Security Analysis Framework

### Assets to Protect
```
┌─────────────────────────────────┐
│  Racing Data (Scraped)          │ ← Confidentiality & Integrity
├─────────────────────────────────┤
│  Model Predictions              │ ← Availability & Integrity
├─────────────────────────────────┤
│  API Keys & Secrets             │ ← Confidentiality (CRITICAL)
├─────────────────────────────────┤
│  Database Credentials           │ ← Confidentiality (CRITICAL)
├─────────────────────────────────┤
│  User Data (if applicable)      │ ← Confidentiality & Privacy
└─────────────────────────────────┘
```

### Threat Model Template

```
Threat: API Key Leakage
├─ Threat Actor: Malicious developer or git history
├─ Attack Vector: Committing keys to git repository
├─ Impact: Unauthorized access to Racing.com API
├─ Probability: Medium (if not careful with secrets)
├─ Exploitability: Easy (keys in repo are obvious)
├─ Detection: Difficult (unauthorized use might not be noticed)
└─ Severity: CRITICAL

Mitigation:
├─ Prevent: Use environment variables, not hardcoded secrets
├─ Prevent: Add pre-commit hook to block secret patterns
├─ Detect: Scan git history for secrets
├─ Respond: Rotate API keys immediately if leaked
└─ Test: Try to commit key, verify it's blocked
```

## Code Patterns for Security

```python
# DON'T: Hardcode secrets
API_KEY = "da2-6nsi4ztsynar3l3frgxf77q5fe"  # WRONG!

# DO: Use environment variables
import os
API_KEY = os.environ.get('RACING_COM_API_KEY')
if not API_KEY:
    raise ValueError("RACING_COM_API_KEY not set in environment")

# DO: Use secrets management library
from dotenv import load_dotenv
load_dotenv()  # Load from .env (not in git!)
API_KEY = os.environ['RACING_COM_API_KEY']

# Security: Input validation
def validate_venue_name(venue: str) -> str:
    """Validate and sanitize venue name."""
    # Prevent injection attacks
    if not venue or not isinstance(venue, str):
        raise ValueError("Invalid venue")
    
    # Only allow alphanumeric + space
    if not all(c.isalnum() or c == ' ' for c in venue):
        raise ValueError("Invalid characters in venue")
    
    return venue.strip().lower()

# Security: Parameterized queries (DuckDB)
# DON'T: String concatenation
# query = f"SELECT * FROM races WHERE venue = '{venue}'"  # SQL injection!

# DO: Parameterized queries
query = "SELECT * FROM races WHERE venue = ?"
result = conn.execute(query, [venue]).fetchall()

# Security: Rate limiting to prevent abuse
from time import sleep

class RateLimitedScraper:
    def __init__(self, requests_per_second: float = 0.5):
        self.delay = 1.0 / requests_per_second
    
    def scrape(self, url):
        """Rate-limited request to prevent abuse."""
        sleep(self.delay)
        return requests.get(url)

# Security: Error handling (don't leak info)
# DON'T: Return full error details
# raise Exception(f"Database error: {db_error_details}")  # Leaks info!

# DO: Generic error, log full details
try:
    result = db.query(...)
except Exception as e:
    logger.error(f"Database error: {e}", exc_info=True)  # Log full details
    raise RuntimeError("Data retrieval failed")  # Generic error to user

# Security: Timeout protection
def safe_request(url, timeout_seconds=10):
    """Request with timeout to prevent hanging."""
    try:
        response = requests.get(url, timeout=timeout_seconds)
        return response
    except requests.Timeout:
        raise RuntimeError("Request timed out")

# Security: Data encryption at rest
from cryptography.fernet import Fernet

def encrypt_sensitive_data(data: str, key: bytes) -> str:
    """Encrypt sensitive data."""
    cipher = Fernet(key)
    return cipher.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted: str, key: bytes) -> str:
    """Decrypt sensitive data."""
    cipher = Fernet(key)
    return cipher.decrypt(encrypted.encode()).decode()
```

## Common Security Vulnerabilities to Check

### Secrets Management
- [ ] No hardcoded API keys, passwords, credentials
- [ ] Secrets loaded from environment variables
- [ ] .env file exists and is in .gitignore
- [ ] No secrets in git history
- [ ] Rotating keys documented

### Input Validation
- [ ] All user input validated
- [ ] SQL injection prevention (parameterized queries)
- [ ] Command injection prevention
- [ ] Path traversal prevention

### Authentication & Authorization
- [ ] API keys properly restricted in scope
- [ ] Access control enforced at module boundaries
- [ ] Audit logging for sensitive operations

### Data Protection
- [ ] Sensitive data encrypted at rest
- [ ] Secure transport (HTTPS/TLS)
- [ ] Sensitive data not logged
- [ ] Data retention policy documented

### Error Handling
- [ ] Generic errors to users (don't leak details)
- [ ] Full errors logged securely
- [ ] Stack traces not exposed

### Dependencies
- [ ] Regular dependency updates
- [ ] Vulnerability scanning (bandit, safety)
- [ ] Known vulnerable packages identified

### Network Security
- [ ] Rate limiting on APIs
- [ ] Timeouts on external requests
- [ ] DDoS protection considerations

## Threat Modeling Canvas

```
┌─────────────────────────────────────────────────────┐
│         Who Could Attack (Actors)?                  │
│ - Malicious developers                              │
│ - External attackers (if exposed)                   │
│ - Competitors                                       │
└─────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────┐
│      What Would They Target (Assets)?               │
│ - API Keys                                          │
│ - Model Predictions                                 │
│ - Racing Data                                       │
│ - Database Credentials                              │
└─────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────┐
│    How Would They Attack (Attack Vectors)?          │
│ - Git history (secrets)                             │
│ - Compromised dependencies                          │
│ - Network sniffing                                  │
│ - API rate limiting bypass                          │
└─────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────┐
│   What's the Impact (Severity)?                     │
│ - API key leakage: CRITICAL                         │
│ - Database compromise: CRITICAL                     │
│ - Prediction accuracy: MEDIUM                       │
└─────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────┐
│     How Do We Defend (Mitigations)?                 │
│ - Environment variables for secrets                 │
│ - Pre-commit hooks                                  │
│ - Dependency scanning                               │
│ - Rate limiting                                     │
└─────────────────────────────────────────────────────┘
```

## Risk Assessment Matrix

| Risk | Probability | Impact | Exploitability | Detection | Severity |
|------|-------------|--------|----------------|-----------|----------|
| API key leak | Medium | Critical | Easy | Hard | CRITICAL |
| SQL injection | Low | High | Medium | Easy | HIGH |
| Dependency vuln | Medium | Medium | Medium | Medium | MEDIUM |
| Rate limit bypass | Low | Medium | Hard | Easy | MEDIUM |
| Timeout attack | Low | Medium | Easy | Hard | LOW |

## Common Security Tasks

### Threat Model Component
- [ ] Identify assets this component accesses
- [ ] List potential threat actors
- [ ] Brainstorm attack vectors
- [ ] Estimate probability and impact
- [ ] Design mitigations
- [ ] Document decisions

### Security Audit Code
- [ ] Check for hardcoded secrets
- [ ] Review input validation
- [ ] Check query parameterization
- [ ] Verify error handling
- [ ] Review dependencies

### Design Secure Feature
- [ ] Threat model the feature
- [ ] Identify high-risk operations
- [ ] Implement security controls
- [ ] Add logging and monitoring
- [ ] Test security properties

### Respond to Vulnerability
- [ ] Assess impact
- [ ] Determine if exploited
- [ ] Implement fix
- [ ] Deploy fix
- [ ] Post-incident review

## Success Criteria
- ✅ Threats identified for all high-value assets
- ✅ Risk assessment completed
- ✅ High-severity risks have mitigations
- ✅ No hardcoded secrets
- ✅ Input validation comprehensive
- ✅ Error handling doesn't leak information
- ✅ Dependencies regularly scanned
- ✅ Security decisions documented
