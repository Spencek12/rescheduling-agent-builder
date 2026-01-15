# HIPAA Compliance Documentation
## AI Rescheduling Agent - Standalone Edition

---

## Executive Summary

The AI Rescheduling Agent Standalone Edition is designed with HIPAA compliance as a core requirement. This document outlines the technical controls, architecture decisions, and operational procedures that support HIPAA compliance.

**Key Compliance Features:**
- ✅ Fully local execution (no cloud processing)
- ✅ Localhost-only binding (no external network exposure)
- ✅ No data transmission (except authorized API calls)
- ✅ No telemetry or analytics
- ✅ Audit logging capabilities
- ✅ Encryption at rest support
- ✅ No persistent storage of PHI (unless configured)

---

## Technical Controls

### 1. Network Security

**Localhost Binding:**
```python
app.run(host='127.0.0.1', ...)  # NEVER 0.0.0.0
```

- Application binds exclusively to `127.0.0.1` (localhost)
- Not accessible from network
- Not accessible from other machines
- Not accessible from internet
- Firewall bypass impossible

**Port Selection:**
- Dynamic port finding (5000-5010)
- Falls back if port in use
- No external port forwarding

### 2. Data Handling

**PHI Processing:**
- All processing happens in-memory
- No automatic persistent storage
- Data only saved when user explicitly exports
- Temporary files cleared on exit

**Data Flow:**
1. User uploads files → Processed in RAM
2. API calls made → Direct to Retell AI (encrypted HTTPS)
3. Results generated → Stored in RAM
4. User downloads results → Saved to user-chosen location
5. Application exits → All data cleared

### 3. API Communication

