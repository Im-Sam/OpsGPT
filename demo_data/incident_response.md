# IT Incident Response Runbook
## Priority Classification, Escalation Paths & Response Procedures
## IT Operations & Security Team | Version 4.0

---

## 1. Incident Priority Definitions

### P1 — Critical (Response: 15 minutes | Resolution Target: 4 hours)

**Definition:** Complete service outage affecting all users, a security breach in progress, or data loss risk.

**Examples:**
- Corporate network or internet connectivity fully down
- Active ransomware or malware outbreak detected
- Azure AD / SSO down (all authentication failing)
- Production database unavailable
- Email system (Exchange/M365) fully down for all users
- Data center power failure
- Confirmed unauthorized access to privileged accounts

**Immediate actions (first 15 minutes):**
1. Page the On-Call SysAdmin immediately via PagerDuty
2. Open a P1 War Room in Microsoft Teams: #incident-p1-[date]
3. Notify IT Director and CISO via phone (not just email)
4. Assess blast radius: how many users/systems affected?
5. Begin incident log in ServiceNow — document every action with timestamps

### P2 — High (Response: 1 hour | Resolution Target: 8 hours)

**Definition:** Major service degradation affecting a significant subset of users or a critical business process.

**Examples:**
- VPN connection issues affecting 25%+ of remote users
- Specific application down (ERP, HRIS, ticketing system)
- Email delivery delays exceeding 30 minutes
- File server inaccessible for a department
- Suspected phishing campaign targeting employees (not yet compromised)
- Single server failure with no automatic failover

### P3 — Medium (Response: 4 hours | Resolution Target: 24 hours)

**Definition:** Service impaired but workaround available, or issue affecting a single user with business-critical needs.

**Examples:**
- Individual printer/peripheral failure
- Software not installing on a specific machine
- MFA issues for a single user
- Slow application performance not affecting all users
- Password reset for an executive or high-priority role

### P4 — Low (Response: 1 business day | Resolution Target: 5 business days)

**Definition:** Minor issue with no business impact, or enhancement request.

**Examples:**
- New user setup request (non-urgent)
- Peripheral device replacement
- Software license request
- General how-to questions

---

## 2. Escalation Paths

### 2.1 Network / Connectivity Incidents

```
Tier 1 Help Desk
    │ No resolution in 30 min (P1) / 2 hrs (P2)
    ▼
Tier 2 SysAdmin / Network Team
    │ Requires hardware intervention or ISP contact
    ▼
Network Engineer / ISP Escalation
    │ Infrastructure failure confirmed
    ▼
IT Director + Vendor TAC (Cisco/Palo Alto/ISP)
```

**Key contacts:**
- ISP (Primary): Comcast Business NOC — 1-800-XXX-XXXX | Account: COMP-XXXXX
- ISP (Backup): AT&T Business — 1-800-XXX-XXXX
- Cisco TAC: 1-800-553-2447 | Contract: CON-XXXXXXX
- Palo Alto NGFW Support: https://support.paloaltonetworks.com | Serial: XXXXXXXXXXXX

### 2.2 Security Incidents (Breach / Malware / Unauthorized Access)

```
Any Staff Member (Reports suspicious activity)
    │ Immediately
    ▼
Help Desk — Creates P1 ticket, notifies Security team
    │ Immediately
    ▼
Security Analyst — Investigates, contains threat
    │ If confirmed breach or data exposure
    ▼
CISO + Legal Counsel — Breach response, regulatory notification
    │ If PII or regulated data involved
    ▼
External IR Firm (CrowdStrike / Mandiant) + Law Enforcement (FBI Cyber if needed)
```

**Do NOT:**
- Power off infected machines before imaging (destroys forensic evidence)
- Communicate breach details over potentially compromised email
- Attempt to "clean" malware yourself — isolate and escalate

### 2.3 Cloud / Azure Incidents

```
Help Desk or SysAdmin detects Azure service issue
    │
    ▼
Check Azure Service Health dashboard: https://status.azure.com
    │ If Microsoft-side issue confirmed
    ▼
Open Azure Support ticket (Severity A for P1, B for P2)
Monitor: @AzureSupport on Twitter for real-time updates
    │ If Microsoft ETA > 2 hours and business critical
    ▼
Activate DR / failover procedures per system-specific runbook
    │
    ▼
IT Director decision: Invoke Business Continuity Plan
```

