# AI Rescheduling Agent - Standalone Deployment Guide

## 🎯 Overview

This guide explains how to build and distribute the AI Rescheduling Agent as standalone executables that require **zero installation** and run **fully local** for HIPAA compliance.

---

## 📋 What You Get

### Windows
- **File:** `AI_Rescheduling_Agent.exe`
- **Size:** ~50-80 MB
- **Requirements:** None - fully standalone
- **Distribution:** Single .exe file

### macOS
- **File:** `AI_Rescheduling_Agent.app`
- **Size:** ~50-80 MB
- **Requirements:** macOS 10.13+
- **Distribution:** Single .app bundle

### Linux
- **File:** `AI_Rescheduling_Agent` (binary)
- **Size:** ~50-80 MB
- **Requirements:** None - fully standalone
- **Distribution:** Single binary file

---

## 🔨 Building the Executables

### Prerequisites for Building

You need to build on each target platform:
- **Windows executable** → Build on Windows machine
- **macOS app** → Build on Mac
- **Linux binary** → Build on Linux

**Required for building:**
- Python 3.8 or higher
- Your existing app files (app.py, templates/, static/)

### Step 1: Prepare Your Project

Your project structure should look like:

```
AI-Rescheduling-Agent/
├── main.py                    (new - entry point)
├── app.py                     (your existing Flask app)
├── requirements.txt           (your existing requirements)
├── templates/
│   └── index.html            (your existing HTML)
├── static/
│   └── style.css             (your existing CSS)
├── build_windows.spec         (new - Windows config)
├── build_mac.spec             (new - macOS config)
├── build.bat                  (new - Windows build script)
├── build.sh                   (new - Mac/Linux build script)
└── config.env.template        (new - config template)
```

### Step 2: Build on Each Platform

**On Windows:**
```batch
# Open Command Prompt in project folder
build.bat

# Output: dist\AI_Rescheduling_Agent.exe
```

**On macOS:**
```bash
# Open Terminal in project folder
chmod +x build.sh
./build.sh

# Output: dist/AI_Rescheduling_Agent.app
```

**On Linux:**
```bash
# Open Terminal in project folder
chmod +x build.sh
./build.sh

# Output: dist/AI_Rescheduling_Agent
```

### Step 3: Test the Build

Before distributing, test the executable:

1. Create a `config.env` file:
   ```
   RETELL_API_KEY=your_test_key
   RETELL_AGENT_ID=your_test_agent
   FROM_NUMBER=+15551234567
   ```

2. Place config.env next to the executable

3. Run the executable:
   - **Windows:** Double-click `AI_Rescheduling_Agent.exe`
   - **macOS:** Double-click `AI_Rescheduling_Agent.app`
   - **Linux:** `./AI_Rescheduling_Agent`

4. Browser should open to `http://127.0.0.1:5000`

5. Test with sample data files

---

## 📦 Distribution Package

### What to Distribute

For each platform, create a distribution folder:

```
AI_Rescheduling_Agent_v1.0_Windows/
├── AI_Rescheduling_Agent.exe
├── config.env.template
├── README.txt
└── HIPAA_COMPLIANCE.pdf
```

### Distribution Methods

**1. ZIP File (Recommended)**
- Compress the folder
- Share via secure file transfer
- Users extract and run

**2. Network Share**
- Place on internal network drive
- Users copy to their machines
- IT can manage centrally

**3. USB Drive**
- Copy folder to USB
- Distribute physically
- Good for high-security environments

**4. Software Distribution (Enterprise)**
- Use SCCM (Windows)
- Use Jamf (macOS)
- Use Ansible/Puppet (Linux)

---

## 👤 End User Instructions

Create a simple `README.txt` for users:

