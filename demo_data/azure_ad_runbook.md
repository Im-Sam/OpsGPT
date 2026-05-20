# Azure Active Directory Operations Runbook
## Version 3.2 | IT Operations Team | Last Updated: 2024-01

---

## 1. User Account Management

### 1.1 Creating a New User Account

**Required permissions**: Global Administrator or User Administrator role.

**Steps:**
1. Sign in to the Azure portal at https://portal.azure.com
2. Navigate to **Azure Active Directory > Users > New user**
3. Select **Create user**
4. Fill in the required fields:
   - **User name**: firstname.lastname@company.com
   - **Name**: Full display name
   - **Password**: Select "Auto-generate password" for first login
5. Under **Properties**, assign **Department**, **Job title**, and **Manager**
6. Under **Assignments**, add the user to the appropriate **groups** based on department
7. Click **Create**
8. Send the temporary password to the user's personal email via ServiceNow ticket
9. Notify the user's manager via email that the account is active

**Post-creation checklist:**
- [ ] Add to department security group
- [ ] Assign M365 license (E3 or E5 depending on role)
- [ ] Verify MFA is enforced via Conditional Access
- [ ] Add to relevant Teams channels

---

### 1.2 Resetting a User's Password

**Who can do this**: Help Desk (tier 1), SysAdmin, or Global Admin.

**Standard reset (user-initiated):**
1. Direct user to https://aka.ms/sspr (Self-Service Password Reset portal)
2. User enters their UPN and completes MFA verification
3. User sets a new password meeting complexity requirements

**Admin-initiated reset:**
1. Navigate to **Azure AD > Users** and search for the user
2. Click the user's display name to open their profile
3. Click **Reset password** in the top action bar
4. Select **Auto-generate password** or enter a temporary password
5. Check **Require this user to change their password when they first sign in**
6. Click **Reset password** and copy the temporary password
7. Deliver the password to the user through a verified channel (phone call or in-person)

**Password requirements:**
- Minimum 12 characters
- At least one uppercase, one lowercase, one number, one special character
- Cannot match the last 10 passwords
- Cannot contain the user's display name or UPN

---

### 1.3 Resetting Multi-Factor Authentication (MFA)

**When to use:** User has lost their authenticator app, changed phones, or is locked out.

**Tier 1 process (Help Desk):**
1. Verify user identity via video call or by answering 3 security questions from HR record
2. Navigate to **Azure AD > Users > [Username]**
3. Under the **Authentication methods** tab, click **Require re-register MFA**
4. Inform the user they will be prompted to register a new authenticator on next login
5. Log the action in ServiceNow with ticket number and verification method used

**Tier 2 process (SysAdmin — full MFA wipe):**
1. Navigate to **Azure AD > Users > [Username] > Authentication methods**
2. Delete all existing methods (phone number, authenticator app, FIDO2 key)
3. Under **My Staff** or **Authentication methods** blade, confirm removal
4. In **Azure AD > Security > MFA > Block/unblock users**, ensure the account is not blocked
5. Instruct user to sign in — they will be forced through MFA registration
6. Follow up after 24 hours to confirm successful re-enrollment

**Escalate to Global Admin if:**
- User is a Privileged Identity Management (PIM) role holder
- Account shows sign-in activity from unexpected geography post-reset
- User reports they did not initiate the reset request (potential account compromise)

---

### 1.4 Disabling and Offboarding a User

**Trigger:** HR submits an offboarding request via ServiceNow with departure date.

**Day of departure — within 1 hour of termination:**
1. **Disable account**: Azure AD > Users > [User] > Toggle **Account enabled** to OFF
2. **Revoke sessions**: Click **Revoke sessions** to invalidate all active tokens
3. **Remove group memberships**: Assignments tab > Remove from all security and M365 groups
4. **Forward email**: Exchange admin center > Mailboxes > Set forwarding to manager for 30 days
5. **Transfer OneDrive**: Assign OneDrive data access to manager (SharePoint admin center)
6. **Remove MFA methods**: Authentication methods tab > delete all
7. **Remove licenses**: Remove M365 license to free the seat
8. **Document in ServiceNow**: Record completion time and ticket number

