# VMware vSphere Infrastructure Runbook
## IT Operations | Version 3.1 | Virtualization & Compute Management

---

## 1. vSphere Environment Overview

### 1.1 Infrastructure Inventory

**vCenter Server:** vcenter.company.local (10.0.1.20)
**vCenter Version:** VMware vCenter Server 8.0 Update 2
**SSO Domain:** vsphere.local

**ESXi Host Cluster — Production:**
| Host | IP | CPU | RAM | Version | Status |
|---|---|---|---|---|---|
| esxi-prod-01 | 10.0.10.11 | 2x Intel Xeon Gold 6348 (56 cores) | 512GB | ESXi 8.0 U2 | Active |
| esxi-prod-02 | 10.0.10.12 | 2x Intel Xeon Gold 6348 (56 cores) | 512GB | ESXi 8.0 U2 | Active |
| esxi-prod-03 | 10.0.10.13 | 2x Intel Xeon Gold 6348 (56 cores) | 512GB | ESXi 8.0 U2 | Active |
| esxi-prod-04 | 10.0.10.14 | 2x Intel Xeon Gold 6348 (56 cores) | 256GB | ESXi 8.0 U2 | Active |

**ESXi Host Cluster — Dev/Test:**
| Host | IP | CPU | RAM | Version |
|---|---|---|---|---|
| esxi-dev-01 | 10.0.20.11 | 2x Intel Xeon Silver 4314 (32 cores) | 256GB | ESXi 8.0 U2 |
| esxi-dev-02 | 10.0.20.12 | 2x Intel Xeon Silver 4314 (32 cores) | 256GB | ESXi 8.0 U2 |

**Datastores:**
| Name | Type | Capacity | Free | Used By |
|---|---|---|---|---|
| prod-ssd-01 | VMFS6 / Pure Storage | 50TB | 18TB | Production VMs |
| prod-ssd-02 | VMFS6 / Pure Storage | 50TB | 22TB | Production VMs |
| dev-datastore-01 | VMFS6 / Local SSD | 10TB | 4TB | Dev/Test VMs |
| backup-nfs-01 | NFS 3 / Synology | 100TB | 67TB | VM Backups (Veeam) |

---

## 2. Virtual Machine Operations

### 2.1 Creating a New Virtual Machine

**Standard VM templates (stored in Content Library):**
- `tmpl-windows-server-2022` — Windows Server 2022 Standard, 60GB thin disk, VMware Tools pre-installed
- `tmpl-ubuntu-22-lts` — Ubuntu 22.04 LTS, 40GB thin disk, open-vm-tools installed
- `tmpl-rhel-9` — RHEL 9, 40GB thin disk, subscription not yet attached

**Deploying from template:**
1. Log into vCenter: https://vcenter.company.local (use your AD credentials)
2. Right-click the target cluster > **New Virtual Machine > Deploy from template**
3. Select the appropriate template from the Content Library
4. Name the VM using the naming convention: `[env]-[function]-[number]` (e.g. `prod-webserver-04`, `dev-db-02`)
5. Select destination cluster and host (vSphere DRS will place automatically)
6. Select datastore: use `prod-ssd-01` or `prod-ssd-02` for production (round-robin)
7. Customize hardware: set vCPU, RAM, additional disks per the sizing guide below
8. Complete customization specification: set hostname, IP address, domain join
9. Click **Finish** — VM deploys in 2-5 minutes

**Standard VM sizing guide:**
| Workload Type | vCPU | RAM | OS Disk | Data Disk |
|---|---|---|---|---|
| Web/App server (light) | 2 | 4GB | 60GB | As needed |
| Web/App server (medium) | 4 | 8GB | 60GB | As needed |
| Database server (small) | 4 | 16GB | 60GB | 500GB+ |
| Database server (large) | 8 | 32GB | 60GB | 1TB+ |
| File server | 2 | 8GB | 60GB | 2TB+ |
| Domain controller | 2 | 8GB | 60GB | — |