```
AI RESCHEDULING AGENT - QUICK START
===================================

1. SETUP (One-time)
   - Copy this folder to your computer
   - Open config.env.template with Notepad/TextEdit
   - Fill in your API credentials
   - Save as "config.env" (remove .template)

2. RUN
   - Windows: Double-click AI_Rescheduling_Agent.exe
   - Mac: Double-click AI_Rescheduling_Agent.app
   - Linux: Run ./AI_Rescheduling_Agent

3. USE
   - Browser will open automatically
   - Upload your data files
   - Start calling
   - Download results when done
   - Close the window to stop

SECURITY NOTES:
- All data stays on your computer
- No internet access except API calls
- Keep config.env secure
- Don't share config.env

SUPPORT:
Email: support@yourcompany.com
Phone: 1-800-XXX-XXXX
```

---

## 🔒 HIPAA Compliance Checklist

Before distributing:

**Technical:**
- [ ] Built from source with localhost binding verified
- [ ] No telemetry in code
- [ ] No persistent storage unless user exports
- [ ] TLS verification for API calls
- [ ] Logging contains no PHI

**Documentation:**
- [ ] HIPAA_COMPLIANCE.md reviewed
- [ ] SOPs created
- [ ] Training materials prepared
- [ ] Incident response plan documented

**Agreements:**
- [ ] BAA signed with Retell AI
- [ ] User agreements prepared
- [ ] Security policies documented

**Deployment:**
- [ ] IT team briefed
- [ ] Security team approved
- [ ] Compliance officer signed off
- [ ] Users trained

---

## 🚀 Deployment Scenarios

### Scenario 1: Small Clinic (5-10 users)

**Approach:** Direct distribution
- Build executable once
- Create config.env with clinic credentials
- Email ZIP file to users
- Schedule 15-minute training call

**Pros:** Fast, simple
**Cons:** Manual credential management

### Scenario 2: Hospital System (100+ users)

**Approach:** Centralized deployment
- Build executable
- Publish to network share
- Use group policy to deploy (Windows)
- Create user-specific config.env per workstation
- Automate with scripts

**Pros:** Centralized control, audit trail
**Cons:** More setup complexity

### Scenario 3: Multi-Site Organization

**Approach:** Site-by-site rollout
- Build executable
- Train site IT leads
- They distribute to local users
- Central support team available

**Pros:** Scalable, localized support
**Cons:** Requires site coordination

---

## 🔧 Troubleshooting

### Build Issues

**"Python not found"**
- Install Python 3.8+ from python.org
- Add to PATH during installation

**"Module not found" during build**
- Run: `pip install -r requirements.txt`
- Then rebuild

**Build succeeds but exe doesn't run**
- Test on clean machine (no Python installed)
- Check antivirus didn't quarantine
- Run from Command Prompt to see errors

### Runtime Issues

**"Config file not found"**
- Ensure config.env is next to executable
- Check filename (not config.env.txt)
- Check file permissions

**"Port already in use"**
- Another instance running
- Close other instances
- App will try ports 5000-5010

**Browser doesn't open**
- Manually open: http://127.0.0.1:5000
- Check default browser setting
- Check firewall not blocking localhost

**Can't access from another computer**
- This is CORRECT behavior (HIPAA)
- App only runs on localhost
- Not accessible from network

---

## 📊 Version Management

### Versioning Strategy

Use semantic versioning: `MAJOR.MINOR.PATCH`

**Example:** v1.2.3
- 1 = Major version (breaking changes)
- 2 = Minor version (new features)
- 3 = Patch (bug fixes)

### Update Distribution

**For Updates:**
1. Build new version
2. Test thoroughly
3. Update version in filename: `AI_Rescheduling_Agent_v1.2.0.exe`
4. Distribute new version
5. Users replace old exe with new exe
6. config.env stays the same

**Migration Guide:**
```
Updating from v1.0 to v1.1
1. Close current application
2. Download new v1.1 executable
3. Replace old executable
4. Keep existing config.env
5. Run new version
6. Verify functionality
```

---

## 🔐 Security Best Practices

### For Developers

1. **Code Signing** (Recommended)
   - Sign executables with code signing certificate
   - Prevents tampering
   - Reduces antivirus false positives
   - Builds user trust

2. **Checksum Distribution**
   - Provide SHA256 hash of executable
   - Users can verify download integrity
   - Example: `sha256sum AI_Rescheduling_Agent.exe`