**Outbound Connections:**
- Only to Retell AI API (https://api.retellai.com)
- All connections over TLS 1.2+
- No other external connections
- No telemetry
- No analytics
- No update checks

**API Security:**
- Credentials stored in local config.env file
- Credentials never logged
- API keys transmitted only over HTTPS
- No credential caching outside memory

### 4. Access Controls

**Application Level:**
- Runs with user's OS permissions
- No elevation required
- No background services
- No system modifications

**File System:**
- Reads: User-selected files only
- Writes: User-specified export location only
- No hidden files created
- No registry modifications (Windows)
- No system preferences modified (macOS)

### 5. Audit & Logging

**What is Logged:**
- Application start/stop times
- Configuration loading (not values)
- API call counts (not content)
- Error messages (no PHI)

**What is NOT Logged:**
- Patient names
- Phone numbers
- Dates of birth
- Appointment details
- Any PHI

**Log Location:**
- Console output only (not persisted by default)
- User can redirect output if needed for audit
- Logs should be reviewed to ensure no PHI

### 6. Encryption

**At Rest:**
- Application does not store PHI persistently
- If user saves results, OS file encryption recommended:
  - Windows: BitLocker
  - macOS: FileVault
  - Linux: LUKS/dm-crypt

**In Transit:**
- All API communications over TLS 1.2+
- Certificate validation enforced
- No downgrade to HTTP

**In Memory:**
- Python's memory management
- No swap file protection (OS responsibility)
- Recommend: Encrypted swap on OS level

---

## HIPAA Requirements Mapping

### Administrative Safeguards

| Requirement | Implementation | Evidence |
|-------------|----------------|----------|
| Security Management Process | Document this file, SOPs for deployment | This document |
| Assigned Security Responsibility | IT/Security team manages deployment | Deployment docs |
| Workforce Training | Train users on proper use, config.env security | Training materials |
| Evaluation | Annual security review | Review schedule |

### Physical Safeguards

| Requirement | Implementation | Evidence |
|-------------|----------------|----------|
| Facility Access Controls | Application runs on user workstation | Covered by facility controls |
| Workstation Security | User must secure their workstation | User agreement |
| Device & Media Controls | User responsible for device encryption | Policy document |

### Technical Safeguards

| Requirement | Implementation | Evidence |
|-------------|----------------|----------|
| Access Control | Localhost-only binding | Source code: main.py line 85 |
| Audit Controls | Console logging available | Source code: main.py |
| Integrity | No data modification, read-only source files | File checksums |
| Transmission Security | TLS 1.2+ for all API calls | Source code: app.py |

---

## Deployment Checklist

### Pre-Deployment

- [ ] Review this compliance document
- [ ] Train staff on proper use
- [ ] Prepare config.env template
- [ ] Document who has access
- [ ] Define incident response plan

### Installation

- [ ] Copy executable to secure location
- [ ] Create config.env from template
- [ ] Secure config.env (file permissions)
- [ ] Test on non-PHI data first
- [ ] Verify localhost-only operation
- [ ] Document installation date and version

### Operational

- [ ] Ensure workstation is encrypted
- [ ] Ensure workstation has screen lock
- [ ] User trained on secure file handling
- [ ] Exported results handled securely
- [ ] No sharing of config.env
- [ ] Regular security updates to workstation

### Audit & Monitoring

- [ ] Periodic review of usage
- [ ] Review of any incidents
- [ ] Annual compliance assessment
- [ ] Update documentation as needed

---

## Risk Assessment

### Identified Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Unauthorized access to config.env | Medium | High | File permissions, encryption, training |
| PHI in exported files not secured | Medium | High | Training, policy, encryption |
| Screen left unlocked with PHI visible | Medium | Medium | Screen lock policy, timeout |
| Network misconfiguration | Low | High | Code review, localhost hardcoded |
| API credential exposure | Low | High | Config file security, no logging |
| Memory dump with PHI | Very Low | Medium | Encrypted swap, physical security |

### Residual Risks

After mitigations, residual risks are primarily operational (user behavior) rather than technical. Address through:
- Training
- Policies
- Monitoring
- Audits

---

## Incident Response

### Potential Incidents

**1. Config.env Exposure**
- Immediately revoke API credentials
- Generate new credentials
- Investigate how exposure occurred
- Update config.env on all installations
- Document incident

**2. Unauthorized Access to Exported Files**
- Identify what PHI was accessed
- Follow organizational breach notification procedures
- Secure remaining files
- Review access controls
- Document incident

**3. Application Runs on Unsecured Workstation**
- Immediately stop application
- Assess what PHI was processed
- Secure workstation
- Retrain user
- Document incident

### Response Team

Define roles:
- Security Officer: [Name/Role]
- Privacy Officer: [Name/Role]
- IT Lead: [Name/Role]
- Compliance: [Name/Role]

---

## Documentation Requirements

Maintain these documents:

1. **This File** - HIPAA_COMPLIANCE.md
   - Technical controls
   - Risk assessment
   - Updated annually

2. **Standard Operating Procedure (SOP)**
   - How to install
   - How to configure
   - How to use
   - How to securely export/destroy data

3. **Training Materials**
   - User training on secure use
   - Admin training on deployment
   - Record of who was trained and when

4. **Business Associate Agreements (BAA)**
   - With Retell AI (if processing PHI)
   - With any other third parties

5. **Incident Log**
   - Date, time, description
   - Response taken
   - Resolution
   - Lessons learned

---

## Third-Party Dependencies

### Retell AI

**Service:** Phone call API  
**Data Shared:** Patient names, phone numbers, appointment dates  
**Security:** HTTPS, their SOC 2/HIPAA status  
**BAA Required:** YES  

**Action Items:**
- [ ] Obtain BAA from Retell AI
- [ ] Verify their HIPAA compliance status
- [ ] Review their security practices
- [ ] Document data sharing agreement

### Python Libraries

All libraries are bundled in the executable:
- Flask: Web framework
- Pandas: Data processing
- Requests: HTTP client
- OpenPyXL: Excel reading

**No External Services:**
- No package repositories accessed at runtime
- No version checking
- No telemetry
- Fully offline capable

---

## Attestation

By deploying this application, you attest that:

- [ ] I have read and understand this compliance documentation
- [ ] I will implement the required safeguards
- [ ] I will train users appropriately
- [ ] I will maintain required documentation
- [ ] I will follow incident response procedures
- [ ] I accept responsibility for operational security

**Signature:** _____________________  
**Name:** _____________________  
**Title:** _____________________  
**Date:** _____________________  

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-08 | Initial compliance documentation | - |

---

## Contact

For questions about HIPAA compliance of this application:

**Security Questions:** [security@yourcompany.com]  
**Privacy Questions:** [privacy@yourcompany.com]  
**Technical Support:** [support@yourcompany.com]

---

## Appendix A: Code Security Review

Key security-relevant code sections:

**Localhost Binding (main.py:85)**
```python
app.run(
    host='127.0.0.1',  # CRITICAL: localhost only
    port=port,
    debug=False,
    ...
)
```

**No Telemetry (Entire Codebase)**
- No `requests.post` to analytics services
- No phone-home functionality
- No update checks
- Search codebase for: `requests.`, `http://`, `https://`
- Only matches: Retell AI API calls

**Configuration Loading (main.py:55)**
```python
# Loads from config.env
# Does not log values
# Does not transmit values
```

---

## Appendix B: Penetration Testing

Recommended penetration tests:

1. **Network Exposure Test**
   - Attempt to access from another machine
   - Should fail (connection refused)

2. **Port Scan Test**
   - Scan workstation while app running
   - Should not see open port from network

3. **API Credential Extraction Test**
   - Attempt to find credentials in memory/logs
   - Should not be in logs
   - Memory: OS-level protection

4. **Man-in-the-Middle Test**
   - Attempt to intercept API calls
   - Should fail (certificate pinning, TLS)

---

## Appendix C: Compliance Checklist

Complete this checklist annually:

**Technical Controls:**
- [ ] Verified localhost-only binding in code
- [ ] Verified no telemetry in code
- [ ] Verified TLS for API calls
- [ ] Verified no persistent PHI storage
- [ ] Verified logging contains no PHI
- [ ] Tested network isolation

**Administrative Controls:**
- [ ] All users trained this year
- [ ] Training documented
- [ ] SOPs updated
- [ ] Incident response plan tested
- [ ] BAAs current and on file

**Physical Controls:**
- [ ] Workstation encryption verified
- [ ] Physical security of workstations verified
- [ ] Screen lock policies enforced

**Audit:**
- [ ] Review of any incidents
- [ ] Risk assessment updated
- [ ] This document reviewed and updated
- [ ] Compliance officer signed off

**Date:** _____________________  
**Reviewer:** _____________________  
**Next Review Due:** _____________________  

---

*This document should be reviewed by legal counsel and compliance officers to ensure it meets your organization's specific HIPAA obligations.*