**Post-deployment checklist:**
- [ ] Verify VMware Tools is running: VM > Summary > VMware Tools status
- [ ] Confirm IP address assigned and DNS record created
- [ ] Run Windows Update / apt upgrade before adding to production
- [ ] Register in CMDB (ServiceNow): Asset > New > Virtual Machine
- [ ] Apply backup policy in Veeam Backup & Replication
- [ ] Enable monitoring in SolarWinds NPM

### 2.2 Modifying VM Resources (Hot-Add)

**CPU hot-add:** Supported on all templates — can add vCPUs without rebooting (guest OS must support).

**Memory hot-add:** Supported on Windows Server 2016+, not supported on Linux by default.

**To add resources without downtime:**
1. Right-click VM > **Edit Settings**
2. Expand CPU or Memory section
3. Increase values — if hot-add is supported, changes apply immediately
4. If hot-add is not enabled on the VM: power off, make changes, power on
5. Update CMDB record with new resource allocation
6. Document reason for change in ServiceNow change ticket

**Important:** Never set vCPU count higher than the number of physical cores on the host. Over-provisioning causes CPU ready time and performance degradation. Alert threshold: CPU ready > 5% sustained.

### 2.3 VM Snapshots

**Policy:** Snapshots are for short-term use only (pre-change safety net). They are NOT backups.

**Maximum snapshot retention:** 72 hours. Snapshots older than 72 hours are automatically flagged by the SolarWinds alert.

**Taking a snapshot:**
1. Right-click VM > **Snapshots > Take Snapshot**
2. Name: `pre-[change description]-[date]` (e.g. `pre-sql-upgrade-2024-01-15`)
3. Description: Include ServiceNow change ticket number
4. Check **Quiesce guest file system** for consistent snapshots (requires VMware Tools)
5. Do NOT check **Snapshot the virtual machine's memory** unless needed (doubles snapshot size)

**Reverting a snapshot:**
1. Right-click VM > **Snapshots > Manage Snapshots**
2. Select the snapshot to revert to
3. Click **Revert to** — VM will reboot to that state
4. Confirm services are operational
5. Delete the snapshot once no longer needed

**Deleting snapshots:**
1. Right-click VM > **Snapshots > Manage Snapshots**
2. Select snapshot > **Delete** (consolidates delta disks back to base)
3. Monitor consolidation progress — large snapshots can take 30+ minutes
4. Do not snapshot VMs during consolidation

---

## 3. vSphere High Availability and DRS

### 3.1 vSphere High Availability (HA)

**Current HA configuration:**
- HA enabled on Production cluster
- Host monitoring: Enabled
- VM monitoring: VM and application monitoring
- Admission control: Reserve 25% cluster capacity for failover
- Heartbeat datastores: prod-ssd-01, prod-ssd-02

**What HA does:** If an ESXi host fails, all VMs on that host are automatically restarted on remaining hosts within 30-120 seconds. HA does not prevent downtime — it minimizes it.

**HA restart priority:**
- **Highest:** Domain controllers, vCenter, core infrastructure VMs
- **High:** Production database servers, application servers
- **Medium:** Web servers, file servers
- **Low:** Dev/test VMs, monitoring VMs

### 3.2 vSphere DRS (Distributed Resource Scheduler)

**DRS mode:** Fully Automated — VMs automatically migrated via vMotion to balance load.

**DRS threshold:** Aggressive (level 5) — migrates frequently to maintain balance.

**vMotion requirements:**
- Shared storage between hosts (Pure Storage SAN)
- VMware vMotion network on dedicated 10GbE vMotion port group
- Compatible CPU families (all production hosts use same Intel Xeon generation)

**Manual vMotion (migrating a VM to a specific host):**
1. Right-click VM > **Migrate**
2. Select **Change compute resource only**
3. Select destination host
4. Select vMotion network
5. Click **Finish** — migration runs live with zero downtime

---