**30 days post-departure:**
- Hard delete the Azure AD account
- Remove email forwarding
- Archive mailbox to compliance storage per retention policy

---

## 2. Conditional Access Policies

### 2.1 Current Active Policies

| Policy Name | State | Applies To | Conditions | Grant |
|---|---|---|---|---|
| Require MFA for All Users | On | All users | Any location | MFA |
| Block Legacy Authentication | On | All users | Legacy auth clients | Block |
| Require Compliant Device | On | All users | Corporate apps | Compliant device OR MFA |
| Admin Role MFA | On | Global/Privileged Admins | Any | MFA + Compliant device |
| Guest User Restrictions | On | External guests | Any | MFA, terms of use |
| BYOD Policy | On | All users | Non-corporate device | MFA + App protection |

### 2.2 Creating a New Conditional Access Policy

1. Navigate to **Azure AD > Security > Conditional Access > New policy**
2. Name the policy clearly: `[Scope] - [Requirement] - [Date]` (e.g., `Finance - Block USB - 2024-01`)
3. Set **Users and groups** (use groups, never individual users)
4. Set **Cloud apps** — be specific; "All cloud apps" can cause lockout if misconfigured
5. Set **Conditions** (location, device platform, sign-in risk)
6. Set **Grant** controls (MFA, compliant device, approved app)
7. Set policy to **Report-only mode first** — monitor for 7 days in Sign-in logs
8. Review impact in **Azure AD > Sign-in logs > Report-only** tab
9. Switch to **On** during a maintenance window
10. Document the policy in the IT policy register

**WARNING:** Never set "Block" policies without testing in Report-only first. A misconfigured Block policy can lock out all users including admins.

---

## 3. Privileged Identity Management (PIM)

### 3.1 Activating a Privileged Role

1. Navigate to https://portal.azure.com > **Azure AD Privileged Identity Management**
2. Click **My roles > Azure AD roles**
3. Find the eligible role (e.g., Global Administrator, Exchange Administrator)
4. Click **Activate**
5. Set activation duration (max 8 hours per policy)
6. Enter a **justification** — be specific (ticket number, task description)
7. Complete MFA challenge
8. Role is now active — begins after approval (if approval required)

**Roles requiring approval:**
- Global Administrator — requires 2 approvers from IT leadership
- Security Administrator — requires 1 approver from Security team
- User Administrator — self-service, no approval required

### 3.2 PIM Access Review Schedule

Access reviews run every 90 days. Managers receive email notifications to review their reports' privileged role assignments. Roles not reviewed within 14 days of review period end are automatically removed.

---

## 4. Sign-in Logs and Audit Logs

### 4.1 Investigating a Suspicious Sign-in

**When triggered by:** Security alert, user report, automated SIEM alert.

1. Navigate to **Azure AD > Sign-in logs**
2. Filter by: **User** (UPN), **Status** (failure/success), **Date** (last 24–72 hours)
3. Look for:
   - Sign-ins from unexpected **IP addresses** or **countries**
   - Rapid sign-in attempts from multiple locations (impossible travel)
   - Legacy protocol usage (BasicAuth, IMAP, POP3)
   - Sign-ins outside business hours
4. Export logs to CSV for further analysis
5. If confirmed suspicious: immediately disable account, revoke sessions, notify Security team
6. Open a P1 incident in ServiceNow and notify the CISO

### 4.2 Audit Log Retention

Azure AD sign-in logs are retained for **30 days** (Azure AD P1) or **90 days** (Azure AD P2). For longer retention, configure **Diagnostic Settings** to export to:
- **Log Analytics Workspace** (recommended — query with KQL)
- **Azure Storage Account** (cold archive)
- **Event Hub** → SIEM (Splunk, Sentinel)
