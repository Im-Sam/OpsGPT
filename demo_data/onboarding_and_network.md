# New Employee IT Onboarding Checklist
## IT Operations | HR & IT Collaboration Document

---

## Pre-Arrival (IT Actions — 3 Business Days Before Start Date)

Triggered by: HR submits onboarding request in ServiceNow with employee start date, role, department, and manager.

### Account Provisioning
- [ ] Create Azure AD account: firstname.lastname@company.com
- [ ] Set department, job title, manager, office location attributes
- [ ] Assign M365 license (E3 for standard roles / E5 for IT/Security/Executive)
- [ ] Add to department security group (drives SharePoint, Teams, and app access)
- [ ] Create shared mailbox if role requires (e.g., support@, billing@)
- [ ] Add to relevant Teams channels (coordinate with manager for list)
- [ ] Provision VPN access if remote role (add to VPN-StandardAccess group)
- [ ] Set up MFA — employee registers on Day 1

### Hardware Provisioning
- [ ] Prepare laptop from imaging station — apply latest OS image
- [ ] Join laptop to Azure AD (Intune enrollment auto-triggers via Autopilot)
- [ ] Verify Defender for Endpoint agent enrolled and reporting
- [ ] Verify Intune compliance policy applied (encryption, PIN, OS version)
- [ ] Install department-standard software via Intune application deployment:
  - Microsoft 365 Apps (Word, Excel, Teams, Outlook)
  - GlobalProtect VPN client
  - Zoom / Webex (per department standard)
  - Department-specific tools (coordinate with manager)
- [ ] Label laptop with asset tag and record in asset management system (Snipe-IT)
- [ ] Prepare accessories: power adapter, monitor cable, mouse/keyboard (if office role)

### Day 1 Prep
- [ ] Prepare IT welcome email with: temp password, MFA setup instructions, help desk contact
- [ ] Book 30-minute IT orientation session for Day 1 morning
- [ ] Confirm desk/workstation setup with facilities (if office role)
- [ ] Create ServiceNow onboarding ticket and assign to L2 for oversight

---

## Day 1 — IT Orientation Session (30 minutes with new employee)

### Account Setup (with employee present)
1. Hand over laptop and temp password
2. Guide employee through first login:
   - Change temporary password
   - Set up Microsoft Authenticator MFA (scan QR code)
   - Verify Outlook opens and email is working
   - Verify Teams access and department channels are visible
3. Show employee: https://aka.ms/sspr — self-service password reset registration
4. Walk through: VPN connection (if remote) — GlobalProtect setup
5. Show IT Help Desk portal: https://helpdesk.company.com
6. Share IT quick reference card (printed or digital)

### Access Verification Checklist (confirm with employee)
- [ ] Can log into https://myapps.microsoft.com (SSO portal)
- [ ] Email accessible in Outlook
- [ ] Teams messages sending and receiving
- [ ] Can access department SharePoint site
- [ ] VPN connects successfully (if applicable)
- [ ] Can access primary role-specific application (check with manager)

### What to Tell the New Employee
- **Password policy**: Minimum 12 characters, changes required every 90 days (prompted automatically)
- **MFA**: Required every time on a new device or after 14 days on trusted devices
- **Phishing**: Never click links in unexpected emails — forward suspicious emails to phishing@company.com
- **Help Desk**: https://helpdesk.company.com or ext. 4357 (HELP) — available Mon–Fri 7am–6pm
- **Acceptable use**: Personal use on corporate devices is limited — full policy at https://intranet.company.com/it-policy

---

## Week 1 — Follow-Up Actions

### IT Actions
- [ ] Verify Intune shows device as compliant after 24 hours
- [ ] Check Defender for Endpoint enrollment is active and no alerts triggered
- [ ] Follow up with employee on any access issues
- [ ] Ensure BitLocker encryption key is escrowed to Azure AD (check in Intune)

### Access Reviews
- [ ] Manager confirms all required application access is working by end of week 1
- [ ] Any additional access requests submitted via ServiceNow with manager approval
- [ ] Privileged access requests (admin rights, VPN privileged) escalated to IT Director

---

# Network Troubleshooting Guide
## IT Operations | Tier 1 & Tier 2 Reference

---

## 1. Systematic Troubleshooting Approach (OSI Model — Bottom Up)

Always troubleshoot from Layer 1 upward. Don't jump to advanced steps before confirming basics.

### Layer 1 — Physical
- Is the ethernet cable plugged in firmly on both ends?
- Is the port LED on the switch lit? (green = active, amber = error, no light = no link)
- Try a different cable and a different switch port
- For wireless: is the WiFi adapter enabled? (check Device Manager / Network settings)

### Layer 2 — Data Link
- Run: `ipconfig /all` — does the NIC show a valid MAC address?
- Is DHCP providing an IP? (Should be 10.x.x.x range, not 169.254.x.x)
- If 169.254.x.x: DHCP server not responding — check DHCP server or switch trunk
- Clear ARP cache: `arp -d *` (Windows) or `ip -s -s neigh flush all` (Linux)