## 4. ESXi Host Maintenance

### 4.1 Placing a Host in Maintenance Mode

Required for: Hardware maintenance, ESXi patching, host replacement.

1. Ensure cluster has sufficient capacity to absorb VMs from this host
2. Right-click host in vCenter > **Maintenance Mode > Enter Maintenance Mode**
3. Select **Move powered-off and suspended VMs to other hosts in the cluster**
4. DRS will automatically vMotion all running VMs to other hosts (takes 5-30 min)
5. Confirm host shows "Maintenance Mode" status before proceeding with physical work
6. After maintenance: Right-click host > **Exit Maintenance Mode**
7. DRS will rebalance VMs back to the host automatically

**Do NOT place more than one host in maintenance mode simultaneously unless cluster capacity allows.**

### 4.2 ESXi Patching with vSphere Lifecycle Manager

**Patch schedule:** ESXi hosts patched on the third Sunday of each month during the 02:00-06:00 EST maintenance window.

**Patching process:**
1. vCenter > Menu > Lifecycle Manager
2. Select the cluster > **Updates** tab
3. Check for available patches: **Check compliance**
4. Review patches — critical security patches applied immediately; feature updates tested in dev first
5. Stage patches to hosts (downloads without applying): **Stage only**
6. During maintenance window: Remediate one host at a time
7. Host automatically enters maintenance mode, patches, reboots, exits maintenance mode
8. Verify host is healthy before remediating next host

---

## 5. Backup and Recovery

### 5.1 Veeam Backup & Replication

**Veeam Server:** veeam.company.local (10.0.1.25)
**Backup Repository:** backup-nfs-01 (100TB NFS on Synology NAS)
**Offsite Repository:** AWS S3 bucket via Veeam Cloud Connect (encrypted)

**Backup jobs and schedules:**
| Job Name | VMs Included | Schedule | Retention | Repository |
|---|---|---|---|---|
| prod-critical-daily | DCs, vCenter, DB servers | Daily 22:00 | 30 days | Local + S3 |
| prod-standard-daily | All other prod VMs | Daily 23:30 | 14 days | Local + S3 |
| dev-weekly | All dev/test VMs | Sunday 01:00 | 4 weeks | Local only |

**Backup SLAs:**
- Critical VMs: RPO 24 hours, RTO 4 hours
- Standard prod VMs: RPO 24 hours, RTO 8 hours
- Dev/test VMs: RPO 7 days, RTO 24 hours

### 5.2 Restoring a Virtual Machine

**Full VM restore:**
1. Open Veeam Backup & Replication console
2. Navigate to **Home > Backups > Disk**
3. Expand the backup job, find the VM, right-click > **Restore entire VM**
4. Select restore point (date/time)
5. Select restore mode: **Restore to original location** (overwrites existing) or **Restore to a new location**
6. Power on VM after restore: check the option or power on manually
7. Verify services are running post-restore
8. Document restore in ServiceNow incident/change ticket

**File-level restore (single files from a VM backup):**
1. Right-click VM backup > **Restore guest files > Microsoft Windows**
2. Browse the backup as if it were a live file system
3. Select files/folders > **Restore** or **Copy to** a local path
4. No VM downtime required for file-level restores

### 5.3 Backup Monitoring and Alerts

Veeam sends daily backup reports to: it-alerts@company.com

**If a backup job fails:**
1. Open Veeam console > **Home > Last 24 hours** — identify failed job
2. Click the failed job > **Statistics** tab > review error message
3. Common causes and fixes:
   - **Snapshot consolidation failed:** Manually consolidate VM snapshots in vCenter first
   - **Repository out of space:** Run backup maintenance to delete expired restore points
   - **Network timeout:** Check connectivity between Veeam server and ESXi hosts
   - **VM not responding:** Check if VM is powered on and VMware Tools is running
4. Retry the job manually after fixing the root cause
5. If backup has failed for 2+ consecutive days: escalate to P2 incident