3. **Secure Build Environment**
   - Build on clean, secure machine
   - No malware or compromise
   - Document build environment
   - Use reproducible builds if possible

### For IT Teams

1. **Whitelisting**
   - Add to antivirus whitelist
   - Add to application whitelist
   - Document approval

2. **Deployment Testing**
   - Test on non-production data first
   - Verify network isolation
   - Test backup/restore procedures

3. **User Access**
   - Define who can use the app
   - Control distribution
   - Track installations

### For End Users

1. **Credential Security**
   - Never share config.env
   - Store in encrypted folder
   - Delete if leaving organization

2. **Data Handling**
   - Use encrypted drive
   - Don't email PHI results
   - Use secure file transfer
   - Delete files when done

3. **Workstation Security**
   - Keep OS updated
   - Use screen lock
   - Enable disk encryption
   - Use antivirus

---

## 📈 Monitoring & Auditing

### What to Track

1. **Deployments**
   - Who has the application
   - Which version
   - Installation date
   - Last used date

2. **Usage**
   - Number of calls made (aggregate)
   - Errors encountered
   - Performance metrics

3. **Security Events**
   - Failed config loads
   - Unauthorized access attempts
   - Unusual patterns

### Audit Log Template

```
Date: 2026-01-15
User: john.doe@hospital.com
Version: 1.0.0
Action: Installed
Notes: Initial rollout, training completed

Date: 2026-01-20
User: john.doe@hospital.com
Action: Used
Records Processed: 25
Calls Made: 25
Results Exported: Yes
Notes: Normal operation

Date: 2026-02-01
User: john.doe@hospital.com
Version: 1.1.0
Action: Updated
Notes: Security patch applied
```

---

## 🆘 Support Plan

### Tier 1: User Issues
- Can't find config.env
- Browser doesn't open
- File upload issues
- **Response:** Email/phone support, FAQ

### Tier 2: Technical Issues
- Application crashes
- API errors
- Performance problems
- **Response:** Remote support, log analysis

### Tier 3: Security Issues
- Credential compromise
- Unauthorized access
- Data breach
- **Response:** Incident response team, escalation

### Support Contact Info

Create a support document:
```
AI RESCHEDULING AGENT SUPPORT
============================

TIER 1 - General Questions
Email: support@yourcompany.com
Phone: 1-800-XXX-XXXX
Hours: 8am-5pm ET, Mon-Fri

TIER 2 - Technical Issues
Email: techsupport@yourcompany.com
Phone: 1-800-XXX-XXXX ext 2
Hours: 24/7

TIER 3 - Security Incidents
Email: security@yourcompany.com
Phone: 1-800-XXX-XXXX ext 9
Hours: 24/7

When contacting support, have ready:
- Version number
- Error message (screenshot)
- Steps to reproduce
- Your operating system
```

---

## ✅ Pre-Launch Checklist

**Development Complete:**
- [ ] All features working
- [ ] Code reviewed for security
- [ ] No hardcoded credentials
- [ ] Localhost binding verified
- [ ] No telemetry code

**Documentation Complete:**
- [ ] HIPAA_COMPLIANCE.md
- [ ] User README.txt
- [ ] IT deployment guide
- [ ] Training materials

**Testing Complete:**
- [ ] Built on all platforms
- [ ] Tested with sample data
- [ ] Network isolation verified
- [ ] Performance acceptable
- [ ] Antivirus compatibility checked

**Compliance Complete:**
- [ ] Risk assessment done
- [ ] BAA signed with Retell AI
- [ ] Security officer approved
- [ ] Privacy officer approved
- [ ] Legal reviewed

**Deployment Ready:**
- [ ] Distribution package created
- [ ] Support plan in place
- [ ] Training scheduled
- [ ] Rollback plan defined

---

## 📞 Questions?

For questions about this deployment guide:

**Technical:** techsupport@yourcompany.com  
**Security:** security@yourcompany.com  
**Compliance:** compliance@yourcompany.com

---

*Last Updated: 2026-01-08*  
*Version: 1.0*