---

## 3. Incident Response Procedures

### 3.1 Network Outage Response

**Step 1 — Identify scope (0–5 min)**
1. Are all offices affected or a single site?
2. Is internet down or only internal connectivity?
3. Run: `ping 8.8.8.8` (internet test) and `ping 10.0.0.1` (internal gateway test)
4. Check core switch/firewall for interface status alerts

**Step 2 — Quick isolations (5–15 min)**
1. Check physical cabling on core switch if single site
2. Log into Palo Alto firewall: check interface status, BGP peer status
3. Log into ISP router: verify WAN IP is assigned, check BGP session
4. Run `traceroute 8.8.8.8` — identify where the path breaks

**Step 3 — Failover (if available)**
1. If primary ISP down: Activate backup ISP link in router configuration
2. Update BGP preference to route through backup
3. Verify failover by pinging external IPs and checking user connectivity
4. Document failover time in incident log

**Step 4 — Communication**
1. Update status page: https://status.company.com (internal admin)
2. Send user notification via M365 Admin Center (if email is up) or Teams message
3. Update IT Director every 30 minutes until resolved

### 3.2 Ransomware / Malware Incident

**CONTAINMENT IS THE PRIORITY — DO NOT ATTEMPT REMOVAL FIRST**

**Immediate containment (0–10 min):**
1. **Isolate infected machine(s)**: Physically disconnect ethernet, disable WiFi adapter
2. Do NOT shut down — memory may contain encryption keys (forensic value)
3. Identify patient zero: who reported first? What did they click/open?
4. Check for lateral movement: are other machines showing similar behavior?
5. Disable the affected user's Azure AD account and revoke sessions

**Escalation (10–20 min):**
1. Notify CISO and IT Director by phone immediately
2. Do NOT send breach details over email (may be monitored by attacker)
3. Convene War Room in Teams on a clean device
4. Preserve all evidence: screenshots of ransomware note, affected file paths, event logs

**Assessment (20–60 min):**
1. Determine if data was exfiltrated (check firewall egress logs for unusual large transfers)
2. Identify the ransomware variant using ID Ransomware: https://id-ransomware.malwarehunterteam.com
3. Check backup integrity: are cloud backups accessible and unaffected?
4. Determine if paying ransom is even being considered (legal decision — CISO + Legal)

**Recovery:**
1. Wipe and reimage affected machines — do not attempt to disinfect
2. Restore from last known-good backup
3. Force password reset for all affected users and any accounts that touched infected systems
4. Deploy EDR telemetry review for 30 days post-incident

### 3.3 Phishing Incident Response

**If a user clicked a phishing link or entered credentials:**
1. Immediately disable the user's Azure AD account
2. Revoke all active sessions (Azure AD > User > Revoke sessions)
3. Reset password and MFA
4. Review Azure AD sign-in logs for any access in the past 24 hours from the account
5. Check mail rules (auto-forwards to external addresses are a key indicator)
6. Search Exchange for the phishing email subject line — quarantine for all recipients
7. Report the phishing domain to your DNS/email security vendor for blocking
8. File a report at: https://www.ic3.gov (FBI Internet Crime Complaint Center)

---

## 4. Post-Incident

### 4.1 Post-Incident Review (PIR)

Required for all P1 incidents and major P2 incidents. Scheduled within 5 business days of resolution.

**PIR Template:**
- **Incident Summary**: What happened, when, impact
- **Timeline**: Minute-by-minute from detection to resolution
- **Root Cause**: Technical root cause (not "human error" — what process failed?)
- **Response Evaluation**: What went well, what was slow or unclear
- **Action Items**: Specific tasks, owners, and due dates
- **Metrics**: MTTD (Mean Time to Detect), MTTR (Mean Time to Resolve)

### 4.2 Communication Templates

**Initial P1 user notification:**
> "We are currently experiencing [brief description]. Our team is actively investigating. We will provide updates every 30 minutes. Workaround: [if available]. Thank you for your patience."

**Resolution notification:**
> "The [service] issue has been resolved as of [time]. Root cause: [one sentence]. All services are now fully operational. If you experience any lingering issues, please contact the Help Desk."