### Layer 3 — Network
- Can you ping the default gateway? `ping 10.0.0.1`
- Can you ping an internal server? `ping fileserver01.company.local`
- Can you ping external? `ping 8.8.8.8`
- Run traceroute to identify where the path breaks: `tracert 8.8.8.8`

### Layer 4–7 — Application
- Can you resolve DNS? `nslookup google.com` — should return 8.8.8.8 or similar
- If DNS fails: `ipconfig /flushdns` then retry
- If ping works but browser fails: proxy settings issue — check IE/Chrome proxy settings
- Is the specific port open? `Test-NetConnection -ComputerName fileserver01 -Port 445`

---

## 2. Common Network Issues and Fixes

### "No Internet Access" — DHCP Not Assigning IP

**Symptom:** ipconfig shows 169.254.x.x (APIPA address)

1. `ipconfig /release` then `ipconfig /renew`
2. If still APIPA: verify DHCP server is online (ping 10.0.1.10 — DHCP server IP)
3. Check switch port VLAN assignment (should be VLAN 10 for corporate endpoints)
4. If one machine only: static IP conflict — check if someone manually set an IP
5. If multiple machines: DHCP scope exhausted or DHCP server down — escalate to P2

### "Cannot Access File Shares" (SMB / CIFS)

**Symptom:** `\\fileserver01\shared` not accessible

1. Verify VPN is connected (if remote) — file shares are LAN-only
2. Test connectivity: `Test-NetConnection -ComputerName fileserver01 -Port 445`
3. Verify DNS resolves: `nslookup fileserver01.company.local`
4. Check user has permission to the share (not an IT issue — escalate to share owner/manager)
5. Try mapping by IP: `\\10.0.2.50\shared` — if this works, DNS is the problem
6. Clear credentials: Credential Manager > Windows Credentials > remove fileserver01 entries

### "WiFi Keeps Disconnecting"

1. Check if issue is building-wide (multiple users) or single device
2. If single device: update WiFi driver, disable power management on adapter
3. Check signal strength — if below -75 dBm, user needs closer to AP or wired connection
4. Review WLAN controller for AP error logs (Cisco WLC / Meraki dashboard)
5. If DHCP lease expiry causing drop: shorten lease time or configure IP reservation

### "Slow Network / High Latency"

1. Run internal speed test: https://speed.company.com
2. Run external speed test: https://fast.com — compare
3. If internal slow, external fast: internal bottleneck — check switch bandwidth utilization
4. Run: `pathping 10.0.0.1` — identifies packet loss at each hop
5. Check for broadcast storms: high CPU on core switch, all ports showing high utilization
6. Identify top talkers via NetFlow/IPFIX on core router — escalate to Network team

---

## 3. DNS Troubleshooting

### Internal DNS Servers
- Primary DNS: 10.0.1.5 (DC01)
- Secondary DNS: 10.0.1.6 (DC02)
- All workstations should use these — NOT 8.8.8.8 (that breaks internal name resolution)

### Common DNS Commands
```powershell
# Test resolution
nslookup fileserver01.company.local

# Force query a specific DNS server
nslookup fileserver01.company.local 10.0.1.5

# Flush DNS cache
ipconfig /flushdns

# Show current DNS settings
Get-DnsClientServerAddress

# Test if DNS port is reachable
Test-NetConnection -ComputerName 10.0.1.5 -Port 53
```

### If Internal DNS Fails
1. Is DC01 / DC02 online? (ping 10.0.1.5 and 10.0.1.6)
2. Check DNS service on DC: `Get-Service DNS` on the domain controller
3. Review DNS event logs: Event Viewer > Applications and Services > DNS Server
4. Temporary workaround: manually set DNS to 10.0.1.6 (secondary) on affected machine

---

## 4. Firewall and Proxy Issues

### If a Specific Website is Blocked
1. Check Palo Alto URL filtering category — the site may be in a blocked category
2. Request exception via ServiceNow: Access Request > URL Exception
3. Provide business justification — approved by manager
4. IT will add URL to appropriate allow list category in Palo Alto within 1 business day

### If an Application Cannot Connect
1. Identify the destination IP and port the app needs (check vendor documentation)
2. Test connectivity: `Test-NetConnection -ComputerName [destination] -Port [port]`
3. If blocked: submit firewall rule request in ServiceNow with source, destination, port, protocol
4. Firewall rules reviewed weekly — emergency rules can be added within 4 hours with IT Director approval

### Proxy Settings (for applications that need explicit proxy)
- Proxy address: proxy.company.com
- Proxy port: 8080
- Bypass list: *.company.com, 10.0.0.0/8, localhost
- Authentication: use corporate credentials (SSO)
